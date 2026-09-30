# 5-Minute Demo Script

## 0:00–0:30 — Problem

Explain that classic RAG waits for a full query, causing latency and forcing the system to ignore evolving multi-intent conversational input.

## 0:30–1:30 — Incremental retrieval

Play the transcript:

1. “I need to plan a customer workshop” → **WAIT**
2. “for 30 people in Pune” → **RETRIEVE** (provisional)
3. “and I need the cancellation policy and catering options” → **RETRIEVE** with multiple subqueries

Show the controller decision and parallel routing.

## 1:30–2:30 — Multi-intent retrieval

Show separate subqueries for capacity, cancellation, and catering. Highlight the merged evidence and source citations.

## 2:30–3:30 — Late-arriving refinement

First ask for the travel reimbursement rule. Then say: “Actually, the trip was international and the booking was made after travel.” Show that the system triggers `late_refinement`, updates Answer Version 2, and keeps the prior evidence.

## 3:30–4:15 — Query suppression

Ask: “Please repeat your last answer in bullet points.” Show `NO_RETRIEVAL` and no new corpus search.

## 4:15–5:00 — Telemetry and engineering

Show the JSONL telemetry record with timestamps, retrieval decisions, source mappings, answer version, and latency. Briefly show the Docker command and benchmark output.
