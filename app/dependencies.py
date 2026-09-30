from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv

from .core.corpus import load_jsonl
from .core.engine import StreamingRAGEngine
from .core.retrieval import HybridRetriever
from .core.telemetry import Telemetry

load_dotenv()

@lru_cache(maxsize=1)
def get_engine() -> StreamingRAGEngine:
    corpus_path = os.getenv("CORPUS_PATH", "data/sample_corpus.jsonl")
    alpha = float(os.getenv("HYBRID_ALPHA", "0.65"))
    lsa_components = int(os.getenv("LSA_COMPONENTS", "64"))
    chunks = load_jsonl(corpus_path)
    retriever = HybridRetriever(chunks, alpha=alpha, lsa_components=lsa_components)
    telemetry = Telemetry(os.getenv("TELEMETRY_PATH", "artifacts/telemetry.jsonl"))
    return StreamingRAGEngine(retriever, telemetry)
