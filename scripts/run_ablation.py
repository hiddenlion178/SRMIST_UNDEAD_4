from __future__ import annotations

import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.dependencies import get_engine


def eval_mode(mode: str):
    engine = get_engine()
    query = "What is the venue capacity, cancellation policy and catering options for a 30-person workshop in Pune?"
    if mode == "hybrid_vs_sparse":
        hybrid = engine.retriever.search(query, top_k=5)
        old_alpha = engine.retriever.alpha
        engine.retriever.alpha = 0.0
        sparse = engine.retriever.search(query, top_k=5)
        engine.retriever.alpha = old_alpha
        print("Hybrid top docs:", [x.chunk.doc_id for x in hybrid])
        print("Sparse top docs:", [x.chunk.doc_id for x in sparse])
        print("Hybrid scores:", [round(x.score, 3) for x in hybrid])
        print("Sparse scores:", [round(x.score, 3) for x in sparse])
    elif mode == "controller_vs_always_retrieve":
        engine.process_chunk("ablation", 0.0, "Summarize the travel reimbursement rule", is_final=True)
        r = engine.process_chunk("ablation", 0.2, "Actually make it shorter", is_final=True)
        print("Controller decision:", r["decision"])
        print("Retrieval suppressed:", r["decision"]["decision"] == "NO_RETRIEVAL")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=["hybrid_vs_sparse", "controller_vs_always_retrieve"])
    args = parser.parse_args()
    eval_mode(args.mode)
