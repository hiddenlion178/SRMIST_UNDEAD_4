from app.dependencies import get_engine

engine = get_engine()
print(f"Loaded {len(engine.retriever.chunks)} corpus chunks")
print("Index ready")
