from src.stargo.inbox.parse_alibaba_email import parse_inquiry

SAMPLE_HTML = """
<html><body>
  <p>Buyer Name: Fred Fred</p>
  <p>Country: United Kingdom</p>
  <p>Product: STARGO APEX Electric Motorcycle</p>
  <p>Message: Hi, what is the price?</p>
  <a href="https://message.alibaba.com/conversation/12345">View Details</a>
  <a href="https://example.com/unsubscribe">Unsubscribe</a>
</body></html>
"""


def test_parse_extracts_fields():
    inq = parse_inquiry(
        message_id="<abc@mail>",
        subject="Alibaba Inquiry Notification",
        html_body=SAMPLE_HTML,
    )
    assert inq.buyer_name == "Fred Fred"
    assert inq.country == "United Kingdom"
    assert "APEX" in inq.product_title
    assert inq.view_details_url == "https://message.alibaba.com/conversation/12345"
    assert inq.dedupe_key() == "<abc@mail>"


def test_parse_falls_back_to_url_when_no_message_id():
    inq = parse_inquiry(message_id="", subject="x", html_body=SAMPLE_HTML)
    assert inq.dedupe_key() == "https://message.alibaba.com/conversation/12345"
