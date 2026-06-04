"""Offline tests for DOM extraction using a fake Playwright-like page."""

from src.stargo.boundary.chat_extract import extract_chat


class FakeLocator:
    def __init__(self, texts):
        self._texts = texts

    def count(self):
        return len(self._texts)

    @property
    def first(self):
        return _Node(self._texts[0]) if self._texts else _Node("")

    def nth(self, i):
        return _Node(self._texts[i])


class _Node:
    def __init__(self, text):
        self._text = text

    def inner_text(self):
        return self._text


class FakePage:
    def __init__(self, body, selector_map, url="https://message.alibaba.com/c/1"):
        self._body = body
        self._map = selector_map
        self.url = url

    def inner_text(self, sel):
        if sel == "body":
            return self._body
        return ""

    def locator(self, sel):
        return FakeLocator(self._map.get(sel, []))


def test_detects_login_page():
    page = FakePage("Please sign in to your account 请登录", {})
    ctx = extract_chat(page)
    assert ctx.needs_login is True
    assert ctx.ok is False


def test_detects_captcha():
    page = FakePage("Security verification: slide to verify 安全验证", {})
    ctx = extract_chat(page)
    assert ctx.needs_captcha is True


def test_extracts_fields_and_messages():
    page = FakePage(
        "Trade Center conversation",
        {
            "[class*='message-content']": ["Hi, what is the price?", "Also do you have CE?"],
            "[class*='product-title']": ["STARGO APEX Electric Motorcycle"],
            "[class*='contact-name']": ["Fred Fred"],
            "[class*='country']": ["United Kingdom"],
        },
    )
    ctx = extract_chat(page)
    assert ctx.ok is True
    assert ctx.buyer_name == "Fred Fred"
    assert ctx.country == "United Kingdom"
    assert "APEX" in ctx.product_title
    assert ctx.latest_message == "Also do you have CE?"
    assert len(ctx.chat_history) == 2


def test_extraction_failed_when_nothing_found():
    page = FakePage("Trade Center but empty", {})
    ctx = extract_chat(page)
    assert ctx.extraction_failed is True
