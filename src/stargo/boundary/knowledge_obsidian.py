"""Load a local Obsidian (Markdown) vault into knowledge documents."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeDoc:
    """One unit of retrievable knowledge."""

    title: str
    category: str
    text: str
    source: str
    tags: list[str] = field(default_factory=list)
    # Operator-only docs (e.g. internal cost prices). Searchable by the operator
    # via ``kb-search``, but NEVER injected into the buyer-facing AI prompt.
    internal_only: bool = False


def load_obsidian(vault_path: str) -> list[KnowledgeDoc]:
    """Recursively load every ``.md`` file under ``vault_path``.

    The first path segment under the vault is used as the category (e.g.
    ``products/apex.md`` -> category ``products``), matching the recommended
    folder layout (company / products / prices / battery / shipping / sample /
    distributor / faq / rules / scripts).
    """
    root = Path(vault_path).expanduser()
    if not root.exists():
        logger.warning("Obsidian vault not found at %s", root)
        return []

    docs: list[KnowledgeDoc] = []
    for md in sorted(root.rglob("*.md")):
        try:
            text = md.read_text(encoding="utf-8", errors="replace").strip()
        except OSError as exc:  # pragma: no cover - defensive
            logger.warning("Could not read %s: %s", md, exc)
            continue
        if not text:
            continue
        rel = md.relative_to(root)
        category = rel.parts[0] if len(rel.parts) > 1 else "general"
        parts = [p.lower() for p in rel.parts]
        stem = md.stem.lower()
        head = text[:400].lower()
        head_raw = text[:400]
        internal_only = (
            any(p.startswith("internal") or p.startswith("cost") for p in parts)
            or stem.startswith("internal")
            or stem.startswith("cost")
            or "do_not_index" in head
            or "internal_only" in head
            or "严禁对客" in head_raw
            or "禁止对客" in head_raw
        )
        docs.append(
            KnowledgeDoc(
                title=md.stem,
                category=category,
                text=text,
                source=str(rel),
                internal_only=internal_only,
            )
        )
    logger.info("Loaded %d Obsidian docs from %s", len(docs), root)
    return docs
