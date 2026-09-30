from __future__ import annotations

import re
from .models import CorpusChunk


def citation_for(chunk: CorpusChunk) -> str:
    return f"[{chunk.doc_id} §{chunk.section}]"


def verify_citations(answer: str, allowed: set[str]) -> list[str]:
    found = re.findall(r"\[([^\]]+?)\]", answer)
    invalid=[]
    for f in found:
        token=f"[{f}]"
        if token not in allowed:
            invalid.append(token)
    return invalid


def support_ratio(citations: list[str], evidence: list[CorpusChunk]) -> float:
    if not citations:
        return 0.0 if evidence else 1.0
    allowed = {citation_for(c) for c in evidence}
    valid = sum(1 for c in citations if c in allowed)
    return valid / len(citations)
