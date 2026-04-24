from __future__ import annotations

from datetime import datetime, timezone

from app.domain.types import DurableRecord, QueryRequest
from app.services.answer_planner import AnswerPlanner
from app.services.contradiction_checker import ContradictionChecker
from app.services.gyro_are import GyroARE
from app.services.intent_classifier import IntentClassifier
from app.services.intake import CrownJewelParser, EchoShield, ScraperBots
from app.services.lane_router import LaneRouter
from app.services.lycanthrope import Lycanthrope
from app.services.recall_service import RecallService
from app.services.recognition_rail import RecognitionRail
from app.services.relevance_gate import RelevanceGate
from app.services.sentinel import Sentinel
from app.services.traillink import TrailLink
from app.services.visor_builder import VisorBuilder
from app.services.write_barrier import WriteBarrier
from app.storage.gravel_store import GravelArtifact, GravelStore
from app.storage.session_store import SessionStore
from app.storage.sqlite_store import SQLiteStore
from app.tracing.veritas import Trace


class TurnEngine:
    def __init__(self, sqlite_path: str = "spectacle.db") -> None:
        self.sqlite = SQLiteStore(sqlite_path)
        self.session_store = SessionStore(self.sqlite)
        self.gravel = GravelStore()

        self.classifier = IntentClassifier()
        self.router = LaneRouter()
        self.gyro = GyroARE()
        self.recall = RecallService(self.sqlite)
        self.relevance_gate = RelevanceGate()
        self.planner = AnswerPlanner()
        self.visor = VisorBuilder()
        self.rail = RecognitionRail()
        self.sentinel = Sentinel()
        self.lycan = Lycanthrope()
        self.contradiction = ContradictionChecker()
        self.write_barrier = WriteBarrier(self.sqlite)
        self.traillink = TrailLink()
        self.scraper = ScraperBots()
        self.echo = EchoShield()
        self.parser = CrownJewelParser()

    def run_query(self, req: QueryRequest) -> dict:
        trace = Trace()
        now = datetime.now(timezone.utc).isoformat()

        # prepare_turn
        self.session_store.append_event(req.session_id, trace.trace_id, now, "user_turn", {"query": req.query})
        classification = self.classifier.classify(req.query)
        lane_plan = self.router.route(classification)
        gyro_state = self.gyro.orient(classification)
        trace.add("prepare_turn", {"classification": classification.__dict__, "lane_plan": lane_plan, "gyro": gyro_state})

        # execute_turn
        recalled = self.recall.recall(req.query, lane_plan["allowed_lanes"])
        routed = [c for c in recalled if not set(c.lane_tags).intersection(lane_plan["suppressed_lanes"])]
        accepted = self.relevance_gate.filter(routed, lane_plan["allowed_lanes"], classification.primary_intent)
        plan = self.planner.plan(req.query, classification, accepted)
        visor = self.visor.build(req.query, plan, trace.to_dict())
        rail = self.rail.build_payload(visor)
        contradiction = self.contradiction.evaluate(plan["response"], plan["supports"])
        trace.add(
            "execute_turn",
            {
                "accepted_candidates": [c.record_id for c in accepted],
                "rejected_candidates": [c.record_id for c in routed if c.record_id not in {a.record_id for a in accepted}],
                "rail": rail,
                "contradiction": contradiction,
            },
        )

        policy = self.sentinel.decide([{"text": plan["response"], "lane_tags": classification.allowed_lanes}])
        if contradiction["has_contradiction"]:
            policy = {"decision": "quarantine", "reason": contradiction["reason"]}
        posture = self.lycan.posture(policy)
        trace.add("governance", {"policy": policy, "posture": posture})

        # finalize_turn
        records_to_commit = self._build_finalize_records(req, trace.trace_id, classification.__dict__, plan, policy, posture)
        committed = self.write_barrier.commit(records_to_commit, approved=policy["decision"].startswith("allow") and not posture["freeze_writes"])
        if committed:
            parent_ids = [c.record_id for c in accepted]
            edges = self.traillink.build_edges(parent_ids, committed[0], trace.trace_id)
            self.sqlite.append_edges(edges)

        self.session_store.update_snapshot(req.session_id, trace.trace_id, now, {"last_intent": classification.primary_intent})
        self.gravel.put(GravelArtifact(artifact_id=trace.trace_id, artifact_kind="trace_index", payload={"committed": committed}))
        trace.add("finalize_turn", {"committed_records": committed, "record_kinds": [r.record_kind for r in records_to_commit]})

        return {
            "trace_id": trace.trace_id,
            "classification": classification.__dict__,
            "lane_plan": lane_plan,
            "answer": plan["response"],
            "supports": plan["supports"],
            "committed_records": committed,
            "trace": trace.to_dict(),
        }

    def _build_finalize_records(self, req: QueryRequest, trace_id: str, classification: dict, plan: dict, policy: dict, posture: dict) -> list[DurableRecord]:
        base = dict(
            source_type="query",
            source_ref="/query",
            trace_id=trace_id,
            session_id=req.session_id,
            lane_tags=classification["allowed_lanes"],
        )
        return [
            DurableRecord(
                record_kind="MemoryRecord",
                canonical_text=plan["response"],
                payload_json={"supports": plan["supports"], "reasoning_mode": classification["reasoning_mode"]},
                trust_level=0.8,
                policy_status=policy["decision"],
                **base,
            ),
            DurableRecord(
                record_kind="QueryTrace",
                canonical_text=req.query,
                payload_json={"classification": classification, "lane_plan": classification["allowed_lanes"]},
                trust_level=0.9,
                policy_status="allow",
                **base,
            ),
            DurableRecord(
                record_kind="PolicyDecision",
                canonical_text=policy["decision"],
                payload_json=policy,
                trust_level=0.95,
                policy_status="allow",
                **base,
            ),
            DurableRecord(
                record_kind="PostureSignal",
                canonical_text=posture["posture"],
                payload_json=posture,
                trust_level=0.95,
                policy_status="allow",
                **base,
            ),
            DurableRecord(
                record_kind="DerivedRecord",
                canonical_text=f"report:{trace_id}",
                payload_json={"report": "trace-summary", "query": req.query},
                trust_level=0.7,
                policy_status="allow",
                **base,
            ),
        ]

    def ingest(self, text: str, source_ref: str, session_id: str) -> dict:
        trace = Trace()
        acquired = self.scraper.acquire(text, source_ref)
        scrubbed = self.echo.scrub(acquired)
        parsed = self.parser.parse(scrubbed["clean_text"])
        lane_tags = parsed["lane_tags"] or self.router.infer_lanes(parsed["canonical_text"])
        record = DurableRecord(
            record_kind="IngestRecord",
            source_type=acquired["source_type"],
            source_ref=source_ref,
            canonical_text=parsed["canonical_text"],
            payload_json={"flags": scrubbed["flags"], "entities": parsed["entities"]},
            lane_tags=lane_tags,
            trust_level=0.7,
            policy_status="allow",
            trace_id=trace.trace_id,
            session_id=session_id,
        )
        self.sqlite.append_record(record)
        return {"record_id": record.record_id, "trace_id": trace.trace_id, "lane_tags": record.lane_tags}

    def get_trace(self, trace_id: str) -> dict:
        records = self.sqlite.fetch_trace_records(trace_id)
        return {"trace_id": trace_id, "records": records}

    def get_report(self, trace_id: str) -> dict:
        records = [r for r in self.sqlite.fetch_trace_records(trace_id) if r["record_kind"] == "DerivedRecord"]
        return {"trace_id": trace_id, "reports": records}
