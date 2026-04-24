from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.turn_engine import TurnEngine
from app.domain.types import QueryRequest

router = APIRouter()
engine = TurnEngine(sqlite_path="data/spectacle.db")


class IngestBody(BaseModel):
    text: str
    source_ref: str = "manual"
    session_id: str = "default"


class QueryBody(BaseModel):
    query: str
    session_id: str = "default"


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "product": "ARE Spectacle v2"}


@router.post("/ingest")
def ingest(body: IngestBody) -> dict:
    return engine.ingest(body.text, body.source_ref, body.session_id)


@router.post("/query")
def query(body: QueryBody) -> dict:
    return engine.run_query(QueryRequest(query=body.query, session_id=body.session_id))


@router.get("/gyro")
def gyro() -> dict:
    return {"status": "seeded", "engine": "Gyro ARE"}


@router.post("/prompt-prefix")
def prompt_prefix(body: QueryBody) -> dict:
    result = engine.run_query(QueryRequest(query=body.query, session_id=body.session_id))
    execute_turn = next(event for event in result["trace"]["events"] if event["stage"] == "execute_turn")
    return {"trace_id": result["trace_id"], "visor": execute_turn["payload"]["rail"]["controlled_context"]}


@router.get("/trace/{trace_id}")
def trace(trace_id: str) -> dict:
    return engine.get_trace(trace_id)


@router.get("/report/{trace_id}")
def report(trace_id: str) -> dict:
    return engine.get_report(trace_id)
