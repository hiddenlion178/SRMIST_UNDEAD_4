# Architecture

## Components

### API / Streaming
FastAPI exposes the query endpoint and streams progress/results using Server-Sent Events (SSE).

### Retrieval Controller
The retrieval layer isolates source selection and evidence retrieval from answer generation. The current implementation is a deterministic demo adapter.

### Synthesis
The synthesis layer converts retrieved evidence into the final answer. It is provider-neutral so an LLM integration can be added without changing the API layer.

### Telemetry
Request timing is emitted as a final streaming event, allowing latency to be observed by a client.

## Production Extension Points

- Connect live APIs, databases, search indexes, or vector stores.
- Add embeddings and reranking where appropriate.
- Integrate the selected LLM provider.
- Add source validation, citation handling, retries, timeouts, and authentication.
- Add persistent metrics and distributed tracing.
