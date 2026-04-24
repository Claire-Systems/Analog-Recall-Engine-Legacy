from __future__ import annotations

from app.domain.types import IntentClassification


class LaneRouter:
    def route(self, classification: IntentClassification) -> dict[str, list[str]]:
        downranked = ["personal_context", "Claire_doctrine"]
        if classification.primary_intent == "legal":
            downranked = ["philosophy", "personal_context", "Claire_doctrine"]
        return {
            "allowed_lanes": classification.allowed_lanes,
            "suppressed_lanes": classification.suppressed_lanes,
            "downranked_lanes": downranked,
        }

    def infer_lanes(self, text: str) -> list[str]:
        q = text.lower()
        lanes: list[str] = []
        if "paisley" in q or "holding" in q:
            lanes.append("legal_case")
        if "ship of theseus" in q or "identity" in q:
            lanes.extend(["philosophy", "identity"])
        if "runtime" in q or "truth spine" in q:
            lanes.extend(["architecture", "runtime"])
        if "policy" in q or "sentinel" in q:
            lanes.append("policy")
        return list(dict.fromkeys(lanes or ["operations"]))
