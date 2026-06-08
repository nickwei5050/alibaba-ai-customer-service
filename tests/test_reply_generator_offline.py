from src.stargo.boundary.drafter_ai import ReplyGenerator
from src.stargo.config import AIConfig
from src.stargo.entity.models import ChatContext


def test_offline_reply_is_safe_and_collects_info():
    gen = ReplyGenerator(AIConfig(provider="offline", api_key=""))
    ctx = ChatContext(buyer_name="Fred", latest_message="what is the price?")
    reply = gen.generate(ctx, knowledge_context="")
    assert reply.auto_send is False  # offline path never auto-decides risky sends
    assert "Fred" in reply.reply_en
    # Must not invent a price.
    assert "$" not in reply.reply_en
    assert reply.missing_info
