"""Type an approved reply into the Alibaba chat box and send it.

Conservative on purpose: it tries the configured input selectors, types the
text, and clicks a Send button (or presses Enter). It never edits products,
orders, prices or account settings. Returns True only if it believes the
message was sent. Selectors come from :class:`~stargo.config.SelectorConfig`.
"""

from __future__ import annotations

import logging
from typing import Any

from ..config import SelectorConfig

logger = logging.getLogger(__name__)

_DEFAULT_SELECTORS = SelectorConfig()


def send_reply(page: Any, text: str, selectors: SelectorConfig | None = None) -> bool:
    """Best-effort: paste ``text`` into the chat input and send it."""
    sel = selectors or _DEFAULT_SELECTORS

    input_loc = None
    for s in sel.input_box:
        try:
            loc = page.locator(s)
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

    for s in sel.send_button:
        try:
            btn = page.locator(s)
            if btn.count() > 0 and btn.first.is_visible():
                btn.first.click()
                logger.info("Reply sent via send button (%s).", s)
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
