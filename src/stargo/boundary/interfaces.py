"""Boundary Protocols — the contracts the Control layer programs against.

These are structural (``typing.Protocol``) so concrete adapters don't need to
inherit anything; they just need matching method signatures. This is the seam
that lets us swap IMAP for Gmail API, Playwright for a stub, SQLite for a Sheet,
etc., without touching Control-layer code.
"""

from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable

from ..entity.models import AIReply, ChatContext, EmailInquiry, InquiryRecord


@runtime_checkable
class DedupeStore(Protocol):
    def seen(self, key: str) -> bool: ...
    def mark(self, key: str, *, subject: str = "", buyer_name: str = "", url: str = "") -> None: ...


@runtime_checkable
class MailSource(Protocol):
    """Polls a mailbox and yields new, de-duplicated inquiries."""

    def fetch_new(self) -> list[EmailInquiry]: ...
    def mark_processed(self, inquiries) -> None: ...


@runtime_checkable
class BrowserDriver(Protocol):
    """Drives a logged-in browser session against Alibaba Trade Center."""

    def start(self) -> None: ...
    def stop(self) -> None: ...
    def open_inquiry(self, url: str) -> ChatContext: ...
    def open_and_reply(self, url: str, reply_text: str) -> tuple[ChatContext, bool]: ...


@runtime_checkable
class KnowledgeBase(Protocol):
    """Retrieves relevant knowledge snippets for a query."""

    def context_snippets(self, query: str, max_chars: int, top_k: int = 5) -> str: ...
    def search(self, query: str, top_k: int = 5): ...


@runtime_checkable
class ReplyDrafter(Protocol):
    """Turns a chat context (+ knowledge) into a structured draft reply."""

    def generate(self, ctx: ChatContext, knowledge_context: str = "") -> AIReply: ...


@runtime_checkable
class Notifier(Protocol):
    """Pushes inquiry/alert notifications to WeChat / WeCom."""

    @property
    def configured(self) -> bool: ...
    def notify_inquiry(self, ctx: ChatContext, reply: AIReply, *, url: str = "") -> bool: ...
    def notify_alert(self, title: str, detail: str, *, url: str = "") -> bool: ...


@runtime_checkable
class CRMSink(Protocol):
    """Persists inquiry records (SQLite, Google Sheet, ...)."""

    def log(self, record: InquiryRecord) -> Optional[int]: ...
