from app.core.turn_engine import TurnEngine
from app.domain.types import QueryRequest


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
