"""Composition root: wire concrete Boundary adapters into Control services.

This is the *only* place that knows about both concrete implementations and the
Control layer. Everything else depends on Entity models and Boundary Protocols.
To swap an adapter (e.g. Gmail API instead of IMAP), change it here — nothing in
``control/`` needs to move.
"""

from __future__ import annotations

from .boundary.browser_playwright import alibaba_browser
from .boundary.crm_sqlite import SqliteLogger
from .boundary.dedupe_sqlite import ProcessedStore
from .boundary.drafter_ai import ReplyGenerator
from .boundary.knowledge_retriever import Retriever
from .boundary.mail_imap import MailWatcher
from .boundary.notifier_wechat import WeChatNotifier
from .config import Config
from .control.inquiry_pipeline import InquiryPipeline
from .control.risk_controller import RiskChecker
from .control.watch_service import WatchService


class AppContext:
    """Lazily-constructed application graph built from :class:`Config`."""

    def __init__(self, config: Config) -> None:
        self.config = config

        # Boundary adapters (concrete).
        self.store = ProcessedStore(config.runtime.db_path)
        self.mail = MailWatcher(config.email, self.store)
        self.notifier = WeChatNotifier(config.wechat)
        self.crm = SqliteLogger(config.crm.sqlite_path)
        self.knowledge = Retriever.from_config(config.knowledge)
        self.drafter = ReplyGenerator(config.ai)

        # Control (depends only on the above via Protocols).
        self.risk = RiskChecker(config.reply_rules)
        self.pipeline = InquiryPipeline(
            knowledge=self.knowledge,
            drafter=self.drafter,
            risk_checker=self.risk,
            notifier=self.notifier,
            crm=self.crm,
            max_context_chars=config.ai.max_context_chars,
        )

    def browser(self):
        """Context manager yielding a started :class:`BrowserDriver`."""
        return alibaba_browser(self.config.browser, self.config.runtime)

    def watch_service(self) -> WatchService:
        return WatchService(
            mail_source=self.mail,
            pipeline=self.pipeline,
            browser_factory=self.browser,
            runtime=self.config.runtime,
            auto_send=self.config.reply_rules.auto_send_low_risk,
        )
