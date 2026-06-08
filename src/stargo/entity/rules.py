"""STARGO hard rules and risk-topic detection.

These rules are the safety backbone. The AI is *told* the rules in the system
prompt, but the :class:`~stargo.control.risk_controller.RiskChecker` also enforces them
deterministically here, so a careless model output can never auto-send a quote.
"""

from __future__ import annotations

# Topics that always require a human before anything is sent to the buyer.
HIGH_RISK_TOPICS: dict[str, tuple[str, ...]] = {
    "price": (
        "price", "quote", "quotation", "cost", "how much", "usd", "$",
        "exw", "fob", "cif", "报价", "价格", "多少钱",
    ),
    "shipping": (
        "shipping cost", "freight", "sea freight", "ocean freight",
        "delivery cost", "shipping fee", "运费", "海运费",
    ),
    "discount": ("discount", "best price", "lowest price", "折扣", "优惠"),
    "distributor": (
        "distributor", "dealer", "agent", "exclusive", "sole agent",
        "representative", "代理", "经销", "独家",
    ),
    "payment_terms": (
        "payment term", "deposit", "t/t", "letter of credit", "l/c",
        "30% deposit", "付款方式", "定金",
    ),
    "delivery_time": (
        "lead time", "delivery time", "how long", "shipment date",
        "when can you ship", "交期", "货期",
    ),
    "certificate": (
        "certificate", "ce ", "eec", "coc", "dot", "epa", "homologation",
        "认证", "证书",
    ),
    "customs": ("customs", "clearance", "duty", "import tax", "清关", "关税"),
    "after_sales": (
        "compensation", "refund", "warranty claim", "broken", "damaged",
        "defective", "complaint", "赔偿", "退款", "投诉",
    ),
}

# Phrases the AI reply must never contain on an auto-send path.
FORBIDDEN_PROMISES: tuple[str, ...] = (
    "we guarantee customs clearance",
    "we will clear customs",
    "guaranteed certificate",
    "exclusive distributor",
    "you are our sole agent",
)

# The canonical quoting structure, injected into prompts and the README.
QUOTE_STRUCTURE = (
    "Always quote as: bare vehicle price + battery price = total EXW factory "
    "price. Exact shipping cost requires destination country, destination port, "
    "quantity and battery type."
)


def detect_risk_topics(text: str) -> list[str]:
    """Return the names of high-risk topics mentioned in ``text``."""
    low = (text or "").lower()
    return [topic for topic, kws in HIGH_RISK_TOPICS.items() if any(k in low for k in kws)]


def contains_forbidden_promise(text: str) -> bool:
    low = (text or "").lower()
    return any(p in low for p in FORBIDDEN_PROMISES)
