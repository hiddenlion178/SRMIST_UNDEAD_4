from __future__ import annotations

import re
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Iterator

from .controller import RetrievalController
from .decomposer import MultiIntentDecomposer
from .fusion import fuse
from .grounding import citation_for, support_ratio
from .models import CorpusChunk, RetrievalDecision, SessionState
from .retrieval import HybridRetriever
from .session import SessionStore
from .synthesizer import Synthesizer
from .telemetry import Telemetry


class StreamingRAGEngine:
    def __init__(self, retriever: HybridRetriever, telemetry: Telemetry):
        self.retriever = retriever
        self.telemetry = telemetry
        self.controller = RetrievalController()
        self.decomposer = MultiIntentDecomposer()
        self.sessions = SessionStore()
        self.synthesizer = Synthesizer()

    def process_chunk(self, session_id: str, timestamp_s: float, text: str, is_final: bool = False) -> dict[str, Any]:
        state = self.sessions.get(session_id)
        state.transcript.append({"timestamp_s": timestamp_s, "text": text})
        decision = self.controller.decide(text, state, is_final=is_final)
        state.last_decision = decision
        self.telemetry.emit(
            "retrieval_decision",
            session_id,
            timestamp_s=timestamp_s,
            decision=decision.decision,
            reason=decision.reason,
            trigger=decision.trigger,
            confidence=decision.confidence,
        )

        if decision.decision == "WAIT":
            return self._result(state, decision, [], [], "")

        if decision.decision == "NO_RETRIEVAL":
            answer = self._reformat_previous(state.answer.answer, text)
            state.answer.version += 1
            state.answer.answer = answer
            self.telemetry.emit(
                "answer_update",
                session_id,
                answer_version=state.answer.version,
                mode="suppression",
                citations=state.answer.citations,
            )
            return self._result(state, decision, [], [], answer)

        # RETRIEVE path
        full_context = " ".join(x["text"] for x in state.transcript)
        query = text if decision.trigger == "late_refinement" else full_context
        subqueries = self.decomposer.decompose(query)
        self.telemetry.emit(
            "decomposition",
            session_id,
            timestamp_s=timestamp_s,
            subqueries=subqueries,
            trigger=decision.trigger,
        )

        started = time.perf_counter()
        with ThreadPoolExecutor(max_workers=min(4, len(subqueries))) as pool:
            futures = [pool.submit(self.retriever.search, q, 6) for q in subqueries]
            results = [f.result() for f in futures]
        latency_ms = round((time.perf_counter() - started) * 1000, 2)

        fused = fuse(results, top_k=6)
        evidence = [r.chunk for r in fused]
        self.telemetry.emit(
            "retrieval_complete",
            session_id,
            timestamp_s=timestamp_s,
            query=query,
            subquery_count=len(subqueries),
            result_count=len(fused),
            latency_ms=latency_ms,
            sources=[citation_for(c) for c in evidence],
        )

        if decision.trigger == "late_refinement" and state.answer.evidence:
            # Merge only delta evidence into existing evidence, rather than restarting full corpus retrieval.
            merged = {citation_for(c): c for c in state.answer.evidence}
            for c in evidence:
                merged[citation_for(c)] = c
            evidence = list(merged.values())[:8]

        refinement = decision.trigger == "late_refinement" and bool(state.answer.answer)
        answer, citations = self.synthesizer.answer(query, evidence, previous_answer=state.answer.answer, refinement=refinement)
        state.answer.version += 1
        state.answer.answer = answer
        state.answer.citations = citations
        state.answer.evidence = evidence
        state.answer.query = query
        state.last_query = query

        support = support_ratio(citations, evidence)
        self.telemetry.emit(
            "answer_update",
            session_id,
            answer_version=state.answer.version,
            mode="refinement" if refinement else "initial_retrieval",
            citations=citations,
            citation_support_ratio=round(support, 3),
        )
        return self._result(state, decision, subqueries, evidence, answer, latency_ms=latency_ms)

    def _result(self, state: SessionState, decision: RetrievalDecision, subqueries, evidence, answer, latency_ms: float | None = None):
        return {
            "session_id": state.session_id,
            "decision": {
                "decision": decision.decision,
                "reason": decision.reason,
                "trigger": decision.trigger,
                "confidence": decision.confidence,
            },
            "sub_queries": subqueries,
            "answer": answer,
            "answer_version": state.answer.version,
            "citations": state.answer.citations,
            "retrieved": [
                {
                    "doc_id": x.doc_id,
                    "section": x.section,
                    "title": x.title,
                    "text": x.text,
                } for x in evidence
            ],
            "latency_ms": latency_ms,
        }

    @staticmethod
    def _reformat_previous(answer: str, instruction: str) -> str:
        if not answer:
            return "There is no previous answer to reformat yet."
        low = instruction.lower()
        if "bullet" in low:
            pieces = [p.strip() for p in re.split(r"(?<=[.!?])\s+", answer) if p.strip()]
            return "\n".join(f"- {p}" for p in pieces[:6])
        if "shorter" in low or "concise" in low or "shorten" in low:
            pieces = [p.strip() for p in re.split(r"(?<=[.!?])\s+", answer) if p.strip()]
            return " ".join(pieces[:2])
        if "table" in low:
            return "| Evidence |\n|---|\n| " + answer.replace("\n", " ") + " |"
        return answer
