"""Document retrieval tool for the RAG agent."""
from __future__ import annotations

from oracle.config import get_settings
from oracle.rag import store


def search_documents(query: str) -> dict:
    """Search the company documents (policies, data dictionary) for passages relevant to a query.

    Args:
        query: A natural-language search query.

    Returns:
        A dict with status and a list of results, each with source, chunk_id, score and text.
    """
    cfg = get_settings()
    try:
        results = store.search(query, k=cfg.top_k)
    except FileNotFoundError:
        return {"status": "error", "error": "Document index not built. Run: make ingest"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error": str(exc)}
    return {"status": "ok", "results": results}
