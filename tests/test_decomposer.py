from app.core.decomposer import MultiIntentDecomposer


def test_multi_intent():
    d = MultiIntentDecomposer()
    q = "I need venue capacity, cancellation policy and catering options in Pune"
    out = d.decompose(q)
    assert len(out) >= 3
