"""PushPlus push to WeChat / WeCom / email / DingTalk / Feishu."""

from __future__ import annotations

import requests


def send_pushplus(token: str, title: str, content: str, timeout: int = 10) -> dict:
    """Push a Markdown message via PushPlus."""
    url = "https://www.pushplus.plus/send"
    payload = {
        "token": token,
        "title": title,
        "content": content,
        "template": "markdown",
    }
    resp = requests.post(url, json=payload, timeout=timeout)
    resp.raise_for_status()
    return resp.json()
