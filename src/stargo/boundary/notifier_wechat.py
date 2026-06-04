"""Notification dispatcher + message formatting for inquiries and alerts."""

from __future__ import annotations

import logging

from ..config import WeChatConfig
from ..entity.models import AIReply, ChatContext
from .notify_providers import send_pushplus, send_serverchan, send_wecom_message

logger = logging.getLogger(__name__)


def format_inquiry_message(ctx: ChatContext, reply: AIReply, *, url: str = "") -> tuple[str, str]:
    """Return ``(title, markdown_body)`` for an inquiry notification."""
    if reply.human_approval_required:
        title = f"【STARGO 高意向客户，需人工确认】{ctx.buyer_name or '客户'}"
        action = "⚠️ 不要自动发送，请人工确认后回复。"
    elif reply.auto_send:
        title = f"【STARGO 已自动回复】{ctx.buyer_name or '客户'}"
        action = "✅ 低风险，已自动发送回复。"
    else:
        title = f"【STARGO 新询盘】{ctx.buyer_name or '客户'}"
        action = "🟡 低风险，自动发送已关闭，等待你确认。"

    missing = ", ".join(reply.missing_info) if reply.missing_info else "（无）"
    body = (
        f"**客户**：{ctx.buyer_name or '未知'}\n"
        f"**国家**：{ctx.country or '未知'}\n"
        f"**平台**：Alibaba\n"
        f"**产品**：{ctx.product_title or '未识别'}\n\n"
        f"**客户消息**：\n> {ctx.latest_message or '(空)'}\n\n"
        f"**AI判断**：意图 {reply.intent} ｜ 客户等级 {reply.customer_level}\n"
        f"**缺少信息**：{missing}\n"
        f"**风险原因**：{reply.reason}\n\n"
        f"**AI建议回复**：\n{reply.reply_en}\n\n"
        f"**处理建议**：{action}"
    )
    if url:
        body += f"\n\n[打开阿里对话]({url})"
    return title, body


def format_alert(title: str, detail: str, *, url: str = "") -> tuple[str, str]:
    body = f"**STARGO 系统提醒**\n\n{detail}"
    if url:
        body += f"\n\n[相关链接]({url})"
    return title, body


class WeChatNotifier:
    """Concrete :class:`~stargo.boundary.interfaces.Notifier` implementation."""

    def __init__(self, config: WeChatConfig) -> None:
        self.config = config

    @property
    def configured(self) -> bool:
        p = self.config.provider
        if p == "wecom":
            return bool(self.config.wecom_webhook_url)
        if p == "serverchan":
            return bool(self.config.serverchan_sendkey)
        if p == "pushplus":
            return bool(self.config.pushplus_token)
        return False

    def send(self, title: str, markdown_body: str) -> bool:
        """Dispatch to the configured provider. Returns True on success."""
        if not self.configured:
            logger.warning("WeChat notifier not configured (provider=%s).", self.config.provider)
            return False
        try:
            provider = self.config.provider
            if provider == "wecom":
                # WeCom markdown takes a single content blob; prepend the title.
                send_wecom_message(self.config.wecom_webhook_url, f"# {title}\n\n{markdown_body}")
            elif provider == "serverchan":
                send_serverchan(self.config.serverchan_sendkey, title, markdown_body)
            elif provider == "pushplus":
                send_pushplus(self.config.pushplus_token, title, markdown_body)
            else:
                logger.error("Unknown WeChat provider: %s", provider)
                return False
            logger.info("Notification sent via %s: %s", provider, title)
            return True
        except Exception as exc:  # pragma: no cover - network errors
            logger.error("Notification failed via %s: %s", self.config.provider, exc)
            return False

    def notify_inquiry(self, ctx: ChatContext, reply: AIReply, *, url: str = "") -> bool:
        title, body = format_inquiry_message(ctx, reply, url=url)
        return self.send(title, body)

    def notify_alert(self, title: str, detail: str, *, url: str = "") -> bool:
        t, body = format_alert(title, detail, url=url)
        return self.send(t, body)
