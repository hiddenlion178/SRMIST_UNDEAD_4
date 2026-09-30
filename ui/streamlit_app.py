from __future__ import annotations

import json
import os
import time

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="UNDEAD — Streaming Live RAG", layout="wide")
st.title("UNDEAD — Streaming Live RAG")
st.caption("Theme 4 prototype: incremental retrieval, multi-intent routing, refinement and grounded citations")

if "session_id" not in st.session_state:
    st.session_state.session_id = "demo-session"

col1, col2 = st.columns([1.4, 1])
with col1:
    st.subheader("Live transcript simulator")
    sample = [
        {"timestamp_s": 0.0, "text": "I need to plan a customer workshop"},
        {"timestamp_s": 0.8, "text": "for 30 people in Pune"},
        {"timestamp_s": 1.6, "text": "and I need the cancellation policy and catering options"},
        {"timestamp_s": 2.1, "text": "[UTTERANCE_END]"},
    ]
    if "chunks" not in st.session_state:
        st.session_state.chunks = sample

    if st.button("Reset demo"):
        st.session_state.chunks = sample
        st.session_state.session_id = f"demo-{int(time.time())}"
        st.rerun()

    for i, ch in enumerate(st.session_state.chunks):
        st.write(f"**{ch['timestamp_s']:.1f}s**  {ch['text']}")

    if st.button("Run Streaming RAG"):
        with st.spinner("Processing transcript stream..."):
            try:
                r = requests.post(f"{API_URL}/v1/stream", json={"session_id": st.session_state.session_id, "chunks": st.session_state.chunks}, stream=True, timeout=60)
                r.raise_for_status()
                states = []
                tokens = []
                event = None
                buf = ""
                for line in r.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    if line.startswith("event:"):
                        event = line.split(":", 1)[1].strip()
                    elif line.startswith("data:"):
                        payload = json.loads(line.split(":", 1)[1].strip())
                        if event == "state":
                            states.append(payload)
                        elif event == "token":
                            tokens.append(payload.get("token", ""))
                        elif event == "done":
                            pass
                st.session_state.states = states
                st.session_state.tokens = tokens
            except Exception as exc:
                st.error(f"API error: {exc}")

with col2:
    st.subheader("Controller / Retrieval state")
    for state in st.session_state.get("states", []):
        dec = state.get("decision", {})
        st.metric("Decision", dec.get("decision", "—"))
        st.write(f"**Trigger:** {dec.get('trigger', '—')}")
        st.write(f"**Reason:** {dec.get('reason', '—')}")
        if state.get("sub_queries"):
            st.write("**Sub-queries**")
            for q in state["sub_queries"]:
                st.write(f"- {q}")

st.divider()
st.subheader("Streaming grounded answer")
if st.session_state.get("tokens"):
    st.write("".join(st.session_state.tokens))
elif st.session_state.get("states"):
    last = st.session_state.states[-1]
    st.write(last.get("answer", ""))

if st.session_state.get("states"):
    last = st.session_state.states[-1]
    st.subheader("Citations")
    for c in last.get("citations", []):
        st.write(f"- {c}")

st.subheader("Late-arriving refinement")
late = st.text_input("Add a late constraint", placeholder="Actually, the trip was international and booking was after travel.")
if st.button("Apply late constraint") and late:
    try:
        payload = {"session_id": st.session_state.session_id, "query": late}
        r = requests.post(f"{API_URL}/v1/query", json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        st.write(data.get("answer", ""))
        st.caption(f"Answer version {data.get('answer_version')}; trigger = {data.get('decision', {}).get('trigger')}")
        for c in data.get("citations", []):
            st.write(f"- {c}")
    except Exception as exc:
        st.error(str(exc))
