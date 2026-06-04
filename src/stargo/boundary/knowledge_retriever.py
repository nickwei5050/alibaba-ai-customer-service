"""A small dependency-free retriever over the knowledge docs.

Uses TF-style keyword overlap scoring. It is intentionally simple and offline;
swap in embeddings later without changing the call sites.
"""

from __future__ import annotations

import logging
import math
import re
from collections import Counter

from ..config import KnowledgeConfig
from .knowledge_obsidian import KnowledgeDoc, load_obsidian
from .knowledge_notion import load_notion, load_notion_catalog

logger = logging.getLogger(__name__)

_TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)
_STOP = {
    "the", "a", "an", "to", "of", "and", "or", "for", "is", "are", "in", "on",
    "we", "you", "your", "our", "with", "can", "please", "would", "could",
    "hi", "hello", "dear", "thanks", "thank",
}


def _tokens(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text or "") if t.lower() not in _STOP]


class Retriever:
    def __init__(self, docs: list[KnowledgeDoc]) -> None:
        self.docs = docs
        self._doc_tokens = [Counter(_tokens(d.text)) for d in docs]
        # Inverse document frequency for discriminative weighting.
        n = max(len(docs), 1)
        df: Counter[str] = Counter()
        for tc in self._doc_tokens:
            df.update(tc.keys())
        self._idf = {term: math.log(1 + n / (1 + freq)) for term, freq in df.items()}

    @classmethod
    def from_config(cls, cfg: KnowledgeConfig) -> "Retriever":
        docs = load_obsidian(cfg.obsidian_path)
        if cfg.notion_enabled:
            docs += load_notion(cfg.notion_api_key, cfg.notion_database_id)
            docs += load_notion_catalog(cfg.notion_api_key, cfg.notion_catalog_database_id)
        return cls(docs)

    def _score(self, query_tokens: Counter[str], idx: int) -> float:
        doc = self._doc_tokens[idx]
        if not doc:
            return 0.0
        score = 0.0
        for term, qcount in query_tokens.items():
            if term in doc:
                score += qcount * doc[term] * self._idf.get(term, 1.0)
        return score / math.sqrt(sum(doc.values()))

    def search(self, query: str, top_k: int = 5) -> list[KnowledgeDoc]:
        if not self.docs:
            return []
        qt = Counter(_tokens(query))
        if not qt:
            return []
        ranked = sorted(
            range(len(self.docs)),
            key=lambda i: self._score(qt, i),
            reverse=True,
        )
        results = [self.docs[i] for i in ranked if self._score(qt, i) > 0]
        return results[:top_k]

    def context_snippets(self, query: str, max_chars: int, top_k: int = 5) -> str:
        """Concatenate top docs into a budgeted context block for the prompt.

        Internal-only docs (e.g. internal cost prices) are skipped here so they
        can never leak into a buyer-facing reply. Fetch extra candidates to
        backfill the slots dropped by the filter.
        """
        chunks: list[str] = []
        used = 0
        candidates = [d for d in self.search(query, top_k=top_k * 3) if not d.internal_only]
        for doc in candidates[:top_k]:
            header = f"### [{doc.category}] {doc.title}\n"
            body = doc.text.strip()
            piece = header + body
            if used + len(piece) > max_chars:
                piece = piece[: max(0, max_chars - used)]
            if not piece:
                break
            chunks.append(piece)
            used += len(piece)
            if used >= max_chars:
                break
        return "\n\n".join(chunks)
