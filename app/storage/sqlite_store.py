from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Iterable

from app.domain.types import DurableRecord, TrailEdge


class SQLiteStore:
    def __init__(self, db_path: str = "spectacle.db") -> None:
        self.db_path = db_path
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS durable_records (
                    record_id TEXT PRIMARY KEY,
                    record_kind TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    source_ref TEXT NOT NULL,
                    canonical_text TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    lane_tags TEXT NOT NULL,
                    trust_level REAL NOT NULL,
                    policy_status TEXT NOT NULL,
                    parent_record_ids TEXT NOT NULL,
                    supersedes_record_ids TEXT NOT NULL,
                    trace_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    content_hash TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS trail_edges (
                    edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parent_record_id TEXT NOT NULL,
                    child_record_id TEXT NOT NULL,
                    edge_kind TEXT NOT NULL,
                    trace_id TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS session_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    trace_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS session_state (
                    session_id TEXT PRIMARY KEY,
                    trace_id TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    snapshot_json TEXT NOT NULL
                );
                """
            )

    def append_record(self, record: DurableRecord) -> None:
        payload = json.dumps(record.payload_json, sort_keys=True)
        lane_tags = json.dumps(record.lane_tags)
        parent_ids = json.dumps(record.parent_record_ids)
        supersedes = json.dumps(record.supersedes_record_ids)
        content_hash = hashlib.sha256(record.canonical_text.encode("utf-8")).hexdigest()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO durable_records (
                    record_id, record_kind, created_at, source_type, source_ref,
                    canonical_text, payload_json, lane_tags, trust_level, policy_status,
                    parent_record_ids, supersedes_record_ids, trace_id, session_id, content_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.record_id,
                    record.record_kind,
                    record.created_at,
                    record.source_type,
                    record.source_ref,
                    record.canonical_text,
                    payload,
                    lane_tags,
                    record.trust_level,
                    record.policy_status,
                    parent_ids,
                    supersedes,
                    record.trace_id,
                    record.session_id,
                    content_hash,
                ),
            )

    def append_session_event(self, session_id: str, trace_id: str, created_at: str, event_type: str, payload: dict) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO session_events (session_id, trace_id, created_at, event_type, payload_json) VALUES (?, ?, ?, ?, ?)",
                (session_id, trace_id, created_at, event_type, json.dumps(payload)),
            )

    def upsert_session_state(self, session_id: str, trace_id: str, updated_at: str, snapshot: dict) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO session_state (session_id, trace_id, updated_at, snapshot_json)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(session_id)
                DO UPDATE SET trace_id=excluded.trace_id, updated_at=excluded.updated_at, snapshot_json=excluded.snapshot_json
                """,
                (session_id, trace_id, updated_at, json.dumps(snapshot)),
            )

    def append_edges(self, edges: Iterable[TrailEdge]) -> None:
        with self._connect() as conn:
            conn.executemany(
                "INSERT INTO trail_edges (parent_record_id, child_record_id, edge_kind, trace_id, created_at) VALUES (?, ?, ?, ?, ?)",
                [(e.parent_record_id, e.child_record_id, e.edge_kind, e.trace_id, e.created_at) for e in edges],
            )

    def fetch_records(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM durable_records ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]

    def fetch_records_for_lanes(self, allowed_lanes: list[str], limit: int = 20) -> list[dict]:
        if not allowed_lanes:
            return []
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM durable_records ORDER BY created_at DESC LIMIT ?",
                (max(limit * 3, limit),),
            ).fetchall()
        selected: list[dict] = []
        for row in rows:
            lane_tags = json.loads(row["lane_tags"])
            if set(lane_tags).intersection(allowed_lanes):
                selected.append(dict(row))
            if len(selected) >= limit:
                break
        return selected

    def fetch_trace_records(self, trace_id: str) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM durable_records WHERE trace_id = ? ORDER BY created_at ASC",
                (trace_id,),
            ).fetchall()
        return [dict(r) for r in rows]
