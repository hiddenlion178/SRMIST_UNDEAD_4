from app.dependencies import get_engine


def test_engine_stream_and_refinement():
    engine = get_engine()
    s = "pytest-session"
    r1 = engine.process_chunk(s, 0.8, "I need a venue for 30 people in Pune", is_final=True)
    assert r1["decision"]["decision"] == "RETRIEVE"
    assert r1["citations"]
    r2 = engine.process_chunk(s, 1.6, "Actually, the trip was international and the booking was made after travel", is_final=True)
    assert r2["answer_version"] >= 2
