from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class IntentClassification:
    primary_intent: str
    secondary_intents: list[str]
    confidence: float
    reasoning_mode: str
    allowed_lanes: list[str]
    suppressed_lanes: list[str]
    retrieval_strategy: str


@dataclass
class QueryRequest:
    query: str
    session_id: str


@dataclass
class RecallCandidate:
    record_id: str
    canonical_text: str
    lane_tags: list[str]
    trust_level: float
    recency_score: float
    source_ref: str
    question_type: str = "general"
    score_breakdown: dict[str, float] = field(default_factory=dict)


@dataclass
class DurableRecord:
    record_kind: str
    source_type: str
    source_ref: str
    canonical_text: str
    payload_json: dict[str, Any]
    lane_tags: list[str]
    trust_level: float
    policy_status: str
    trace_id: str
    session_id: str
    parent_record_ids: list[str] = field(default_factory=list)
    supersedes_record_ids: list[str] = field(default_factory=list)
    record_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now)


@dataclass
class TrailEdge:
    parent_record_id: str
    child_record_id: str
    edge_kind: str
    trace_id: str
    created_at: str = field(default_factory=utc_now)
