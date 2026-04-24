from __future__ import annotations

from app.domain.types import RecallCandidate


class RelevanceGate:
    def filter(self, candidates: list[RecallCandidate], allowed_lanes: list[str], query_type: str) -> list[RecallCandidate]:
        accepted: list[RecallCandidate] = []
        for candidate in candidates:
            lane_match = 1.0 if set(candidate.lane_tags).intersection(allowed_lanes) else 0.0
            question_type_match = 1.0 if candidate.question_type in {"general", query_type} else 0.2
            semantic = min(len(candidate.canonical_text) / 200.0, 1.0)
            entity = 0.8
            support_role_fit = 0.9
            final_score = (
                lane_match * 0.35
                + question_type_match * 0.2
                + semantic * 0.15
                + entity * 0.1
                + candidate.recency_score * 0.1
                + candidate.trust_level * 0.05
                + support_role_fit * 0.05
            )
            candidate.score_breakdown = {
                "lane_match": lane_match,
                "question_type_match": question_type_match,
                "semantic_match": semantic,
                "entity_match": entity,
                "recency": candidate.recency_score,
                "trust": candidate.trust_level,
                "support_role_fit": support_role_fit,
                "final_score": final_score,
            }
            if lane_match < 0.5 or question_type_match < 0.5:
                continue
            accepted.append(candidate)
        return sorted(accepted, key=lambda c: c.score_breakdown["final_score"], reverse=True)
