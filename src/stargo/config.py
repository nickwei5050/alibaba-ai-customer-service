"""Configuration loading: YAML + ``${ENV}`` expansion, validated with pydantic."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

try:  # optional, but recommended
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None  # type: ignore[assignment]

_ENV_PATTERN = re.compile(r"\$\{([^}]+)\}")


class EmailConfig(BaseModel):
    provider: str = "gmail"
    imap_host: str = "imap.gmail.com"
    imap_port: int = 993
    folder: str = "INBOX"
    subject_keyword: str = "Alibaba Inquiry Notification"
    user: str = ""
    password: str = ""
    lookback_days: int = 3


class BrowserConfig(BaseModel):
    chrome_user_data_dir: str = "./chrome-profile"
    chrome_profile: str = "Default"
    channel: str = "chrome"
    headless: bool = False
    nav_timeout_ms: int = 45000
    slow_mo_ms: int = 250


class KnowledgeConfig(BaseModel):
    obsidian_path: str = "./knowledge"
    notion_enabled: bool = False
    notion_api_key: str = ""
    notion_database_id: str = ""
    # Structured product-catalog database (one row per model). Pulls all models'
    # specs (voltage/motor/range/...) into the index when synced locally.
    notion_catalog_database_id: str = ""


class AIConfig(BaseModel):
    provider: str = "openai"
    api_key: str = ""
    base_url: str = ""
    model: str = "gpt-4o-mini"
    temperature: float = 0.3
    max_context_chars: int = 6000


class ReplyRules(BaseModel):
    auto_send_low_risk: bool = False
    require_approval_for_price: bool = True
    require_approval_for_shipping: bool = True
    require_approval_for_distributor: bool = True
    require_approval_for_payment_terms: bool = True
    require_approval_for_delivery_time: bool = True


class WeChatConfig(BaseModel):
    provider: str = "serverchan"
    wecom_webhook_url: str = ""
    serverchan_sendkey: str = ""
    pushplus_token: str = ""


class CRMConfig(BaseModel):
    provider: str = "sqlite"
    sqlite_path: str = "./data/stargo.db"
    google_sheet_id: str = ""
    google_service_account_json: str = "service_account.json"


class RuntimeConfig(BaseModel):
    check_interval_seconds: int = 60
    screenshot_dir: str = "./data/screenshots"
    log_dir: str = "./data/logs"
    db_path: str = "./data/stargo.db"
    max_per_cycle: int = 5
    min_action_interval_seconds: int = 2


class Config(BaseModel):
    email: EmailConfig = Field(default_factory=EmailConfig)
    browser: BrowserConfig = Field(default_factory=BrowserConfig)
    knowledge: KnowledgeConfig = Field(default_factory=KnowledgeConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    reply_rules: ReplyRules = Field(default_factory=ReplyRules)
    wechat: WeChatConfig = Field(default_factory=WeChatConfig)
    crm: CRMConfig = Field(default_factory=CRMConfig)
    runtime: RuntimeConfig = Field(default_factory=RuntimeConfig)


def _expand_env(value: Any) -> Any:
    """Recursively replace ``${VAR}`` with environment values (empty if unset)."""
    if isinstance(value, str):
        return _ENV_PATTERN.sub(lambda m: os.environ.get(m.group(1), ""), value)
    if isinstance(value, dict):
        return {k: _expand_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand_env(v) for v in value]
    return value


def _default_config_path() -> Path:
    root = Path(__file__).resolve().parents[2]
    candidate = root / "config" / "config.yaml"
    if candidate.exists():
        return candidate
    return root / "config" / "config.example.yaml"


def load_config(path: str | os.PathLike[str] | None = None) -> Config:
    """Load config from YAML, expanding ``${ENV}`` after loading ``.env``."""
    if load_dotenv is not None:
        load_dotenv()

    config_path = Path(path) if path else _default_config_path()
    raw: dict[str, Any] = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as fh:
            raw = yaml.safe_load(fh) or {}
    raw = _expand_env(raw)
    return Config.model_validate(raw)
