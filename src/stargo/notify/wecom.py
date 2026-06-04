"""WeCom (企业微信) group robot webhook notifications."""

from __future__ import annotations

import requests


def send_wecom_message(webhook_url: str, content: str, timeout: int = 10) -> dict:
    """Send a Markdown message to a WeCom group robot."""
    payload = {"msgtype": "markdown", "markdown": {"content": content}}
    resp = requests.post(webhook_url, json=payload, timeout=timeout)
    resp.raise_for_status()
    return resp.json()
