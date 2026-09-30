from __future__ import annotations

from .models import RetrievedChunk


def fuse(results: list[list[RetrievedChunk]], top_k: int = 6) -> list[RetrievedChunk]:
    """Merge evidence across subqueries; retain strongest score per source and reward coverage."""
    by_id: dict[tuple[str, str], RetrievedChunk] = {}
    coverage: dict[tuple[str, str], int] = {}
    for group in results:
        seen_group = set()
        for item in group:
            key = (item.chunk.doc_id, item.chunk.section)
            if key in seen_group:
                continue
            seen_group.add(key)
            coverage[key] = coverage.get(key, 0) + 1
            existing = by_id.get(key)
            if existing is None or item.score > existing.score:
                by_id[key] = item

    fused=[]
    for key, item in by_id.items():
        item.score += 0.04 * max(0, coverage.get(key, 1) - 1)
        fused.append(item)
    fused.sort(key=lambda x: x.score, reverse=True)
    return fused[:top_k]
