"""Tests for the main-link hardening: safety kill-switch, dry-run, email-hint
fallback, internal-price protection, unparsed-email alerting, and notifications.
"""

from datetime import datetime, timezone

from src.stargo.boundary.knowledge_obsidian import KnowledgeDoc
from src.stargo.boundary.knowledge_retriever import Retriever
from src.stargo.boundary.notifier_wechat import format_inquiry_message
from src.stargo.config import ReplyRules, RuntimeConfig
from src.stargo.control.inquiry_pipeline import InquiryPipeline
from src.stargo.control.risk_controller import RiskChecker
from src.stargo.control.watch_service import WatchService
from src.stargo.entity.models import AIReply, ChatContext, EmailInquiry


# --- fakes -----------------------------------------------------------------
class FakeKnowledge:
    def context_snippets(self, query, max_chars, top_k=5):
        return ""

    def search(self, query, top_k=5):
        return []


class FakeDrafter:
    def __init__(self, reply):
        self._reply = reply

    def generate(self, ctx, knowledge_context=""):
        return self._reply


class FakeNotifier:
    def __init__(self):
        self.inquiries, self.alerts = [], []

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
        self._ctx, self._sent, self.sent_text = ctx, sent, None

    def open_inquiry(self, url):
        return self._ctx

    def open_and_reply(self, url, reply_text):
        self.sent_text = reply_text
        return self._ctx, self._sent


def _pipe(reply, notifier, crm, *, force_manual=False, rules=None):
    return InquiryPipeline(
        knowledge=FakeKnowledge(),
        drafter=FakeDrafter(reply),
        risk_checker=RiskChecker(rules or ReplyRules(auto_send_low_risk=True),
                                 force_manual_only=force_manual),
        notifier=notifier,
        crm=crm,
    )


# --- safety kill-switch ----------------------------------------------------
def test_force_manual_only_never_autosends_even_low_risk():
    ctx = ChatContext(buyer_name="Tom", latest_message="Hi, tell me more about your bikes")
    reply = AIReply(reply_en="Could you confirm the model?",
                    auto_send=True, human_approval_required=False)
    notifier, crm = FakeNotifier(), FakeCRM()
    browser = FakeBrowser(ctx)
    _pipe(reply, notifier, crm, force_manual=True).process(browser, "https://x/inq")

    assert browser.sent_text is None                      # nothing sent
    assert crm.records[-1].auto_send is False
    assert crm.records[-1].approval_required is True


# --- dry-run ---------------------------------------------------------------
def test_dry_run_never_sends_even_if_autosend_allowed():
    ctx = ChatContext(buyer_name="Tom", latest_message="hello")
    reply = AIReply(reply_en="Hi Tom", auto_send=True, human_approval_required=False)
    notifier, crm = FakeNotifier(), FakeCRM()
    browser = FakeBrowser(ctx)
    # force_manual off + auto_send rules on, but dry_run must still block sending.
    _pipe(reply, notifier, crm).process(browser, "https://x/inq", dry_run=True)

    assert browser.sent_text is None
    assert crm.records[-1].status == "dry_run"
    assert len(notifier.inquiries) == 1                   # still notifies for review


# --- email-hint fallback ---------------------------------------------------
def test_email_hint_backfills_missing_dom_fields():
    ctx = ChatContext(latest_message="")                  # DOM extraction got nothing useful
    reply = AIReply(reply_en="Hi")
    notifier, crm = FakeNotifier(), FakeCRM()
    hint = EmailInquiry(message_id="m1", buyer_name="Ahmed", country="Egypt",
                        product_title="STARGO APEX", message_preview="Need price for 50 units",
                        received_at=datetime(2026, 6, 4, tzinfo=timezone.utc))
    _pipe(reply, notifier, crm, force_manual=True).process(
        browser=FakeBrowser(ctx), url="https://x/inq", email_hint=hint)

    rec = crm.records[-1]
    assert rec.buyer_name == "Ahmed" and rec.country == "Egypt"
    assert rec.product_title == "STARGO APEX"
    assert rec.buyer_message == "Need price for 50 units"


