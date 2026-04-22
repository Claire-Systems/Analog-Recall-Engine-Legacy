from __future__ import annotations

from app.storage.sqlite_store import SQLiteStore


class SessionStore:
    def __init__(self, sqlite_store: SQLiteStore) -> None:
        self.sqlite_store = sqlite_store

    def append_event(self, session_id: str, trace_id: str, created_at: str, event_type: str, payload: dict) -> None:
        self.sqlite_store.append_session_event(session_id, trace_id, created_at, event_type, payload)

    def update_snapshot(self, session_id: str, trace_id: str, updated_at: str, snapshot: dict) -> None:
        self.sqlite_store.upsert_session_state(session_id, trace_id, updated_at, snapshot)
