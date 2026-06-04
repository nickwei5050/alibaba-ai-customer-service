from src.stargo.knowledge.obsidian_loader import KnowledgeDoc
from src.stargo.knowledge.retriever import Retriever


def _docs():
    return [
        KnowledgeDoc("apex", "products", "STARGO APEX electric motorcycle top speed range", "products/apex.md"),
        KnowledgeDoc("shipping", "shipping", "freight depends on destination port and quantity", "shipping/rules.md"),
        KnowledgeDoc("battery", "battery", "lithium and lead-acid battery options available", "battery/options.md"),
    ]


def test_search_ranks_relevant_doc_first():
    r = Retriever(_docs())
    results = r.search("electric motorcycle speed", top_k=3)
    assert results
    assert results[0].title == "apex"


def test_search_empty_query_returns_nothing():
    r = Retriever(_docs())
    assert r.search("", top_k=3) == []


def test_context_snippets_respects_char_budget():
    r = Retriever(_docs())
    snippet = r.context_snippets("battery options", max_chars=50)
    assert len(snippet) <= 60  # header + budget, small slack
