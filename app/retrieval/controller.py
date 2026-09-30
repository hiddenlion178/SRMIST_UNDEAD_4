"""Retrieval layer for the Streaming Live RAG demo."""

from typing import Any


async def retrieve(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Return demo evidence.

    Replace this function with the project's live search/vector/database
    retrieval implementation when connecting real data sources.
    """
    top_k = max(1, top_k)
    return [
        {
            "id": "demo-1",
            "title": "Demo live source",
            "content": f"Demo evidence retrieved for: {query}",
            "score": 1.0,
            "freshness": "demo",
        }
    ][:top_k]
