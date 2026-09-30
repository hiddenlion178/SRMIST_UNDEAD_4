# Architecture Brief — Streaming Live RAG

## 1. Problem

Traditional RAG waits for an entire user turn before searching. Theme 4 requires an event-driven system that can begin retrieval on stable partial transcript chunks, split compound utterances into independent intents, refine an existing answer when new constraints arrive, and suppress unnecessary retrieval for presentation-only requests.

## 2. Pipeline

```text
Incremental Transcript
        |
        v
Retrieval Controller
 WAIT / RETRIEVE / NO_RETRIEVAL
        |
        v
Multi-Intent Decomposer
        |
        +-------------------+-------------------+
        |                   |                   |
      Query 1             Query 2             Query 3
        |                   |                   |
        +-------------------+-------------------+
                            v
                 Dense + Sparse Retrieval
                            |
                    Rerank + Deduplicate
                            |
                      Evidence Fusion
                            |
                    Session State Store
                            |
                  Grounded Synthesis
                            |
               Streamed Answer + Sources
                            |
                     Telemetry / Logs
```

## 3. Retrieval Controller

The controller considers chunk size, semantic stability, search hints, existing answer state, and formatting-only language.

- `WAIT`: incomplete fragment or unstable intent.
- `RETRIEVE`: search intent is sufficiently stable.
- `NO_RETRIEVAL`: the user is only asking to transform or reformat an existing response.
- `late_refinement` trigger: a new constraint modifies an existing topic; retrieval targets only the delta.

## 4. Multi-Intent Routing

The decomposer detects multiple intent classes and produces search-ready subqueries. Retrieval is performed concurrently to reduce wall-clock latency. Over-fragmentation is avoided by preserving the full utterance as a fallback.

## 5. Evidence Fusion

Each subquery uses hybrid scoring:

`hybrid = alpha * dense + (1-alpha) * sparse`

The implementation also adds lightweight lexical overlap, rewards evidence appearing across multiple subqueries, and removes highly similar duplicate chunks.

## 6. Session Refinement

Sessions store only active conversation state. A late constraint triggers targeted retrieval and merges delta evidence into the current evidence set. The answer version increments instead of restarting the whole session.

## 7. Grounding

The response uses only retrieved corpus chunks. Citations are created by the application from source metadata, not invented by the LLM. The deterministic fallback returns explicit uncertainty if the corpus does not provide evidence.

## 8. Observability

Telemetry events capture timestamps, decisions, triggers, subqueries, source citations, retrieval latency, answer versions, and citation support ratios. Logs are JSONL for replay and analysis.

## 9. Reproducibility

The repository contains pinned Python dependencies, Docker configuration, a local sample corpus, automated tests, benchmark scripts, and one-command startup instructions.
