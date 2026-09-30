from __future__ import annotations

import re

INTENT_HINTS = {
    "capacity": ["capacity", "people", "attendees", "seats", "room size"],
    "cancellation": ["cancel", "cancellation", "refund", "refund policy"],
    "catering": ["catering", "food", "meals", "refreshments", "menu"],
    "travel": ["travel", "reimbursement", "expense", "trip"],
    "international": ["international", "foreign currency", "abroad"],
    "late_booking": ["late booking", "after travel", "post-travel", "senior director approval"],
    "availability": ["availability", "available", "open", "slot"],
    "cost": ["cost", "price", "pricing", "budget", "fee"],
}


def _intent_label(text: str) -> str | None:
    low = text.lower()
    for label, hints in INTENT_HINTS.items():
        if any(h in low for h in hints):
            return label
    return None


class MultiIntentDecomposer:
    def decompose(self, utterance: str) -> list[str]:
        text = utterance.strip()
        # Preserve the full query as the fallback because over-splitting is a core pitfall.
        labels = []
        for label in INTENT_HINTS:
            if _intent_label_for_label(text, label):
                labels.append(label)

        if len(set(labels)) <= 1:
            return [text]

        # Keep a shared topic prefix and generate concise search-ready queries.
        topic = ""
        m = re.search(r"(?:for|about|regarding) (.{0,90})", text, flags=re.I)
        if m:
            topic = m.group(1).strip(" .,")

        queries = []
        for label in labels:
            queries.append(self._build_query(label, text, topic))
        return _unique(queries)

    def _build_query(self, label: str, original: str, topic: str) -> str:
        mapping = {
            "capacity": "venue capacity and attendee limit",
            "cancellation": "cancellation terms and refund policy",
            "catering": "catering options and food service policy",
            "travel": "travel reimbursement policy",
            "international": "international travel reimbursement exception",
            "late_booking": "late booking exception and approval",
            "availability": "venue availability or slot availability",
            "cost": "cost pricing fee budget",
        }
        q = mapping[label]
        if topic:
            return f"{q} — {topic}"
        return q


def _intent_label_for_label(text: str, label: str) -> bool:
    low = text.lower()
    return any(h in low for h in INTENT_HINTS[label])


def _unique(items: list[str]) -> list[str]:
    out=[]
    seen=set()
    for x in items:
        k=re.sub(r"\W+", " ", x.lower()).strip()
        if k not in seen:
            seen.add(k); out.append(x)
    return out
