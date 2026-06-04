"""Parse Alibaba "inquiry notification" emails into :class:`EmailInquiry`.

Alibaba changes its email templates often, so this parser is intentionally
defensive: it tries several labelled-field heuristics, then falls back to the
most prominent ``View Details`` style link. Everything is best-effort — missing
fields come back empty rather than raising.
"""

from __future__ import annotations

import re
from email.message import Message
from email.utils import parsedate_to_datetime
from typing import Optional

from bs4 import BeautifulSoup

from ..entity.models import EmailInquiry

# Anchor text that typically wraps the link into the Trade Center conversation.
_VIEW_DETAILS_TEXTS = (
    "view details",
    "view detail",
    "reply now",
    "reply to buyer",
    "view message",
    "check now",
    "view inquiry",
    "立即回复",
    "查看详情",
    "查看",
)

_LABELS = {
    "buyer_name": ("buyer name", "name", "from", "contact", "客户", "买家", "姓名"),
    "country": ("country", "country/region", "region", "国家", "地区"),
    "product_title": ("product", "product name", "subject", "产品", "商品"),
}


def _html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["style", "script"]):
        tag.decompose()
    return soup.get_text("\n", strip=True)


def _extract_view_details_url(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    best = ""
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href.lower().startswith("http"):
            continue
        text = a.get_text(" ", strip=True).lower()
        if any(t in text for t in _VIEW_DETAILS_TEXTS):
            return href
        # Remember the first Alibaba message/trade link as a fallback.
        if not best and re.search(r"(message|trade|inquiry|tradecenter|i18n)", href, re.I):
            best = href
    return best


def _extract_labelled(text: str, keys: tuple[str, ...]) -> str:
    for line in text.splitlines():
        parts = re.split(r"[:：]", line, maxsplit=1)
        if len(parts) != 2:
            continue
        label = parts[0].strip().lower()
        value = parts[1].strip()
        if value and any(label == k or label.startswith(k) for k in keys):
            return value
    return ""


def _strip_known_labels(text: str) -> str:
    """Heuristic message preview: drop boilerplate-ish label lines."""
    lines = []
    for line in text.splitlines():
        low = line.strip().lower()
        if not low:
            continue
        if any(t in low for t in _VIEW_DETAILS_TEXTS):
            continue
        lines.append(line.strip())
    return " ".join(lines[:6])[:500]


def parse_inquiry(
    *,
    message_id: str,
    subject: str,
    html_body: str,
    text_body: str = "",
    received_raw: Optional[str] = None,
) -> EmailInquiry:
    """Build an :class:`EmailInquiry` from raw email parts."""
    text = _html_to_text(html_body) if html_body else (text_body or "")
    url = _extract_view_details_url(html_body) if html_body else ""

    received_at = None
    if received_raw:
        try:
            received_at = parsedate_to_datetime(received_raw)
        except (TypeError, ValueError):
            received_at = None

    return EmailInquiry(
        message_id=message_id,
        subject=subject,
        buyer_name=_extract_labelled(text, _LABELS["buyer_name"]),
        country=_extract_labelled(text, _LABELS["country"]),
        product_title=_extract_labelled(text, _LABELS["product_title"]),
        message_preview=_strip_known_labels(text),
        view_details_url=url,
        received_at=received_at,
    )


def parse_email_message(msg: Message, message_id: str) -> EmailInquiry:
    """Parse a stdlib :class:`email.message.Message` into an inquiry."""
    subject = str(msg.get("Subject", "") or "")
    received_raw = msg.get("Date")

    html_body, text_body = "", ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if part.get_content_disposition() == "attachment":
                continue
            try:
                payload = part.get_payload(decode=True)
            except Exception:  # pragma: no cover - defensive
                continue
            if not payload:
                continue
            charset = part.get_content_charset() or "utf-8"
            decoded = payload.decode(charset, errors="replace")
            if ctype == "text/html" and not html_body:
                html_body = decoded
            elif ctype == "text/plain" and not text_body:
                text_body = decoded
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            decoded = payload.decode(charset, errors="replace")
            if msg.get_content_type() == "text/html":
                html_body = decoded
            else:
                text_body = decoded

    return parse_inquiry(
        message_id=message_id,
        subject=subject,
        html_body=html_body,
        text_body=text_body,
        received_raw=received_raw,
    )
