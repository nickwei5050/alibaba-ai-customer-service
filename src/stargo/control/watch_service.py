"""Control: the long-running watch loop.

Polls the mail source, and for each new inquiry with a link, opens a browser
session and runs the pipeline. Depends only on Boundary Protocols + the pipeline.
"""

from __future__ import annotations

import logging
import time
from typing import Callable

from ..boundary.interfaces import MailSource
from ..config import RuntimeConfig
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
        auto_send: bool = False,
    ) -> None:
        self.mail_source = mail_source
        self.pipeline = pipeline
        self.browser_factory = browser_factory
        self.runtime = runtime
        self.auto_send = auto_send

    def run_once(self) -> int:
        """One poll cycle. Returns the number of inquiries processed."""
        inquiries = self.mail_source.fetch_new()
        if not inquiries:
            return 0
        logger.info("Fetched %d new inquiry email(s).", len(inquiries))
        batch = [i for i in inquiries if i.view_details_url][: self.runtime.max_per_cycle]
        processed = 0
        if batch:
            with self.browser_factory() as browser:
                for inq in batch:
                    try:
                        self.pipeline.process(browser, inq.view_details_url)
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
