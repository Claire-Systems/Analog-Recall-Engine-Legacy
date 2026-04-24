from __future__ import annotations

from app.domain.types import IntentClassification


class GyroARE:
    def orient(self, classification: IntentClassification) -> dict:
        return {
            "lane_affinity": classification.allowed_lanes,
            "stability_vector": {
                "recency": 0.2,
                "historical_relevance": 0.2,
                "lane_affinity": 0.25,
                "semantic_direction": 0.15,
                "trust": 0.1,
                "session_momentum": 0.1,
            },
        }
