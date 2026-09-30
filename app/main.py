from fastapi import FastAPI
from dotenv import load_dotenv

from app.api.routes import router

load_dotenv()
app = FastAPI(title="SRMIST UNDEAD 4 — Streaming Live RAG", version="0.1.0")
app.include_router(router)
