"""Proves the ECC seam: Control (InquiryPipeline) runs against fake Boundary
implementations only — no IMAP, browser, network, or DB required.
"""

from src.stargo.config import ReplyRules
from src.stargo.control.inquiry_pipeline import InquiryPipeline
from src.stargo.control.risk_controller import RiskChecker
from src.stargo.entity.models import AIReply, ChatContext


class FakeKnowledge:
    def context_snippets(self, query, max_chars, top_k=5):
        return "KB: APEX electric motorcycle"

    def search(self, query, top_k=5):
        return []


class FakeDrafter:
    def __init__(self, reply):
        self._reply = reply

    def generate(self, ctx, knowledge_context=""):
        return self._reply


class FakeNotifier:
    def __init__(self):
        self.inquiries = []
        self.alerts = []

    @property
    def configured(self):
        return True

    def notify_inquiry(self, ctx, reply, *, url=""):
        self.inquiries.append((ctx, reply, url))
        return True

    def notify_alert(self, title, detail, *, url=""):
        self.alerts.append((title, detail, url))
        return True


class FakeCRM:
    def __init__(self):
        self.records = []

    def log(self, record):
        self.records.append(record)
        return len(self.records)


class FakeBrowser:
    def __init__(self, ctx, sent=True):
        self._ctx = ctx
        self._sent = sent
        self.sent_text = None

    def start(self):
        pass

    def stop(self):
        pass

    def open_inquiry(self, url):
        return self._ctx

    def open_and_reply(self, url, reply_text):
        self.sent_text = reply_text
        return self._ctx, self._sent


def _pipeline(drafter, notifier, crm, rules):
    return InquiryPipeline(
        knowledge=FakeKnowledge(),
        drafter=drafter,
        risk_checker=RiskChecker(rules),
        notifier=notifier,
        crm=crm,
    )


def test_low_risk_autosends_when_enabled():
    ctx = ChatContext(buyer_name="Tom", latest_message="Hi, can you tell me more?")
    reply = AIReply(reply_en="Hi Tom, could you confirm the model and quantity?",
                    auto_send=True, human_approval_required=False)
    notifier, crm = FakeNotifier(), FakeCRM()
    browser = FakeBrowser(ctx, sent=True)
    pipe = _pipeline(FakeDrafter(reply), notifier, crm, ReplyRules(auto_send_low_risk=True))

    pipe.process(browser, "https://x/inq")

    assert browser.sent_text is not None          # reply was sent
    assert crm.records[-1].status == "auto_sent"
    assert len(notifier.inquiries) == 1


def test_high_risk_routes_to_approval():
    ctx = ChatContext(buyer_name="Ahmed", latest_message="Please quote CIF Jakarta price")
    reply = AIReply(reply_en="We can prepare a quotation.",
                    auto_send=True, human_approval_required=False)
    notifier, crm = FakeNotifier(), FakeCRM()
    browser = FakeBrowser(ctx, sent=True)
    pipe = _pipeline(FakeDrafter(reply), notifier, crm, ReplyRules(auto_send_low_risk=True))

    pipe.process(browser, "https://x/inq")

    assert browser.sent_text is None              # never auto-sent a quote
    assert crm.records[-1].status == "awaiting_approval"
    assert notifier.inquiries[0][1].human_approval_required is True


def test_blocked_context_alerts_and_skips_draft():
    ctx = ChatContext(needs_login=True)
    notifier, crm = FakeNotifier(), FakeCRM()
    browser = FakeBrowser(ctx)
    # Drafter would raise if called — it must not be, on a blocked page.
    pipe = _pipeline(FakeDrafter(None), notifier, crm, ReplyRules())

    pipe.process(browser, "https://x/inq")

    assert len(notifier.alerts) == 1
    assert crm.records[-1].status == "needs_login"
