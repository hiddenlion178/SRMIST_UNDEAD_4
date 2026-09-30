from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Decision = Literal["WAIT", "RETRIEVE", "NO_RETRIEVAL"]

@dataclass
class CorpusChunk:
    doc_id: str
    section: str
    title: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp_s: float | None = None

@dataclass
class RetrievedChunk:
    chunk: CorpusChunk
    score: float
    dense_score: float
    sparse_score: float

@dataclass
class RetrievalDecision:
    decision: Decision
    reason: str
    trigger: str
    confidence: float

@dataclass
class Evidence:
    chunk: RetrievedChunk
    citation: str

@dataclass
class AnswerState:
    version: int = 0
    answer: str = ""
    citations: list[str] = field(default_factory=list)
    evidence: list[CorpusChunk] = field(default_factory=list)
    query: str = ""

@dataclass
class SessionState:
    session_id: str
    transcript: list[dict[str, Any]] = field(default_factory=list)
    last_query: str = ""
    answer: AnswerState = field(default_factory=AnswerState)
    constraints: dict[str, Any] = field(default_factory=dict)
    last_decision: RetrievalDecision | None = None
