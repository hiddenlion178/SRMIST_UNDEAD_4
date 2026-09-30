from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.dependencies import get_engine

router = APIRouter()

class QueryRequest(BaseModel):
    session_id: str = Field(min_length=1)
    query: str = Field(min_length=1)

class Chunk(BaseModel):
    timestamp_s: float
    text: str

class StreamRequest(BaseModel):
    session_id: str = Field(min_length=1)
    chunks: list[Chunk]

class CorpusAppendRequest(BaseModel):
    records: list[dict[str, Any]]


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/v1/query")
def query(req: QueryRequest):
    engine = get_engine()
    result = engine.process_chunk(req.session_id, timestamp_s=0.0, text=req.query, is_final=True)
    return result


@router.post("/v1/stream")
def stream(req: StreamRequest):
    engine = get_engine()

    def events():
        for i, chunk in enumerate(req.chunks):
            final = i == len(req.chunks) - 1 or chunk.text.strip() == "[UTTERANCE_END]"
            if chunk.text.strip() == "[UTTERANCE_END]":
                text = ""
            else:
                text = chunk.text
            if text:
                result = engine.process_chunk(req.session_id, chunk.timestamp_s, text, is_final=final)
            else:
                result = engine.process_chunk(req.session_id, chunk.timestamp_s, "", is_final=True)
            yield f"event: state\ndata: {json.dumps(result, ensure_ascii=False)}\n\n"
            if result.get("answer"):
                for token in _tokenize(result["answer"]):
                    yield f"event: token\ndata: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")


@router.post("/v1/corpus/append")
def append_corpus(req: CorpusAppendRequest):
    # Demo-only event-driven ingestion endpoint. The core retrieval layer is rebuilt for correctness and simplicity.
    from app.core.models import CorpusChunk
    engine = get_engine()
    chunks = [
        CorpusChunk(
            doc_id=str(r["doc_id"]),
            section=str(r.get("section", "")),
            title=str(r.get("title", r["doc_id"])),
            text=str(r["text"]),
            metadata=dict(r.get("metadata", {})),
            timestamp_s=r.get("timestamp_s"),
        ) for r in req.records
    ]
    engine.retriever.add_chunks(chunks)
    engine.telemetry.emit("corpus_append", "system", count=len(chunks), sources=[f"[{c.doc_id} §{c.section}]" for c in chunks])
    return {"status": "ok", "added": len(chunks)}


def _tokenize(text: str):
    # Token-sized streaming chunks for the UI; punctuation is kept attached for readability.
    words = text.split()
    for w in words:
        yield w + " "
