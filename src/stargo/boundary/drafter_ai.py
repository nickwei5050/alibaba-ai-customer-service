"""Generate a structured English reply for an Alibaba buyer.

If an OpenAI-compatible API key is configured we ask the model for the structured
JSON described in ``config/prompts/reply_system.md``. Otherwise we fall back to a
deterministic, safe, information-collecting reply so the whole pipeline still
runs offline (and during tests).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from ..config import AIConfig
from ..entity.models import AIReply, ChatContext
from ..entity.rules import QUOTE_STRUCTURE, detect_risk_topics

logger = logging.getLogger(__name__)

_PROMPT_PATH = Path(__file__).resolve().parents[3] / "config" / "prompts" / "reply_system.md"

_FALLBACK_REPLY = (
    "Hi {name}, thank you for your inquiry and your interest in STARGO electric "
    "vehicles.\n\nTo prepare an accurate quotation for you, could you please "
    "confirm:\n"
    "1. The model you are interested in\n"
    "2. Order quantity\n"
    "3. Preferred battery option\n"
    "4. Destination country and port\n"
    "5. Whether you need EXW, FOB or CIF pricing\n\n"
    "Once we have these details we will get back to you with the full "
    "information. Looking forward to your reply."
)


def _load_system_prompt() -> str:
    try:
        return _PROMPT_PATH.read_text(encoding="utf-8")
    except OSError:  # pragma: no cover - defensive
        return "You are the STARGO B2B export sales assistant. Reply professionally."


def _offline_reply(ctx: ChatContext) -> AIReply:
    """Safe, generic information-collecting reply (no prices, no commitments)."""
    name = ctx.buyer_name or "there"
    risks = detect_risk_topics(ctx.latest_message)
    return AIReply(
        intent="price_inquiry" if "price" in risks else "greeting",
        customer_level="C",
        missing_info=["model", "quantity", "battery option", "destination port"],
        reply_en=_FALLBACK_REPLY.format(name=name),
        reply_cn="离线模式：仅收集信息，未报价。",
        auto_send=False,
        human_approval_required=False,
        reason="Offline rule-based information-collection reply.",
    )


def _parse_ai_json(raw: str) -> AIReply:
    text = raw.strip()
    # Tolerate ```json fenced blocks.
    if text.startswith("```"):
        text = text.strip("`")
        text = text[text.find("{") :] if "{" in text else text
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1:
        text = text[start : end + 1]
    data = json.loads(text)
    return AIReply.model_validate(data)


class ReplyGenerator:
    def __init__(self, config: AIConfig) -> None:
        self.config = config
        self._system_prompt = _load_system_prompt()

    def _use_openai(self) -> bool:
        return self.config.provider == "openai" and bool(self.config.api_key)

    def generate(self, ctx: ChatContext, knowledge_context: str = "") -> AIReply:
        if not self._use_openai():
            return _offline_reply(ctx)
        try:
            return self._generate_openai(ctx, knowledge_context)
        except Exception as exc:  # pragma: no cover - network/parse errors
            logger.warning("AI generation failed (%s); using offline fallback.", exc)
            return _offline_reply(ctx)

    def _generate_openai(self, ctx: ChatContext, knowledge_context: str) -> AIReply:
        from openai import OpenAI  # lazy import

        client_kwargs = {"api_key": self.config.api_key}
        if self.config.base_url:
            client_kwargs["base_url"] = self.config.base_url
        client = OpenAI(**client_kwargs)

        user_content = (
            f"QUOTING RULE: {QUOTE_STRUCTURE}\n\n"
            f"BUYER NAME: {ctx.buyer_name}\n"
            f"COUNTRY: {ctx.country}\n"
            f"PRODUCT: {ctx.product_title}\n"
            f"LATEST BUYER MESSAGE:\n{ctx.latest_message}\n\n"
            f"CHAT HISTORY:\n" + "\n".join(ctx.chat_history[-10:]) + "\n\n"
            f"KNOWLEDGE BASE SNIPPETS:\n{knowledge_context or '(none)'}\n\n"
            "Respond with ONLY the JSON object."
        )

        resp = client.chat.completions.create(
            model=self.config.model,
            temperature=self.config.temperature,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": self._system_prompt},
                {"role": "user", "content": user_content},
            ],
        )
        return _parse_ai_json(resp.choices[0].message.content or "{}")
