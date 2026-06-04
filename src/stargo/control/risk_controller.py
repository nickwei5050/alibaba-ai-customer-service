"""Deterministic risk control — the final word on whether a reply auto-sends.

The AI proposes; the RiskChecker disposes. Even if the model returns
``auto_send: true``, we override to human approval whenever the buyer's message
or the drafted reply touches a high-risk topic, or the reply contains a
forbidden promise. This guarantees no quote/freight/commitment is ever sent
without a human.
"""

from __future__ import annotations

from ..config import ReplyRules
from ..entity.models import AIReply, ChatContext
from ..entity.rules import (
    contains_forbidden_promise,
    detect_risk_topics,
)

# Maps a detected topic to the config flag that gates it. Topics without a flag
# (certificate, customs, after_sales) always require approval.
_TOPIC_TO_FLAG = {
    "price": "require_approval_for_price",
    "shipping": "require_approval_for_shipping",
    "discount": "require_approval_for_price",
    "distributor": "require_approval_for_distributor",
    "payment_terms": "require_approval_for_payment_terms",
    "delivery_time": "require_approval_for_delivery_time",
}
_ALWAYS_APPROVE = {"certificate", "customs", "after_sales"}


class RiskDecision:
    def __init__(self, auto_send: bool, approval_required: bool, reason: str, topics: list[str]):
        self.auto_send = auto_send
        self.approval_required = approval_required
        self.reason = reason
        self.topics = topics


class RiskChecker:
    def __init__(self, rules: ReplyRules) -> None:
        self.rules = rules

    def evaluate(self, ctx: ChatContext, reply: AIReply) -> RiskDecision:
        combined = f"{ctx.latest_message}\n{reply.reply_en}"
        topics = sorted(set(detect_risk_topics(combined)))

        gating: list[str] = []
        for topic in topics:
            if topic in _ALWAYS_APPROVE:
                gating.append(topic)
            else:
                flag = _TOPIC_TO_FLAG.get(topic)
                if flag and getattr(self.rules, flag, True):
                    gating.append(topic)

        if contains_forbidden_promise(reply.reply_en):
            return RiskDecision(
                auto_send=False,
                approval_required=True,
                reason="Reply contains a forbidden promise; human approval required.",
                topics=topics,
            )

        if gating:
            return RiskDecision(
                auto_send=False,
                approval_required=True,
                reason="High-risk topic(s): " + ", ".join(gating),
                topics=topics,
            )

        # No risk topics. Honor config master switch for auto-send.
        if not self.rules.auto_send_low_risk:
            return RiskDecision(
                auto_send=False,
                approval_required=False,
                reason="Low-risk, but auto-send is disabled in config.",
                topics=topics,
            )

        return RiskDecision(
            auto_send=True,
            approval_required=False,
            reason="Low-risk information-collection reply.",
            topics=topics,
        )

    def apply(self, ctx: ChatContext, reply: AIReply) -> AIReply:
        """Return a copy of ``reply`` with routing fields overridden by policy."""
        decision = self.evaluate(ctx, reply)
        return reply.model_copy(
            update={
                "auto_send": decision.auto_send,
                "human_approval_required": decision.approval_required,
                "reason": decision.reason,
            }
        )
