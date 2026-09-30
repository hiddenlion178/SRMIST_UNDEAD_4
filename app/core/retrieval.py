from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Iterable

import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .models import CorpusChunk, RetrievedChunk


def _normalize(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    if len(values) == 0:
        return values
    lo, hi = float(values.min()), float(values.max())
    if hi - lo < 1e-12:
        return np.ones_like(values) * 0.5
    return (values - lo) / (hi - lo)


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9]+", text.lower()))


class HybridRetriever:
    """Dense + sparse retriever.

    Default dense backend is an LSA projection because it is fully offline and reproducible.
    The project can be extended with SentenceTransformer embeddings without changing the API.
    """

    def __init__(self, chunks: list[CorpusChunk], alpha: float = 0.65, lsa_components: int = 64):
        self.chunks = chunks
        self.alpha = float(alpha)
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            min_df=1,
            max_df=0.98,
            stop_words="english",
        )
        sparse = self.vectorizer.fit_transform([c.text for c in chunks])
        self.sparse_matrix = sparse
        k = max(2, min(lsa_components, sparse.shape[1] - 1 if sparse.shape[1] > 2 else 2))
        if sparse.shape[0] <= 2 or sparse.shape[1] <= 2:
            self.svd = None
            self.dense_matrix = sparse.toarray().astype(np.float32)
        else:
            self.svd = TruncatedSVD(n_components=k, random_state=42)
            self.dense_matrix = self.svd.fit_transform(sparse)

    def add_chunks(self, chunks: Iterable[CorpusChunk]) -> None:
        # Refit for simple local-demo ingestion. Production integration can use an incremental vector DB.
        self.chunks = list(self.chunks) + list(chunks)
        self.__init__(self.chunks, alpha=self.alpha)

    def search(self, query: str, top_k: int = 6) -> list[RetrievedChunk]:
        if not query.strip():
            return []
        q_sparse = self.vectorizer.transform([query])
        sparse_scores = cosine_similarity(q_sparse, self.sparse_matrix)[0]
        if self.svd is not None:
            q_dense = self.svd.transform(q_sparse)
            dense_scores = cosine_similarity(q_dense, self.dense_matrix)[0]
        else:
            dense_scores = sparse_scores.copy()

        sparse_n = _normalize(sparse_scores)
        dense_n = _normalize(dense_scores)
        combined = self.alpha * dense_n + (1.0 - self.alpha) * sparse_n

        candidates = []
        for idx in np.argsort(combined)[::-1]:
            chunk = self.chunks[int(idx)]
            # Small freshness bonus if a source carries a numeric event timestamp.
            freshness_bonus = 0.0
            ts = chunk.timestamp_s
            if ts is not None:
                freshness_bonus = 0.02 / (1.0 + max(0.0, 10.0 - float(ts)))
            score = float(combined[idx] + freshness_bonus)
            candidates.append(
                RetrievedChunk(
                    chunk=chunk,
                    score=score,
                    dense_score=float(dense_n[idx]),
                    sparse_score=float(sparse_n[idx]),
                )
            )

        # Lightweight lexical rerank around the query terms.
        q_terms = _tokens(query)
        for item in candidates:
            overlap = len(q_terms & _tokens(item.chunk.text)) / max(1, len(q_terms))
            item.score += 0.08 * overlap

        candidates.sort(key=lambda x: x.score, reverse=True)

        # Deduplicate near-identical evidence.
        selected: list[RetrievedChunk] = []
        selected_tokens: list[set[str]] = []
        for item in candidates:
            toks = _tokens(item.chunk.text)
            duplicate = False
            for prev in selected_tokens:
                jacc = len(toks & prev) / max(1, len(toks | prev))
                if jacc > 0.82:
                    duplicate = True
                    break
            if duplicate:
                continue
            selected.append(item)
            selected_tokens.append(toks)
            if len(selected) >= top_k:
                break
        return selected
