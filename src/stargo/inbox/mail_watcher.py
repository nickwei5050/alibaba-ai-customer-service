"""IMAP mail watcher: poll a mailbox for Alibaba inquiry notifications.

Works with Gmail (``imap.gmail.com``, requires an App Password) and QQ Mail
(``imap.qq.com``, requires the IMAP authorization code). Returns parsed,
de-duplicated :class:`EmailInquiry` objects.
"""

from __future__ import annotations

import imaplib
import email
import logging
from datetime import datetime, timedelta
from email.header import decode_header, make_header
from typing import Iterable

from ..config import EmailConfig
from ..models import EmailInquiry
from .parse_alibaba_email import parse_email_message
from .store import ProcessedStore

logger = logging.getLogger(__name__)


def _decode(value: str | None) -> str:
    if not value:
        return ""
    try:
        return str(make_header(decode_header(value)))
    except Exception:  # pragma: no cover - defensive
        return value


class MailWatcher:
    def __init__(self, config: EmailConfig, store: ProcessedStore) -> None:
        self.config = config
        self.store = store

    def _connect(self) -> imaplib.IMAP4_SSL:
        conn = imaplib.IMAP4_SSL(self.config.imap_host, self.config.imap_port)
        conn.login(self.config.user, self.config.password)
        conn.select(self.config.folder)
        return conn

    def _search_criteria(self) -> str:
        since = (datetime.now() - timedelta(days=self.config.lookback_days)).strftime("%d-%b-%Y")
        # IMAP SUBJECT search is server-side; we still re-check locally.
        return f'(SINCE "{since}")'

    def fetch_new(self) -> list[EmailInquiry]:
        """Poll once and return new, matching, not-yet-seen inquiries."""
        if not self.config.user or not self.config.password:
            logger.warning("Email credentials are not configured; skipping mail poll.")
            return []

        conn = self._connect()
        try:
            typ, data = conn.search(None, self._search_criteria())
            if typ != "OK" or not data or not data[0]:
                return []
            ids = data[0].split()
            results: list[EmailInquiry] = []
            keyword = self.config.subject_keyword.lower()

            for num in reversed(ids):  # newest first
                typ, msg_data = conn.fetch(num, "(RFC822)")
                if typ != "OK" or not msg_data or not msg_data[0]:
                    continue
                raw = msg_data[0][1]
                msg = email.message_from_bytes(raw)

                subject = _decode(msg.get("Subject"))
                if keyword and keyword not in subject.lower():
                    continue

                message_id = _decode(msg.get("Message-ID")) or f"uid-{num.decode()}"
                if self.store.seen(message_id):
                    continue

                inquiry = parse_email_message(msg, message_id)
                inquiry.subject = subject
                results.append(inquiry)

            return results
        finally:
            try:
                conn.close()
            except Exception:  # pragma: no cover
                pass
            conn.logout()

    def mark_processed(self, inquiries: Iterable[EmailInquiry]) -> None:
        for inq in inquiries:
            self.store.mark(
                inq.dedupe_key(),
                subject=inq.subject,
                buyer_name=inq.buyer_name,
                url=inq.view_details_url,
            )
