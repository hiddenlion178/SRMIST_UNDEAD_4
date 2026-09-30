from __future__ import annotations

import re
from .models import RetrievalDecision, SessionState

FORMAT_ONLY_PATTERNS = [
    r"\brepeat\b.*\banswer\b",
    r"\bmake (it|this) (shorter|concise)\b",
    r"\bshorten\b",
    r"\bsummarize (the )?(last|previous) answer\b",
    r"\bput (it|that) in (a )?(table|bullets|bullet points)\b",
    r"\bconvert (it|that) to\b",
    r"\brephrase\b",
    r"\bsimplify\b",
    r"\bchange the format\b",
]

LATE_PATTERNS = [
    r"\bactually\b",
    r"\binstead\b",
    r"\bexcept\b",
    r"\bonly if\b",
    r"\bafter\b",
    r"\bbefore\b",
    r"\binternational\b",
    r"\blate[- ]booking\b",
    r"\bpost[- ]travel\b",
    r"\bchanged? to\b",
]

SEARCH_HINTS = [
    "capacity", "people", "attendees", "venue", "cancel", "refund", "catering",
    "food", "travel", "reimbursement", "booking", "international", "policy", "price",
    "cost", "availability", "exception", "approval", "rules", "deadline", "support",
]


def _looks_like_late_constraint(text: str) -> bool:
    low = text.lower()
    return any(re.search(p, low) for p in LATE_PATTERNS)


def _is_format_only(text: str) -> bool:
    low = text.lower().strip()
    return any(re.search(p, low) for p in FORMAT_ONLY_PATTERNS)


class RetrievalController:
    def decide(self, text: str, state: SessionState, is_final: bool = False) -> RetrievalDecision:
        clean = text.strip()
        if not clean:
            return RetrievalDecision("WAIT", "empty_chunk", "incremental", 1.0)

        if _is_format_only(clean) and state.answer.answer:
            return RetrievalDecision("NO_RETRIEVAL", "presentation_restructure", "suppression", 0.97)

        if state.answer.answer and _looks_like_late_constraint(clean):
            return RetrievalDecision("RETRIEVE", "late_constraint", "late_refinement", 0.92)

        words = re.findall(r"\b\w+\b", clean.lower())
        hint_count = sum(1 for w in words if w in SEARCH_HINTS)
        has_question = any(x in clean.lower() for x in ["what", "how", "where", "when", "which", "can", "does", "do", "is", "are", "need"])
        if len(words) < 5 and not is_final:
            return RetrievalDecision("WAIT", "insufficient_semantic_stability", "incremental", 0.92)

        if hint_count >= 1 or has_question or is_final:
            trigger = "provisional" if not is_final else "utterance_end"
            return RetrievalDecision("RETRIEVE", "stable_search_intent", trigger, min(0.95, 0.55 + 0.08 * hint_count))

        return RetrievalDecision("WAIT", "no_stable_retrieval_intent", "incremental", 0.78)
