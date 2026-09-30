from __future__ import annotations

import os
import re
from typing import Iterable

from .grounding import citation_for
from .models import CorpusChunk


class Synthesizer:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "none").lower()
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.api_key = os.getenv("GEMINI_API_KEY")
        self._gemini = None
        if self.provider == "gemini" and self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._gemini = genai.GenerativeModel(self.model)
            except Exception:
                self._gemini = None

    def answer(self, query: str, evidence: list[CorpusChunk], previous_answer: str = "", refinement: bool = False) -> tuple[str, list[str]]:
        citations = [citation_for(c) for c in evidence]
        if not evidence:
            return (
                "I could not verify this from the supplied corpus. Please provide a more specific question or a corpus entry that contains the needed fact.",
                [],
            )

        if self._gemini is not None:
            prompt = self._prompt(query, evidence, previous_answer, refinement)
            try:
                response = self._gemini.generate_content(prompt)
                text = (getattr(response, "text", "") or "").strip()
                if text:
                    # Citations are appended from verified retrieval evidence rather than trusted from the model.
                    text = self._strip_model_citations(text)
                    text += "\n\nSources: " + " ".join(citations)
                    return text, citations
            except Exception:
                pass

        return self._deterministic_answer(query, evidence, previous_answer, refinement), citations

    def _prompt(self, query: str, evidence: list[CorpusChunk], previous_answer: str, refinement: bool) -> str:
        snippets = "\n".join(
            f"SOURCE {citation_for(c)}\n{c.text}" for c in evidence
        )
        mode = "Update only the claims affected by the new constraint; preserve unaffected facts." if refinement else "Answer the user's question directly."
        return f"""
You are a grounded RAG synthesizer. {mode}
Use ONLY the evidence below. Do not introduce facts not present in the evidence.
When evidence is incomplete, say so explicitly.
Do not invent citations or URLs.

QUESTION:
{query}

PREVIOUS ANSWER:
{previous_answer}

EVIDENCE:
{snippets}
""".strip()

    @staticmethod
    def _strip_model_citations(text: str) -> str:
        # Keep prose clean; verified citations are appended by this application.
        return re.sub(r"\[[^\]]+\]", "", text).strip()

    @staticmethod
    def _deterministic_answer(query: str, evidence: list[CorpusChunk], previous_answer: str, refinement: bool) -> str:
        # The fallback is intentionally conservative and corpus-grounded.
        sentences=[]
        query_terms = set(re.findall(r"[a-zA-Z0-9]+", query.lower()))
        for chunk in evidence[:5]:
            text = re.sub(r"\s+", " ", chunk.text).strip()
            if not text:
                continue
            # Prefer a sentence with lexical overlap; otherwise take the first sentence.
            candidates = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
            chosen = max(candidates[:4] or [text], key=lambda s: len(query_terms & set(re.findall(r"[a-zA-Z0-9]+", s.lower()))))
            sentences.append(f"{chosen} {citation_for(chunk)}")
        prefix = "Updated answer: " if refinement else "Based on the supplied corpus: "
        return prefix + " ".join(sentences)
