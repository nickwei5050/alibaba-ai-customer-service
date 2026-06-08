"""Drive a logged-in local Chrome with Playwright (persistent profile).

Key safety properties:
- Uses a **persistent** browser context (your existing Chrome login). We never
  store or type the Alibaba password.
- Runs **visible** (non-headless) so you can log in / solve a captcha once.
- On login/captcha/extraction failure it stops and lets the caller notify you;
  it never tries to bypass verification.

Playwright is imported lazily so the rest of the package (email, AI, notify,
tests) works without browsers installed.
"""

from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

from ..config import BrowserConfig, RuntimeConfig, SelectorConfig
from ..entity.models import ChatContext
from .chat_extract import extract_chat, probe_selectors
from .chat_send import send_reply as _send_reply

logger = logging.getLogger(__name__)


class AlibabaBrowser:
    def __init__(
        self,
        browser_cfg: BrowserConfig,
        runtime_cfg: RuntimeConfig,
        selectors: SelectorConfig | None = None,
    ) -> None:
        self.cfg = browser_cfg
        self.runtime = runtime_cfg
        self.selectors = selectors or SelectorConfig()
        self._pw = None
        self._context = None
        Path(runtime_cfg.screenshot_dir).mkdir(parents=True, exist_ok=True)

    # -- lifecycle ---------------------------------------------------------
    def start(self) -> None:
        try:
            from playwright.sync_api import sync_playwright  # lazy import
        except ImportError as exc:
            raise RuntimeError(
                "Playwright 未安装。请先运行：pip install -r requirements.txt"
            ) from exc

        self._pw = sync_playwright().start()
        launch_kwargs: dict[str, Any] = {
            "user_data_dir": self.cfg.chrome_user_data_dir,
            "headless": self.cfg.headless,
            "slow_mo": self.cfg.slow_mo_ms,
        }
        if self.cfg.channel:
            launch_kwargs["channel"] = self.cfg.channel
        try:
            self._context = self._pw.chromium.launch_persistent_context(**launch_kwargs)
        except Exception as exc:
            msg = str(exc)
            if "Executable doesn't exist" in msg or "playwright install" in msg:
                raise RuntimeError(
                    "Chromium 浏览器未安装。请运行：python -m playwright install chromium"
                ) from exc
            if self.cfg.channel and ("channel" in msg.lower() or "not found" in msg.lower()):
                raise RuntimeError(
                    f"找不到 Chrome 通道 '{self.cfg.channel}'。请安装 Google Chrome，"
                    "或在 config.yaml 把 browser.channel 设为空字符串以使用内置 Chromium。"
                ) from exc
            raise
        logger.info("Launched persistent Chrome context (%s).", self.cfg.chrome_user_data_dir)

    def stop(self) -> None:
        try:
            if self._context:
                self._context.close()
        finally:
            if self._pw:
                self._pw.stop()
        self._context = None
        self._pw = None

    # -- helpers -----------------------------------------------------------
    def _screenshot(self, page: Any, tag: str) -> str:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = Path(self.runtime.screenshot_dir) / f"{ts}-{tag}.png"
        try:
            page.screenshot(path=str(path), full_page=True)
            return str(path)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Screenshot failed (%s): %s", tag, exc)
            return ""

    def _dump_dom(self, page: Any, tag: str = "inquiry-dom") -> str:
        """Save the page's DOM text under data/debug for traceability / selector
        tuning. Returns the path (empty string on failure)."""
        debug_dir = Path(self.runtime.screenshot_dir).parent / "debug"
        debug_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = debug_dir / f"{ts}-{tag}.txt"
        try:
            path.write_text(page.inner_text("body") or "", encoding="utf-8")
            return str(path)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("DOM dump failed (%s): %s", tag, exc)
            return ""

    # -- main operations ---------------------------------------------------
    def open_inquiry(self, url: str) -> ChatContext:
        """Open a View Details URL and extract the chat context."""
        if self._context is None:
            raise RuntimeError("Browser not started; call start() first.")
        page = self._context.new_page()
        page.set_default_timeout(self.cfg.nav_timeout_ms)
        try:
            self._screenshot(page, "before")
            page.goto(url, wait_until="domcontentloaded")
            time.sleep(max(self.runtime.min_action_interval_seconds, 2))
            ctx = extract_chat(page, self.selectors)
            ctx.screenshot_path = self._screenshot(page, "loaded")
            ctx.debug_report_path = self._dump_dom(page, "inquiry-dom")
            return ctx
        except Exception as exc:
            logger.error("Failed to open inquiry %s: %s", url, exc)
            shot = self._screenshot(page, "error")
            return ChatContext(product_url=url, extraction_failed=True, screenshot_path=shot)
        finally:
            try:
                page.close()
            except Exception:
                pass

    def inspect(self, url: str) -> dict:
        """Debug mode: open the URL, dump DOM text/HTML + screenshots, attempt
        extraction, and return a report. **Never sends a reply.**"""
        if self._context is None:
            raise RuntimeError("Browser not started; call start() first.")
        debug_dir = Path(self.runtime.screenshot_dir).parent / "debug"
        debug_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")

        page = self._context.new_page()
        page.set_default_timeout(self.cfg.nav_timeout_ms)
        report: dict = {"url": url, "timestamp": ts, "screenshots": []}
        try:
            report["screenshots"].append(self._screenshot(page, "debug-before"))
            page.goto(url, wait_until="domcontentloaded")
            time.sleep(max(self.runtime.min_action_interval_seconds, 2))
            report["screenshots"].append(self._screenshot(page, "debug-loaded"))

            # Dump DOM text + raw HTML for offline selector tuning.
            dom_text = ""
            try:
                dom_text = page.inner_text("body") or ""
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("DOM text dump failed: %s", exc)
            dom_path = debug_dir / f"{ts}-dom.txt"
            dom_path.write_text(dom_text, encoding="utf-8")
            report["dom_text_path"] = str(dom_path)
            report["dom_chars"] = len(dom_text)
            try:
                html_path = debug_dir / f"{ts}-page.html"
                html_path.write_text(page.content() or "", encoding="utf-8")
                report["html_path"] = str(html_path)
            except Exception:  # pragma: no cover
                report["html_path"] = ""

            ctx = extract_chat(page, self.selectors)
            report["needs_login"] = ctx.needs_login
            report["needs_captcha"] = ctx.needs_captcha
            report["extraction_failed"] = ctx.extraction_failed
            report["buyer_name"] = ctx.buyer_name
            report["country"] = ctx.country
            report["product_title"] = ctx.product_title
            report["product_url"] = ctx.product_url
            report["latest_message"] = ctx.latest_message
            report["chat_history_count"] = len(ctx.chat_history)
            report["chat_preview"] = ctx.chat_history[:5]
            # Per-field selector diagnostics + input/send presence (no sending).
            report["selector_report"] = probe_selectors(page, self.selectors)
            return report
        except Exception as exc:
            logger.error("inspect failed for %s: %s", url, exc)
            report["error"] = str(exc)
            report["screenshots"].append(self._screenshot(page, "debug-error"))
            return report
        finally:
            try:
                page.close()
            except Exception:
                pass

    def open_and_reply(self, url: str, reply_text: str) -> tuple[ChatContext, bool]:
        """Open the inquiry, then type+send ``reply_text``. Returns (ctx, sent)."""
        if self._context is None:
            raise RuntimeError("Browser not started; call start() first.")
        page = self._context.new_page()
        page.set_default_timeout(self.cfg.nav_timeout_ms)
        sent = False
        try:
            page.goto(url, wait_until="domcontentloaded")
            time.sleep(max(self.runtime.min_action_interval_seconds, 2))
            ctx = extract_chat(page, self.selectors)
            if not ctx.ok:
                ctx.screenshot_path = self._screenshot(page, "blocked")
                return ctx, False
            sent = _send_reply(page, reply_text, self.selectors)
            time.sleep(max(self.runtime.min_action_interval_seconds, 1))
            ctx.screenshot_path = self._screenshot(page, "after-send" if sent else "send-failed")
            return ctx, sent
        except Exception as exc:
            logger.error("open_and_reply failed for %s: %s", url, exc)
            shot = self._screenshot(page, "error")
            return ChatContext(product_url=url, extraction_failed=True, screenshot_path=shot), False
        finally:
            try:
                page.close()
            except Exception:
                pass


@contextmanager
def alibaba_browser(
    browser_cfg: BrowserConfig,
    runtime_cfg: RuntimeConfig,
    selectors: SelectorConfig | None = None,
) -> Iterator[AlibabaBrowser]:
    browser = AlibabaBrowser(browser_cfg, runtime_cfg, selectors)
    browser.start()
    try:
        yield browser
    finally:
        browser.stop()
