from app.core.controller import RetrievalController
from app.core.models import SessionState, AnswerState


def test_wait_on_fragment():
    c = RetrievalController()
    s = SessionState("x")
    r = c.decide("I need to plan", s, is_final=False)
    assert r.decision == "WAIT"


def test_retrieve_on_stable_intent():
    c = RetrievalController()
    s = SessionState("x")
    r = c.decide("I need a venue for 30 people in Pune", s, is_final=False)
    assert r.decision == "RETRIEVE"


def test_suppress_format_only():
    c = RetrievalController()
    s = SessionState("x")
    s.answer = AnswerState(version=1, answer="Existing answer", citations=["[Doc_01 §1]"])
    r = c.decide("Please repeat your last answer in bullet points", s, is_final=True)
    assert r.decision == "NO_RETRIEVAL"


def test_late_constraint():
    c = RetrievalController()
    s = SessionState("x")
    s.answer = AnswerState(version=1, answer="Existing answer")
    r = c.decide("Actually, the trip was international", s, is_final=True)
    assert r.decision == "RETRIEVE"
    assert r.trigger == "late_refinement"
