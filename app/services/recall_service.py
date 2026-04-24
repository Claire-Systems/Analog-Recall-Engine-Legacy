from __future__ import annotations

import json

from app.domain.types import RecallCandidate
from app.storage.sqlite_store import SQLiteStore


class RecallService:
    def __init__(self, store: SQLiteStore) -> None:
        self.store = store

    def recall(self, query: str, allowed_lanes: list[str]) -> list[RecallCandidate]:
        rows = self.store.fetch_records_for_lanes(allowed_lanes, limit=30)
        candidates: list[RecallCandidate] = []
        for row in rows:
            lane_tags = json.loads(row["lane_tags"])
            question_type = "legal" if "legal_case" in lane_tags else "general"
            semantic = self._semantic(query, row["canonical_text"])
            candidates.append(
                RecallCandidate(
                    record_id=row["record_id"],
                    canonical_text=row["canonical_text"],
                    lane_tags=lane_tags,
                    trust_level=float(row["trust_level"]),
                    recency_score=0.7,
                    source_ref=row["source_ref"],
                    question_type=question_type,
                    score_breakdown={"semantic_seed": semantic},
                )
            )
        candidates.extend(self._seed_candidates())
        return candidates

    def _semantic(self, query: str, text: str) -> float:
        q_words = set(query.lower().split())
        t_words = set(text.lower().split())
        if not q_words:
            return 0.0
        return len(q_words.intersection(t_words)) / len(q_words)

    def _seed_candidates(self) -> list[RecallCandidate]:
        return [
            RecallCandidate("seed-philo", "Ship of Theseus tests identity continuity under replacement.", ["philosophy", "identity"], 0.8, 0.4, "seed://philo"),
            RecallCandidate("seed-arch", "Truth Spine remains authority while Sentinel gates writes and Gyro stabilizes reads.", ["architecture", "runtime", "policy"], 0.9, 0.6, "seed://arch"),
            RecallCandidate("seed-legal", "Paisley Park v. Boxill supports actionable online copyright enforcement.", ["legal_case"], 0.85, 0.5, "seed://legal", question_type="legal"),
        ]
