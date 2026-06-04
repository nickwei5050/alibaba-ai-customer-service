"""Optional Notion knowledge sync.

Only used when ``knowledge.notion_enabled`` is true and ``NOTION_API_KEY`` is
set. Imports of ``notion_client`` are lazy so the rest of the system runs
without the dependency installed.
"""

from __future__ import annotations

import logging
from typing import Any

from .obsidian_loader import KnowledgeDoc

logger = logging.getLogger(__name__)


def _rich_text(blocks: list[dict[str, Any]]) -> str:
    return "".join(b.get("plain_text", "") for b in blocks or [])


def _page_to_text(client: Any, page_id: str) -> str:
    """Flatten a page's top-level blocks into plain text (best-effort)."""
    parts: list[str] = []
    cursor: str | None = None
    while True:
        resp = client.blocks.children.list(block_id=page_id, start_cursor=cursor)
        for block in resp.get("results", []):
            btype = block.get("type", "")
            content = block.get(btype, {})
            text = _rich_text(content.get("rich_text", []))
            if text:
                parts.append(text)
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return "\n".join(parts)


def load_notion(api_key: str, database_id: str) -> list[KnowledgeDoc]:
    if not api_key or not database_id:
        return []
    try:
        from notion_client import Client  # type: ignore
    except ImportError:
        logger.warning("notion-client not installed; skipping Notion sync.")
        return []

    client = Client(auth=api_key)
    docs: list[KnowledgeDoc] = []
    try:
        cursor: str | None = None
        while True:
            resp = client.databases.query(database_id=database_id, start_cursor=cursor)
            for page in resp.get("results", []):
                props = page.get("properties", {})
                title = ""
                category = "notion"
                for name, prop in props.items():
                    if prop.get("type") == "title":
                        title = _rich_text(prop.get("title", []))
                    if name.lower() in ("category", "type") and prop.get("type") == "select":
                        sel = prop.get("select") or {}
                        category = sel.get("name", category)
                body = _page_to_text(client, page["id"])
                if title or body:
                    docs.append(
                        KnowledgeDoc(
                            title=title or page["id"],
                            category=category,
                            text=f"{title}\n{body}".strip(),
                            source=f"notion:{page['id']}",
                        )
                    )
            if not resp.get("has_more"):
                break
            cursor = resp.get("next_cursor")
    except Exception as exc:  # pragma: no cover - network/permission errors
        logger.warning("Notion sync failed: %s", exc)
    logger.info("Loaded %d Notion docs", len(docs))
    return docs
