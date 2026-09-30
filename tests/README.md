# Tests

Add automated API/retrieval/synthesis tests here.

Suggested checks:
- GET /health returns HTTP 200.
- POST /query validates query and top_k.
- POST /query returns SSE events in the expected order.
