"""Control: the long-running watch loop.

Polls the mail source, and for each new inquiry with a link, opens a browser
session and runs the pipeline. Depends only on Boundary Protocols + the pipeline.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Callable

from ..boundary.interfaces import MailSource, Notifier
from ..config import RuntimeConfig
from ..entity.models import EmailInquiry
from .inquiry_pipeline import InquiryPipeline

logger = logging.getLogger(__name__)


class WatchService:
    def __init__(
        self,
        *,
        mail_source: MailSource,
        pipeline: InquiryPipeline,
        browser_factory: Callable[[], object],
        runtime: RuntimeConfig,
        notifier: Notifier | None = None,
        auto_send: bool = False,
    ) -> None:
        self.mail_source = mail_source
        self.pipeline = pipeline
        self.browser_factory = browser_factory
        self.runtime = runtime
        # Used to alert on emails we couldn't parse a link out of. Falls back to
        # the pipeline's notifier so existing wiring keeps working.
        self.notifier = notifier or getattr(pipeline, "notifier", None)
        self.auto_send = auto_send

    def _handle_unparsed(self, inq: EmailInquiry) -> None:
        """An inquiry email with no View Details URL: dump raw HTML + alert."""
        debug_dir = Path(self.runtime.log_dir).parent / "debug"
        debug_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = debug_dir / f"{ts}-email-unparsed.html"
        try:
            path.write_text(inq.raw_html or "(no html body)", encoding="utf-8")
        except OSError as exc:  # pragma: no cover - defensive
            logger.warning("Could not write unparsed email dump: %s", exc)
            path = None  # type: ignore[assignment]
        logger.warning("No View Details URL in email '%s'; saved %s", inq.subject, path)
        if self.notifier is not None:
            self.notifier.notify_alert(
                "【STARGO 需人工处理】邮件未能提取阿里链接",
                f"主题：{inq.subject or '(无)'}\n"
                f"客户：{inq.buyer_name or '未知'} ｜ 国家：{inq.country or '未知'}\n"
                f"无法从邮件中提取 View Details 链接，已保存原始 HTML：\n{path or '(写入失败)'}",
            )

    def run_once(self, *, dry_run: bool = False) -> int:
        """One poll cycle. Returns the number of inquiries processed.

        Emails with a link are run through the pipeline (passing the email as a
        fallback hint); emails without a link are dumped for debugging and
        flagged to the operator. ``dry_run`` forbids any send to the buyer.
        """
        inquiries = self.mail_source.fetch_new()
        if not inquiries:
            return 0
        logger.info("Fetched %d new inquiry email(s).", len(inquiries))

        for inq in inquiries:
            if not inq.view_details_url:
                self._handle_unparsed(inq)

        batch = [i for i in inquiries if i.view_details_url][: self.runtime.max_per_cycle]
        processed = 0
        if batch:
            with self.browser_factory() as browser:
                for inq in batch:
                    try:
                        self.pipeline.process(
                            browser, inq.view_details_url, dry_run=dry_run, email_hint=inq
                        )
                        processed += 1
                    except Exception as exc:  # pragma: no cover - keep going
                        logger.exception("Failed processing %s: %s", inq.view_details_url, exc)
                    time.sleep(self.runtime.min_action_interval_seconds)
        self.mail_source.mark_processed(inquiries)
        return processed

    def run_forever(self) -> None:
        logger.info(
            "Starting watch loop (interval=%ss, auto_send=%s).",
            self.runtime.check_interval_seconds,
            self.auto_send,
        )
        while True:
            try:
                self.run_once()
            except Exception as exc:  # pragma: no cover - never die on a cycle
                logger.exception("Watch cycle error: %s", exc)
            time.sleep(self.runtime.check_interval_seconds)
