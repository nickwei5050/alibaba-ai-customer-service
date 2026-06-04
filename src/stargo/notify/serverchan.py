"""ServerChan (Server酱) push to personal WeChat."""

from __future__ import annotations

import requests


def send_serverchan(sendkey: str, title: str, desp: str, timeout: int = 10) -> dict:
    """Push a message to personal WeChat via ServerChan SendKey."""
    url = f"https://sctapi.ftqq.com/{sendkey}.send"
    resp = requests.post(url, data={"title": title, "desp": desp}, timeout=timeout)
    resp.raise_for_status()
    return resp.json()
