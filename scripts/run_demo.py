from app.dependencies import get_engine

engine = get_engine()
session = "cli-demo"
chunks = [
    (0.0, "I need to plan a customer workshop"),
    (0.8, "for 30 people in Pune"),
    (1.6, "and I need the cancellation policy and catering options"),
]
for ts, text in chunks:
    result = engine.process_chunk(session, ts, text, is_final=False)
    print(f"{ts:.1f}s -> {result['decision']}")
    if result["sub_queries"]:
        print("  subqueries:", *result["sub_queries"], sep="\n    - ")
    if result["answer"]:
        print("  answer:", result["answer"])

result = engine.process_chunk(session, 2.1, "", is_final=True)
print("2.1s ->", result["decision"])
print(result["answer"])
