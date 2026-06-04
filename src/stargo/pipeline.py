"""End-to-end orchestration of a single inquiry.

Wires together: browser extraction -> knowledge retrieval -> AI draft ->
deterministic risk control -> optional auto-send -> WeChat notify -> CRM log.
"""

from __future__ import annotations

import logging

from .ai.reply_generator import ReplyGenerator
from .ai.risk_checker import RiskChecker
from .browser.alibaba_playwright import AlibabaBrowser
from .config import Config
from .crm.sqlite_logger import SqliteLogger
from .knowledge.retriever import Retriever
from .models import AIReply, ChatContext, InquiryRecord
from .notify.notifier import Notifier

logger = logging.getLogger(__name__)


class Pipeline:
    def __init__(
        self,
        config: Config,
        *,
        retriever: Retriever,
        generator: ReplyGenerator,
        risk_checker: RiskChecker,
        notifier: Notifier,
        crm: SqliteLogger,
    ) -> None:
        self.config = config
        self.retriever = retriever
        self.generator = generator
        self.risk_checker = risk_checker
        self.notifier = notifier
        self.crm = crm

    @classmethod
    def build(cls, config: Config) -> "Pipeline":
        return cls(
            config,
            retriever=Retriever.from_config(config.knowledge),
            generator=ReplyGenerator(config.ai),
            risk_checker=RiskChecker(config.reply_rules),
            notifier=Notifier(config.wechat),
            crm=SqliteLogger(config.crm.sqlite_path),
        )

    def _draft(self, ctx: ChatContext) -> AIReply:
        query = " ".join(filter(None, [ctx.product_title, ctx.latest_message]))
        knowledge = self.retriever.context_snippets(query, self.config.ai.max_context_chars)
        reply = self.generator.generate(ctx, knowledge)
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

    def process(self, browser: AlibabaBrowser, url: str) -> ChatContext:
        """Process one inquiry using an already-started browser."""
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
