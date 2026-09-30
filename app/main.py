"""FastAPI entry point for the Streaming Live RAG demo."""

import json

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.retrieval.controller import retrieve
from app.synthesis.generator import synthesize
from app.telemetry.metrics import Timer

app = FastAPI(title="SRMIST_UNDEAD_4 - Streaming Live RAG", version="1.0.0")


class QueryRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/query")
async def query(request: QueryRequest) -> StreamingResponse:
    timer = Timer()

    async def event_stream():
        yield f"data: {json.dumps({'type': 'status', 'message': 'retrieving'})}\n\n"

        evidence = await retrieve(request.query, request.top_k)
        yield f"data: {json.dumps({'type': 'evidence', 'items': evidence})}\n\n"

        yield f"data: {json.dumps({'type': 'status', 'message': 'synthesizing'})}\n\n"
        answer = await synthesize(request.query, evidence)
        yield f"data: {json.dumps({'type': 'answer', 'text': answer})}\n\n"

        yield f"data: {json.dumps({'type': 'telemetry', 'elapsed_ms': round(timer.elapsed_ms, 2)})}\n\n"
        yield "data: {"type":"done"}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
