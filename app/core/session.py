from __future__ import annotations

from threading import Lock
from .models import SessionState


class SessionStore:
    def __init__(self):
        self._sessions: dict[str, SessionState] = {}
        self._lock = Lock()

    def get(self, session_id: str) -> SessionState:
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = SessionState(session_id=session_id)
            return self._sessions[session_id]

    def clear(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)
