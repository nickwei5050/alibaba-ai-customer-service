"""Low-level WeChat push providers: WeCom robot, ServerChan, PushPlus.

Thin HTTP wrappers; the :class:`~stargo.boundary.notifier_wechat.WeChatNotifier`
dispatcher chooses among them based on config.
"""

from __future__ import annotations

import requests


def send_wecom_message(webhook_url: str, content: str, timeout: int = 10) -> dict:
    """Send a Markdown message to a WeCom (企业微信) group robot."""
    payload = {"msgtype": "markdown", "markdown": {"content": content}}
    resp = requests.post(webhook_url, json=payload, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def send_serverchan(sendkey: str, title: str, desp: str, timeout: int = 10) -> dict:
    """Push a message to personal WeChat via ServerChan (Server酱) SendKey."""
    url = f"https://sctapi.ftqq.com/{sendkey}.send"
    resp = requests.post(url, data={"title": title, "desp": desp}, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def send_pushplus(token: str, title: str, content: str, timeout: int = 10) -> dict:
    """Push a Markdown message via PushPlus (WeChat / WeCom / email / DingTalk)."""
    url = "https://www.pushplus.plus/send"
    payload = {"token": token, "title": title, "content": content, "template": "markdown"}
    resp = requests.post(url, json=payload, timeout=timeout)
    resp.raise_for_status()
    return resp.json()