# --- internal price protection --------------------------------------------
def test_internal_docs_excluded_from_ai_context_but_searchable():
    docs = [
        KnowledgeDoc("internal-fob", "prices", "NOVA factory cost 1879 RMB secret",
                     "prices/internal-fob.local.md", internal_only=True),
        KnowledgeDoc("quoting", "rules", "Quote as bare vehicle price plus battery NOVA",
                     "rules/quoting.md"),
    ]
    r = Retriever(docs)
    context = r.context_snippets("NOVA price", max_chars=2000)
    assert "secret" not in context and "1879" not in context     # cost never in prompt
    assert "bare vehicle price" in context                        # public rule kept
    # Operator can still find the internal doc via kb-search.
    titles = [d.title for d in r.search("NOVA factory cost", top_k=5)]
    assert "internal-fob" in titles


# --- unparsed email --------------------------------------------------------
def test_watch_alerts_and_dumps_when_no_link(tmp_path):
    class FakeMail:
        def fetch_new(self):
            return [EmailInquiry(message_id="m1", subject="Alibaba Inquiry",
                                 raw_html="<html>no link here</html>")]

        def mark_processed(self, inquiries):
            self.marked = inquiries

    notifier = FakeNotifier()
    runtime = RuntimeConfig(log_dir=str(tmp_path / "logs"))
    ws = WatchService(mail_source=FakeMail(), pipeline=object(),
                      browser_factory=lambda: None, runtime=runtime, notifier=notifier)
    processed = ws.run_once()

    assert processed == 0
    assert len(notifier.alerts) == 1
    dumps = list((tmp_path / "debug").glob("*-email-unparsed.html"))
    assert dumps and "no link here" in dumps[0].read_text()


# --- watch_service: never drop un-handled inquiries ------------------------
class _CtxMgr:
    def __init__(self, obj): self.obj = obj
    def __enter__(self): return self.obj
    def __exit__(self, *a): return False


class RecordingMail:
    def __init__(self, inquiries): self._inq = inquiries; self.marked = None
    def fetch_new(self): return self._inq
    def mark_processed(self, inquiries): self.marked = list(inquiries)


def test_failed_inquiry_is_not_marked_processed():
    class BoomPipeline:
        notifier = None
        def process(self, *a, **k):
            raise RuntimeError("transient browser failure")

    inq = EmailInquiry(message_id="m1", view_details_url="https://x/1")
    mail = RecordingMail([inq])
    ws = WatchService(mail_source=mail, pipeline=BoomPipeline(),
                      browser_factory=lambda: _CtxMgr(object()), runtime=RuntimeConfig())
    ws.run_once()
    assert mail.marked == []                      # retried next cycle, not dropped


def test_overflow_inquiries_are_not_marked():
    class OkPipeline:
        notifier = None
        def process(self, *a, **k): return None

    inqs = [EmailInquiry(message_id=f"m{i}", view_details_url=f"https://x/{i}") for i in range(3)]
    mail = RecordingMail(inqs)
    ws = WatchService(mail_source=mail, pipeline=OkPipeline(),
                      browser_factory=lambda: _CtxMgr(object()),
                      runtime=RuntimeConfig(max_per_cycle=1))
    processed = ws.run_once()
    assert processed == 1
    assert len(mail.marked) == 1                  # only the one we handled


# --- notification content --------------------------------------------------
def test_notification_includes_required_fields():
    ctx = ChatContext(buyer_name="Ravi", country="India", product_title="STARGO TANK",
                      latest_message="What is your MOQ?", screenshot_path="/data/s/loaded.png",
                      received_at=datetime(2026, 6, 4, 9, 30, tzinfo=timezone.utc))
    reply = AIReply(intent="spec_inquiry", customer_level="B", missing_info=["model", "quantity"],
                    reply_en="Hi Ravi, our MOQ is ...", reply_cn="询问MOQ，安全回复",
                    human_approval_required=True, reason="info collection")
    title, body = format_inquiry_message(ctx, reply, url="https://x/inq")
    # Received time is rendered in the operator's local tz — compute the expected
    # string the same way so the test is timezone-independent.
    local_time = ctx.received_at.astimezone().strftime("%Y-%m-%d %H:%M")
    for needle in ["Ravi", "India", "STARGO TANK", "What is your MOQ?", "spec_inquiry",
                   "B", "model, quantity", "Hi Ravi", "询问MOQ", "需要人工确认",
                   "/data/s/loaded.png", local_time]:
        assert needle in (title + body), needle
