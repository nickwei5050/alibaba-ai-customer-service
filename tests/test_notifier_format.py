from src.stargo.boundary.notifier_wechat import format_inquiry_message
from src.stargo.entity.models import AIReply, ChatContext


def test_high_risk_title_and_body():
    ctx = ChatContext(buyer_name="Ahmed", country="Indonesia",
                      product_title="APEX", latest_message="Quote 20 units CIF Jakarta")
    reply = AIReply(intent="price_inquiry", customer_level="A",
                    reply_en="We can prepare a quotation...",
                    human_approval_required=True, auto_send=False,
                    reason="High-risk topic(s): price, shipping")
    title, body = format_inquiry_message(ctx, reply, url="https://x")
    assert "人工确认" in title
    assert "Ahmed" in body
    assert "Indonesia" in body
    assert "https://x" in body


def test_autosent_title():
    ctx = ChatContext(buyer_name="Tom", latest_message="hi")
    reply = AIReply(reply_en="Hi Tom...", auto_send=True, human_approval_required=False)
    title, _ = format_inquiry_message(ctx, reply)
    assert "已自动回复" in title
