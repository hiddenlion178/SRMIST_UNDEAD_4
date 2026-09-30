from pathlib import Path
from app.core.corpus import load_jsonl
from app.core.retrieval import HybridRetriever


def test_hybrid_retrieval():
    chunks = load_jsonl(Path("data/sample_corpus.jsonl"))
    r = HybridRetriever(chunks)
    hits = r.search("venue capacity for 30 attendees in Pune", top_k=3)
    assert hits
    assert hits[0].chunk.doc_id in {"Doc_01", "Doc_14", "Doc_04"}
