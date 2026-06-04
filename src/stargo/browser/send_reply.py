"""Type an approved reply into the Alibaba chat box and send it.

Conservative on purpose: it tries known input selectors, types the text, and
clicks a Send button (or presses Enter). It never edits products, orders, prices
or account settings. Returns True only if it believes the message was sent.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

_INPUT_SELECTORS = (
    "textarea[class*='input']",
    "div[contenteditable='true']",
    "textarea",
    "[class*='editor'] [contenteditable='true']",
)
_SEND_BUTTON_SELECTORS = (
    "button:has-text('Send')",
    "button:has-text('发送')",
    "[class*='send-btn']",
    "[class*='btn-send']",
)


def send_reply(page: Any, text: str) -> bool:
    """Best-effort: paste ``text`` into the chat input and send it."""
    input_loc = None
    for sel in _INPUT_SELECTORS:
        try:
            loc = page.locator(sel)
            if loc.count() > 0 and loc.first.is_visible():
                input_loc = loc.first
                break
        except Exception:
            continue

    if input_loc is None:
        logger.error("Could not locate Alibaba chat input; not sending.")
        return False

    try:
        input_loc.click()
        input_loc.fill("")  # clear any draft
        input_loc.type(text, delay=20)
    except Exception as exc:
        logger.error("Failed to type reply: %s", exc)
        return False

    for sel in _SEND_BUTTON_SELECTORS:
        try:
            btn = page.locator(sel)
            if btn.count() > 0 and btn.first.is_visible():
                btn.first.click()
                logger.info("Reply sent via send button (%s).", sel)
                return True
        except Exception:
            continue

    # Fallback: many chat inputs send on Enter.
    try:
        input_loc.press("Enter")
        logger.info("Reply sent via Enter key.")
        return True
    except Exception as exc:
        logger.error("Failed to send reply: %s", exc)
        return False
