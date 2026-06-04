"""Control: end-to-end orchestration of a single inquiry.

Depends only on the Entity models and the Boundary *Protocols* — never on
concrete adapters. Concrete implementations are injected by :mod:`stargo.app`,
which keeps this business logic unit-testable with fakes.

Flow: browser extraction -> knowledge retrieval -> AI draft -> deterministic
risk control -> optional auto-send -> WeChat notify -> CRM log.
"""

from __future__ import annotations

import logging

from ..boundary.interfaces import (
    BrowserDriver,
    CRMSink,
    KnowledgeBase,
    Notifier,
    ReplyDrafter,
)
from ..entity.models import AIReply, ChatContext, InquiryRecord
from .risk_controller import RiskChecker

logger = logging.getLogger(__name__)


class InquiryPipeline:
    def __init__(
        self,
        *,
        knowledge: KnowledgeBase,
        drafter: ReplyDrafter,
        risk_checker: RiskChecker,
        notifier: Notifier,
        crm: CRMSink,
        max_context_chars: int = 6000,
    ) -> None:
        self.knowledge = knowledge
        self.drafter = drafter
        self.risk_checker = risk_checker
        self.notifier = notifier
        self.crm = crm
        self.max_context_chars = max_context_chars

    def _draft(self, ctx: ChatContext) -> AIReply:
        query = " ".join(filter(None, [ctx.product_title, ctx.latest_message]))
        knowledge = self.knowledge.context_snippets(query, self.max_context_chars)
        reply = self.drafter.generate(ctx, knowledge)
        # Policy has the final say over routing.
        return self.risk_checker.apply(ctx, reply)

    def _log(self, ctx: ChatContext, reply: AIReply, status: str) -> None:
        record = InquiryRecord(
            buyer_name=ctx.buyer_name,
            country=ctx.country,
            product_title=ctx.product_title,
            product_url=ctx.product_url,
            buyer_message=ctx.latest_message,
            ai_intent=reply.intent,
            customer_level=reply.customer_level,
            ai_reply_en=reply.reply_en,
            auto_send=reply.auto_send,
            approval_required=reply.human_approval_required,
            status=status,
            screenshot_path=ctx.screenshot_path,
        )
        try:
            self.crm.log(record)
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("CRM logging failed: %s", exc)

    def process(self, browser: BrowserDriver, url: str) -> ChatContext:
        """Process one inquiry using an already-started browser driver."""
        logger.info("Processing inquiry: %s", url)
        ctx = browser.open_inquiry(url)

        if not ctx.ok:
            detail = []
            if ctx.needs_login:
                detail.append("阿里登录已失效，请在浏览器重新登录。")
            if ctx.needs_captcha:
                detail.append("出现验证码/安全验证，需要人工处理。")
            if ctx.extraction_failed:
                detail.append("无法读取对话内容（页面结构可能变化）。")
            self.notifier.notify_alert(
                "【STARGO 需人工处理】无法读取阿里对话",
                "\n".join(detail) or "未知问题",
                url=url,
            )
            self._log(ctx, AIReply(reason="blocked"), status="needs_login")
            return ctx

        reply = self._draft(ctx)

        status = "awaiting_approval"
        if reply.auto_send and not reply.human_approval_required:
            _, sent = browser.open_and_reply(url, reply.reply_en)
            status = "auto_sent" if sent else "failed"
            if not sent:
                logger.warning("Auto-send failed; routing to manual approval.")

        self.notifier.notify_inquiry(ctx, reply, url=url)
        self._log(ctx, reply, status=status)
        return ctx
