"""Read buyer messages and context off the Alibaba page (DOM-first).

Selectors on Alibaba change frequently, so this module tries a list of likely
selectors and degrades gracefully. ``page`` is a Playwright ``Page`` — typed
loosely to avoid a hard import at module load.
"""

from __future__ import annotations

import logging
from typing import Any

from ..models import ChatContext

logger = logging.getLogger(__name__)

# Indicators that we are not actually on a conversation page.
_LOGIN_HINTS = ("login", "sign in", "passport.alibaba", "请登录", "登录")
_CAPTCHA_HINTS = ("captcha", "verify", "verification", "slide to", "拖动", "验证", "安全验证")

# Candidate selectors, broadest-useful first. None are guaranteed to exist.
_MESSAGE_SELECTORS = (
    "[class*='message-content']",
    "[class*='msg-content']",
    "[class*='chat-content']",
    "[class*='im-message']",
    "div[class*='bubble']",
)
_PRODUCT_TITLE_SELECTORS = (
    "[class*='product-title']",
    "[class*='card-title']",
    "a[href*='/product-detail']",
)


def _page_text(page: Any) -> str:
    try:
        return (page.inner_text("body") or "").strip()
    except Exception:  # pragma: no cover - defensive
        return ""


def _first_text(page: Any, selectors: tuple[str, ...]) -> str:
    for sel in selectors:
        try:
            loc = page.locator(sel)
            if loc.count() > 0:
                txt = (loc.first.inner_text() or "").strip()
                if txt:
                    return txt
        except Exception:
            continue
    return ""


def _all_messages(page: Any) -> list[str]:
    for sel in _MESSAGE_SELECTORS:
        try:
            loc = page.locator(sel)
            n = loc.count()
            if n:
                msgs = []
                for i in range(min(n, 50)):
                    t = (loc.nth(i).inner_text() or "").strip()
                    if t:
                        msgs.append(t)
                if msgs:
                    return msgs
        except Exception:
            continue
    return []


def extract_chat(page: Any) -> ChatContext:
    """Extract a :class:`ChatContext` from the current page."""
    body_low = _page_text(page).lower()
    url = ""
    try:
        url = page.url
    except Exception:
        pass

    needs_login = any(h in body_low for h in _LOGIN_HINTS) and "trade" not in body_low
    needs_captcha = any(h in body_low for h in _CAPTCHA_HINTS)

    if needs_login or needs_captcha:
        return ChatContext(
            product_url=url,
            needs_login=needs_login,
            needs_captcha=needs_captcha,
        )

    messages = _all_messages(page)
    product_title = _first_text(page, _PRODUCT_TITLE_SELECTORS)

    ctx = ChatContext(
        product_title=product_title,
        product_url=url,
        latest_message=messages[-1] if messages else "",
        chat_history=messages,
        extraction_failed=not messages and not product_title,
    )
    if ctx.extraction_failed:
        logger.warning("DOM extraction found no messages; consider screenshot/OCR fallback.")
    return ctx
