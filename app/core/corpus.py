from __future__ import annotations

import json
from pathlib import Path
from .models import CorpusChunk


def load_jsonl(path: str | Path) -> list[CorpusChunk]:
    chunks: list[CorpusChunk] = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            chunks.append(
                CorpusChunk(
                    doc_id=str(obj["doc_id"]),
                    section=str(obj.get("section", "")),
                    title=str(obj.get("title", obj["doc_id"])),
                    text=str(obj["text"]),
                    metadata=dict(obj.get("metadata", {})),
                    timestamp_s=obj.get("timestamp_s"),
                )
            )
    if not chunks:
        raise ValueError(f"Corpus is empty: {path}")
    return chunks
