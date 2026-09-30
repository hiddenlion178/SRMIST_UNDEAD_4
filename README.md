# PRISM GENAI HACKATHON Y2026 — Streaming Live RAG

**Team:** SRMIST_UNDEAD_4  
**Theme:** Theme 4 — Streaming Live RAG  
**Submission Tag:** PRISM_GENAI_HACKATHON_Y2026

## Overview

This project implements a streaming Retrieval-Augmented Generation (RAG) service designed to retrieve relevant evidence and progressively stream the response to the client.

The application is organized into independent retrieval, synthesis, streaming API, and telemetry components so that the demo implementation can be extended with production retrieval and LLM providers without changing the API contract.

## Architecture

```text
Client
  |
  v
FastAPI /query
  |
  +--> Retrieval Controller --> Evidence
  |
  +--> Synthesis Generator --> Answer
  |
  +--> Telemetry --> Latency / events
  |
  v
SSE event stream
```

## Repository Structure

```text
SRMIST_UNDEAD_4/
├── app/
│   ├── main.py
│   ├── retrieval/
│   │   └── controller.py
│   ├── synthesis/
│   │   └── generator.py
│   └── telemetry/
│       └── metrics.py
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DEMO_VIDEO.md
│   └── SUBMISSION.md
├── presentation/
│   └── SRMIST_UNDEAD_4.pptx
├── tests/
│   └── README.md
├── .gitignore
├── .submission_tag
├── Dockerfile
├── README.md
└── requirements.txt
```

## Quick Start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open the API at `http://127.0.0.1:8000`.

### Health check

```text
GET /health
```

### Streaming query

```text
POST /query
Content-Type: application/json

{"query":"What is streaming RAG?","top_k":5}
```

The response is delivered as Server-Sent Events (SSE).

## Docker

```bash
docker build -t srmist-undead-4 .
docker run -p 8000:8000 srmist-undead-4
```

## Demo and Presentation

The presentation belongs in `presentation/SRMIST_UNDEAD_4.pptx`.

If the demo video is hosted externally because of file-size limits, add the accessible YouTube/Google Drive link to `docs/DEMO_VIDEO.md`.

## Submission

The required submission marker is stored in `.submission_tag`. The actual Git tag should be created after all final submission files have been committed.

## Notes

The retrieval and synthesis modules are intentionally provider-neutral demo components. Replace them with the project's real retrieval index/data sources and LLM provider configuration when available.
