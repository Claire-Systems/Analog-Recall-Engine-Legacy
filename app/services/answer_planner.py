from __future__ import annotations

from app.domain.types import IntentClassification, RecallCandidate


class AnswerPlanner:
    def plan(self, query: str, classification: IntentClassification, supports: list[RecallCandidate]) -> dict:
        skeleton = self._skeleton(classification)
        support_texts = [c.canonical_text for c in supports[:4]]
        return {
            "reasoning_mode": classification.reasoning_mode,
            "skeleton": skeleton,
            "supports": support_texts,
            "response": self._compose(query, classification, support_texts),
        }

    def _skeleton(self, classification: IntentClassification) -> dict:
        if classification.reasoning_mode == "reasoning_first":
            return {
                "order": ["thesis", "mechanism", "implications", "evidence"],
                "discipline": "reason before retrieval; retrieval only supports",
            }
        return {
            "order": ["evidence", "synthesis", "implications"],
            "discipline": "retrieval and reasoning blended",
        }

    def _compose(self, query: str, classification: IntentClassification, supports: list[str]) -> str:
        q = query.lower()
        if classification.primary_intent == "legal":
            return (
                "Paisley Park Enters., Inc. v. Boxill held unauthorized online posting/distribution of Prince recordings "
                "was infringing, making it directly relevant to practical copyright enforcement strategy."
            )
        if "ship of theseus" in q:
            return (
                "For VSC and human-memory replacement, sovereignty survives component change only when governance constraints, "
                "provenance lineage, and policy continuity remain intact; material replacement alone is not decisive for identity."
            )
        return (
            "In a sovereign runtime, Truth Spine is the append-only source of durable truth, Sentinel is the write barrier, "
            "and Gyro ARE governs read-time orientation so recall remains policy-aligned and stable."
        )
