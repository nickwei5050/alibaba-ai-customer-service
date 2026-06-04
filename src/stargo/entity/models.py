"""Shared pydantic data models for the inquiry pipeline."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class EmailInquiry(BaseModel):
    """A parsed Alibaba inquiry-notification email."""

    message_id: str
    subject: str = ""
    buyer_name: str = ""
    country: str = ""
    message_preview: str = ""
    product_title: str = ""
    view_details_url: str = ""
    received_at: Optional[datetime] = None
    # Raw HTML body, retained so a parse failure can be dumped for debugging.
    raw_html: str = ""

    def dedupe_key(self) -> str:
        """Stable key for deduplication (message id, falling back to the URL)."""
        return self.message_id or self.view_details_url


class ChatContext(BaseModel):
    """What we read off the Alibaba Trade Center page via Playwright."""

    buyer_name: str = ""
    country: str = ""
    product_title: str = ""
    product_url: str = ""
    latest_message: str = ""
    chat_history: list[str] = Field(default_factory=list)
    needs_login: bool = False
    needs_captcha: bool = False
    extraction_failed: bool = False
    screenshot_path: str = ""
    # Optional carry-throughs for the notification / CRM (from the source email).
    received_at: Optional[datetime] = None
    message_preview: str = ""

    def merge_email_hint(self, email: "EmailInquiry") -> None:
        """Fill any field the DOM extraction missed from the source email."""
        self.buyer_name = self.buyer_name or email.buyer_name
        self.country = self.country or email.country
        self.product_title = self.product_title or email.product_title
        self.latest_message = self.latest_message or email.message_preview
        self.message_preview = self.message_preview or email.message_preview
        self.received_at = self.received_at or email.received_at

    @property
    def ok(self) -> bool:
        return not (self.needs_login or self.needs_captcha or self.extraction_failed)


class AIReply(BaseModel):
    """Structured output of the AI reply generator."""

    intent: str = "other"
    customer_level: str = "C"
    missing_info: list[str] = Field(default_factory=list)
    reply_en: str = ""
    reply_cn: str = ""
    auto_send: bool = False
    human_approval_required: bool = True
    reason: str = ""


class InquiryRecord(BaseModel):
    """A full CRM row for one processed inquiry."""

    date: datetime = Field(default_factory=_utcnow)
    platform: str = "alibaba"
    buyer_name: str = ""
    country: str = ""
    product_title: str = ""
    product_url: str = ""
    buyer_message: str = ""
    ai_intent: str = ""
    customer_level: str = ""
    missing_info: str = ""       # comma-joined for the flat CRM row
    ai_reply_en: str = ""
    ai_reply_cn: str = ""
    auto_send: bool = False
    approval_required: bool = True
    status: str = "new"          # new | auto_sent | awaiting_approval | failed | needs_login | dry_run | parse_failed
    screenshot_path: str = ""
    next_follow_up_time: Optional[datetime] = None
