"""Optional Notion knowledge sync.

Only used when ``knowledge.notion_enabled`` is true and ``NOTION_API_KEY`` is
set. Imports of ``notion_client`` are lazy so the rest of the system runs
without the dependency installed.
"""

from __future__ import annotations

import logging
from typing import Any

from .knowledge_obsidian import KnowledgeDoc

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


def _prop_text(prop: dict[str, Any]) -> str:
    """Flatten a single Notion page property value to plain text."""
    ptype = prop.get("type", "")
    if ptype == "title":
        return _rich_text(prop.get("title", []))
    if ptype == "rich_text":
        return _rich_text(prop.get("rich_text", []))
    if ptype == "select":
        return (prop.get("select") or {}).get("name", "")
    if ptype == "multi_select":
        return ", ".join(o.get("name", "") for o in prop.get("multi_select", []))
    if ptype == "number":
        n = prop.get("number")
        return "" if n is None else str(n)
    if ptype == "status":
        return (prop.get("status") or {}).get("name", "")
    return ""


def load_notion_catalog(api_key: str, database_id: str) -> list[KnowledgeDoc]:
    """Load a structured product-catalog database (one KnowledgeDoc per model).

    Reads every row's properties (Model / 中文名 / Series / Wheels / Voltage /
    Motor / Range / Top Speed / Load / Markets / Status), so the retriever can
    answer per-model spec questions for all rows in the catalog.
    """
    if not api_key or not database_id:
        return []
    try:
        from notion_client import Client  # type: ignore
    except ImportError:
        logger.warning("notion-client not installed; skipping Notion catalog sync.")
        return []

    client = Client(auth=api_key)
    docs: list[KnowledgeDoc] = []
    try:
        cursor: str | None = None
        while True:
            resp = client.databases.query(database_id=database_id, start_cursor=cursor)
            for row in resp.get("results", []):
                props = row.get("properties", {})
                fields = {name: _prop_text(p) for name, p in props.items()}
                title = next(
                    (v for n, v in fields.items() if props.get(n, {}).get("type") == "title"),
                    "",
                )
                if not (title or any(fields.values())):
                    continue
                text = " | ".join(f"{n}: {v}" for n, v in fields.items() if v)
                docs.append(
                    KnowledgeDoc(
                        title=title or row.get("id", ""),
                        category="products",
                        text=text,
                        source=f"notion-catalog:{row.get('id', '')}",
                    )
                )
            if not resp.get("has_more"):
                break
            cursor = resp.get("next_cursor")
    except Exception as exc:  # pragma: no cover - network/permission errors
        logger.warning("Notion catalog sync failed: %s", exc)
    logger.info("Loaded %d Notion catalog rows", len(docs))
    return docs
