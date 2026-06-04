"""Optional Google Sheet CRM sync (append-only).

Lazy-imports ``gspread`` so the dependency is only needed when enabled.
"""

from __future__ import annotations

import logging

from ..models import InquiryRecord

logger = logging.getLogger(__name__)

_HEADER = [
    "date", "platform", "buyer_name", "country", "product_title", "product_url",
    "buyer_message", "ai_intent", "customer_level", "ai_reply_en", "auto_send",
    "approval_required", "status", "screenshot_path", "next_follow_up_time",
]


class GoogleSheetLogger:
    def __init__(self, sheet_id: str, service_account_json: str) -> None:
        self.sheet_id = sheet_id
        self.service_account_json = service_account_json
        self._ws = None

    def _worksheet(self):
        if self._ws is not None:
            return self._ws
        import gspread  # lazy import

        client = gspread.service_account(filename=self.service_account_json)
        sheet = client.open_by_key(self.sheet_id)
        ws = sheet.sheet1
        # Ensure header row exists.
        if not ws.row_values(1):
            ws.append_row(_HEADER)
        self._ws = ws
        return ws

    def log(self, record: InquiryRecord) -> None:
        try:
            ws = self._worksheet()
            ws.append_row(
                [
                    record.date.isoformat(),
                    record.platform,
                    record.buyer_name,
                    record.country,
                    record.product_title,
                    record.product_url,
                    record.buyer_message,
                    record.ai_intent,
                    record.customer_level,
                    record.ai_reply_en,
                    str(record.auto_send),
                    str(record.approval_required),
                    record.status,
                    record.screenshot_path,
                    record.next_follow_up_time.isoformat() if record.next_follow_up_time else "",
                ]
            )
        except Exception as exc:  # pragma: no cover - network/auth errors
            logger.warning("Google Sheet sync failed: %s", exc)
