"""Read buyer messages and context off the Alibaba page (DOM-first).

Selectors on Alibaba change frequently, so this module tries a list of likely
selectors and degrades gracefully. The selector lists come from
:class:`~stargo.config.SelectorConfig` (override in config.yaml; inspect matches
with ``debug-url``). ``page`` is a Playwright ``Page`` — typed loosely to avoid a
hard import at module load.
"""

from __future__ import annotations

import logging
from typing import Any

from ..config import SelectorConfig
from ..entity.models import ChatContext

logger = logging.getLogger(__name__)

# Indicators that we are not actually on a conversation page.
_LOGIN_HINTS = ("login", "sign in", "passport.alibaba", "请登录", "登录")
_CAPTCHA_HINTS = ("captcha", "verify", "verification", "slide to", "拖动", "验证", "安全验证")

# Default selector set, used when no SelectorConfig is supplied (e.g. tests).
_DEFAULT_SELECTORS = SelectorConfig()


def _page_text(page: Any) -> str:
    try:
        return (page.inner_text("body") or "").strip()
    except Exception:  # pragma: no cover - defensive
        return ""


def _first_text(page: Any, selectors: list[str]) -> tuple[str, str]:
    """Return ``(text, matched_selector)`` for the first selector with text."""
    for sel in selectors:
        try:
            loc = page.locator(sel)
            if loc.count() > 0:
                txt = (loc.first.inner_text() or "").strip()
                if txt:
                    return txt, sel
        except Exception:
            continue
    return "", ""


def _all_messages(page: Any, selectors: list[str]) -> tuple[list[str], str]:
    """Return ``(messages, matched_selector)`` for the first selector with hits."""
    for sel in selectors:
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
                    return msgs, sel
        except Exception:
            continue
    return [], ""


def _selectors(selectors: SelectorConfig | None) -> SelectorConfig:
    return selectors or _DEFAULT_SELECTORS


def extract_chat(page: Any, selectors: SelectorConfig | None = None) -> ChatContext:
    """Extract a :class:`ChatContext` from the current page."""
    sel = _selectors(selectors)
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

    messages, _ = _all_messages(page, sel.message)
    product_title, _ = _first_text(page, sel.product_title)
    buyer_name, _ = _first_text(page, sel.buyer_name)
    country, _ = _first_text(page, sel.country)

    ctx = ChatContext(
        buyer_name=buyer_name,
        country=country,
        product_title=product_title,
        product_url=url,
        latest_message=messages[-1] if messages else "",
        chat_history=messages,
        extraction_failed=not messages and not product_title,
    )
    if ctx.extraction_failed:
        logger.warning("DOM extraction found no messages; selectors likely need tuning.")
    return ctx


def probe_selectors(page: Any, selectors: SelectorConfig | None = None) -> dict[str, Any]:
    """Diagnostic: report which selector matched each field (for ``debug-url``).

    Returns a dict mapping field name -> match info, plus presence flags for the
    input box and send button. Sends nothing, interacts with nothing.
    """
    sel = _selectors(selectors)
    report: dict[str, Any] = {}

    for field, sels in (
        ("buyer_name", sel.buyer_name),
        ("country", sel.country),
        ("product_title", sel.product_title),
    ):
        text, matched = _first_text(page, sels)
        report[field] = {
            "matched_selector": matched or "(none)",
            "value_preview": text[:120],
        }

    messages, msg_sel = _all_messages(page, sel.message)
    report["chat_history"] = {
        "matched_selector": msg_sel or "(none)",
        "count": len(messages),
        "latest_preview": (messages[-1][:160] if messages else ""),
    }

    def _present(sels: list[str]) -> dict[str, Any]:
        for s in sels:
            try:
                loc = page.locator(s)
                if loc.count() > 0:
                    try:
                        visible = bool(loc.first.is_visible())
                    except Exception:
                        visible = False
                    return {"matched_selector": s, "count": loc.count(), "visible": visible}
            except Exception:
                continue
        return {"matched_selector": "(none)", "count": 0, "visible": False}

    report["input_box"] = _present(sel.input_box)
    report["send_button"] = _present(sel.send_button)
    return report
