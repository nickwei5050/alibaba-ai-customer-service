from src.stargo.ai.risk_checker import RiskChecker
from src.stargo.config import ReplyRules
from src.stargo.models import AIReply, ChatContext


def _reply(text="Hi, could you confirm the model and quantity?"):
    return AIReply(reply_en=text, auto_send=True, human_approval_required=False)


def test_price_in_buyer_message_forces_approval():
    rules = ReplyRules(auto_send_low_risk=True)
    checker = RiskChecker(rules)
    ctx = ChatContext(latest_message="Please send me your CIF price for 20 units")
    decision = checker.evaluate(ctx, _reply())
    assert decision.approval_required is True
    assert decision.auto_send is False
    assert "price" in decision.topics


def test_low_risk_autosend_when_enabled():
    rules = ReplyRules(auto_send_low_risk=True)
    checker = RiskChecker(rules)
    ctx = ChatContext(latest_message="Hi, can you tell me more about this model?")
    decision = checker.evaluate(ctx, _reply())
    assert decision.auto_send is True
    assert decision.approval_required is False


def test_master_switch_off_blocks_autosend():
    rules = ReplyRules(auto_send_low_risk=False)
    checker = RiskChecker(rules)
    ctx = ChatContext(latest_message="Hi there")
    decision = checker.evaluate(ctx, _reply())
    assert decision.auto_send is False
    assert decision.approval_required is False  # low risk, just not auto-sent


def test_forbidden_promise_blocks():
    rules = ReplyRules(auto_send_low_risk=True)
    checker = RiskChecker(rules)
    ctx = ChatContext(latest_message="Hello")
    reply = _reply("You are our exclusive distributor and we guarantee customs clearance.")
    decision = checker.evaluate(ctx, reply)
    assert decision.approval_required is True


def test_certificate_always_requires_approval_even_if_flag_unset():
    rules = ReplyRules(auto_send_low_risk=True)
    checker = RiskChecker(rules)
    ctx = ChatContext(latest_message="Do you have CE certificate?")
    decision = checker.evaluate(ctx, _reply())
    assert decision.approval_required is True
    assert "certificate" in decision.topics


def test_apply_overrides_reply_fields():
    rules = ReplyRules(auto_send_low_risk=True)
    checker = RiskChecker(rules)
    ctx = ChatContext(latest_message="What is your best price?")
    reply = _reply()
    out = checker.apply(ctx, reply)
    assert out.auto_send is False
    assert out.human_approval_required is True
