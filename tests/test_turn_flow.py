from fastapi.testclient import TestClient

from app.api import routes
from app.core.turn_engine import TurnEngine
from app.domain.types import DurableRecord, QueryRequest
from app.main import app
from app.services.write_barrier import WriteBarrier
from app.storage.sqlite_store import SQLiteStore


def build_engine(tmp_path):
    db_path = tmp_path / "spectacle.db"
    return TurnEngine(sqlite_path=str(db_path))


def test_retrieval_hijack_regression(tmp_path):
    engine = build_engine(tmp_path)
    q = (
        "Claire, can you prove you can solve the 'Ship of Theseus' identity paradox for my deterministic "
        "Veritas Sovereign Core (VSC), built to U.S. Provisional Patent No. 63/942,560, that has been upgraded "
        "one component at a time, but also explain how your analysis would change if it were my human memory "
        "that was incrementally replaced with deterministic, analog recall engine (ARE) modules instead? You must "
        "include how both scenarios would impact the core concept of a 'sovereign' intelligence."
    )
    result = engine.run_query(QueryRequest(query=q, session_id="s1"))

    assert result["classification"]["primary_intent"] == "mixed"
    assert result["classification"]["reasoning_mode"] == "reasoning_first"
    assert "philosophical" in result["classification"]["secondary_intents"]
    assert "architectural" in result["classification"]["secondary_intents"]
    assert "technical" in result["classification"]["secondary_intents"]
    assert "legal_case" in result["classification"]["suppressed_lanes"]
    assert all("Paisley Park" not in support for support in result["supports"])
    assert "sovereignty" in result["answer"].lower()


def test_legal_recall_lane_allowed(tmp_path):
    engine = build_engine(tmp_path)
    q = "What is the holding in Paisley Park Enters., Inc. v. Boxill and is it relevant to copyright enforcement?"
    result = engine.run_query(QueryRequest(query=q, session_id="s2"))

    assert result["classification"]["primary_intent"] == "legal"
    assert "legal_case" in result["classification"]["allowed_lanes"]


def test_architecture_lane_suppression(tmp_path):
    engine = build_engine(tmp_path)
    q = "How should the deterministic truth spine interact with Sentinel and Gyro in a sovereign runtime?"
    result = engine.run_query(QueryRequest(query=q, session_id="s3"))

    allowed = result["classification"]["allowed_lanes"]
    assert "architecture" in allowed
    assert "runtime" in allowed
    assert "policy" in allowed
    assert "legal_case" in result["classification"]["suppressed_lanes"]


def test_mixed_memo_prioritization(tmp_path):
    engine = build_engine(tmp_path)
    q = "Give me a research memo connecting Ship of Theseus, identity continuity, and legal analogies relevant to AI sovereignty."
    result = engine.run_query(QueryRequest(query=q, session_id="s4"))

    assert result["classification"]["primary_intent"] == "mixed"
    assert "philosophical" in result["classification"]["secondary_intents"]
    assert "legal" in result["classification"]["secondary_intents"]
    assert "philosophy" in result["classification"]["allowed_lanes"]
    assert "identity" in result["classification"]["allowed_lanes"]
    assert "sovereignty" in result["classification"]["allowed_lanes"]
    assert "legal_case" in result["classification"]["suppressed_lanes"]


def test_write_barrier_commit_is_atomic_on_duplicate_record_id(tmp_path):
    store = SQLiteStore(str(tmp_path / "spectacle.db"))
    barrier = WriteBarrier(store)
    trace_id = "trace-atomic"
    duplicate_id = "dup-record"
    records = [
        DurableRecord(
            record_id=duplicate_id,
            record_kind="MemoryRecord",
            source_type="query",
            source_ref="/query",
            canonical_text="first",
            payload_json={"i": 1},
            lane_tags=["architecture"],
            trust_level=0.8,
            policy_status="allow",
            trace_id=trace_id,
            session_id="s1",
        ),
        DurableRecord(
            record_id=duplicate_id,
            record_kind="QueryTrace",
            source_type="query",
            source_ref="/query",
            canonical_text="second",
            payload_json={"i": 2},
            lane_tags=["architecture"],
            trust_level=0.9,
            policy_status="allow",
            trace_id=trace_id,
            session_id="s1",
        ),
    ]

    try:
        barrier.commit(records, approved=True)
        raised = False
    except Exception:
        raised = True

    assert raised
    assert store.fetch_trace_records(trace_id) == []


def test_prompt_prefix_returns_execute_turn_controlled_context(tmp_path, monkeypatch):
    monkeypatch.setattr(routes, "engine", build_engine(tmp_path))
    client = TestClient(app)

    response = client.post("/prompt-prefix", json={"query": "How should Gyro interact with Sentinel?", "session_id": "s5"})

    assert response.status_code == 200
    body = response.json()
    assert body["visor"]["query"] == "How should Gyro interact with Sentinel?"
    assert "answer_support" in body["visor"]
    assert "reasoning_support" in body["visor"]
    assert body["visor"]["trace_id"] == body["trace_id"]
    assert "policy" not in body["visor"]
    assert "posture" not in body["visor"]
