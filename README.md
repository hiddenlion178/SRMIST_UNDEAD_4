# SRMIST_UNDEAD_4 — Streaming Live RAG

Samsung PRISM GenAI Hackathon 3.0 — Theme 4

**Team:** UNDEAD  
**College:** SRM Institute of Science and Technology  
**Members:**
- KA Mohammed Ziyan — RA2411026010528
- Subham Sankhala — RA2411031010082

## What this project implements

This repository is a complete reference implementation of the Theme 4 requirements described in the supplied Samsung **Streaming Live RAG** guide:

- Incremental transcript processing
- Retrieval Controller: `WAIT | RETRIEVE | NO_RETRIEVAL`
- Multi-intent decomposition and parallel sub-query retrieval
- Hybrid corpus retrieval with dense + sparse scoring
- Evidence fusion, reranking, and deduplication
- Session-aware answer refinement for late-arriving constraints
- Query suppression for formatting/presentation-only requests
- Strict corpus-grounded citations and explicit uncertainty
- Structured observability telemetry
- Streaming answer output over Server-Sent Events
- Benchmark runner and ablation experiments
- Docker / one-command startup

The architecture follows the Theme 4 guide's four-stage pipeline: Retrieval Controller → Multi-Intent Decomposer → Corpus Retrieval & Fusion → Session-Aware Synthesis, with telemetry emitted throughout.

## Important corpus note

The supplied participant kit does not provide the official Theme 4 benchmark corpus in the repository. This project therefore uses a clearly labelled local demonstration corpus. This repo therefore ships a **small local demonstration corpus** in `data/sample_corpus.jsonl` so the prototype is runnable immediately. Replace that file with the official Theme 4 corpus when the official benchmark corpus/test set is provided.

The code is deliberately written so a replacement JSONL corpus can be dropped in without changing the architecture.

## Quick start

### Option A — local Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/build_index.py
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

In a second terminal:

```bash
source .venv/bin/activate
streamlit run ui/streamlit_app.py
```

Open `http://localhost:8501`.

### Option B — Docker

```bash
docker compose up --build
```

- API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Demo UI: `http://localhost:8501`

## API

### Health

`GET /health`

```json
{"status":"ok"}
```

### Single query

`POST /v1/query`

```json
{
  "session_id": "demo-1",
  "query": "What is the venue capacity and cancellation policy for a 30-person workshop in Pune?"
}
```

### Incremental stream

`POST /v1/stream`

```json
{
  "session_id": "demo-1",
  "chunks": [
    {"timestamp_s": 0.0, "text": "I need to plan a customer workshop"},
    {"timestamp_s": 0.8, "text": "for 30 people in Pune"},
    {"timestamp_s": 1.6, "text": "and I need the cancellation policy and catering options"},
    {"timestamp_s": 2.1, "text": "[UTTERANCE_END]"}
  ]
}
```

The endpoint emits Server-Sent Events containing retrieval decisions, sub-queries, citations, answer versions, and streamed tokens.

## Configuration

See `.env.example`.

The project runs without any external LLM key using a deterministic grounded synthesizer. For a generative demo, set:

```text
LLM_PROVIDER=gemini
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.0-flash
```

The LLM is never allowed to add unsupported sources; citations are generated from retrieved corpus chunks.

## Benchmarking

```bash
python scripts/run_benchmark.py
```

Results are written to `artifacts/benchmark_results.json`.

Ablation examples:

```bash
python scripts/run_ablation.py --mode hybrid_vs_sparse
python scripts/run_ablation.py --mode controller_vs_always_retrieve
```

The included benchmark is a **local engineering benchmark**, not an official Samsung hidden test. Do not present its numbers as official acceptance-gate results unless the official test set has been run.

## GitHub finalization

After the actual final implementation is validated:

```bash
git init
git add .
git commit -m "Final Theme 4 implementation"
git tag -a PRISM_GENAI_HACKATHON_Y2026 -m "PRISM Gen AI Hackathon Y2026 Final Submission"
```

Then connect the remote and push the branch + tag.

## Repository structure

```text
SRMIST_UNDEAD_4/
├── app/
│   ├── api/routes.py
│   ├── core/controller.py
│   ├── core/decomposer.py
│   ├── core/fusion.py
│   ├── core/grounding.py
│   ├── core/retrieval.py
│   ├── core/session.py
│   ├── core/synthesizer.py
│   ├── core/telemetry.py
│   ├── core/engine.py
│   └── main.py
├── data/sample_corpus.jsonl
├── docs/
├── scripts/
├── tests/
├── ui/streamlit_app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```
