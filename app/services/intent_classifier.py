from __future__ import annotations

from app.domain.types import IntentClassification

LANE_SET = {
    "legal_case",
    "legal_theory",
    "philosophy",
    "identity",
    "sovereignty",
    "architecture",
    "runtime",
    "VSC",
    "ARE",
    "Claire_doctrine",
    "personal_context",
    "operations",
    "provenance",
    "policy",
    "product",
}


class IntentClassifier:
    def classify(self, query: str) -> IntentClassification:
        q = query.lower()

        markers = {
            "legal": [" v. ", "holding", "copyright", "court", "paisley", "legal", "patent"],
            "philosophical": ["ship of theseus", "identity", "paradox", "continuity", "sovereign intelligence"],
            "architectural": ["architecture", "runtime", "truth spine", "sentinel", "gyro", "interact", "vsc", "sovereign core"],
            "technical": ["deterministic", "module", "engine", "api", "component"],
            "psychological": ["memory", "mind", "cognition", "behavior"],
            "operational": ["runbook", "operate", "incident", "deployment", "workflow"],
        }
        hits = {k: any(token in q for token in vals) for k, vals in markers.items()}
        matched = [k for k, v in hits.items() if v]

        if len(matched) >= 2:
            primary = "mixed"
            reasoning_mode = "reasoning_first"
        elif hits["legal"]:
            primary = "legal"
            reasoning_mode = "retrieval_first"
        elif hits["architectural"]:
            primary = "architectural"
            reasoning_mode = "reasoning_first"
        elif hits["philosophical"]:
            primary = "philosophical"
            reasoning_mode = "reasoning_first"
        elif hits["operational"]:
            primary = "operational"
            reasoning_mode = "mixed"
        elif hits["psychological"]:
            primary = "psychological"
            reasoning_mode = "mixed"
        else:
            primary = "technical"
            reasoning_mode = "mixed"

        secondary = [m for m in matched if m != primary]
        allowed, suppressed = self._lane_policy(primary, secondary, q)

        return IntentClassification(
            primary_intent=primary,
            secondary_intents=secondary,
            confidence=0.84 if primary != "mixed" else 0.79,
            reasoning_mode=reasoning_mode,
            allowed_lanes=allowed,
            suppressed_lanes=suppressed,
            retrieval_strategy="reasoning_scaffold" if reasoning_mode == "reasoning_first" else "evidence_first",
        )

    def _lane_policy(self, primary: str, secondary: list[str], q: str) -> tuple[list[str], list[str]]:
        if primary == "legal":
            allowed = ["legal_case", "legal_theory", "policy", "provenance"]
            suppressed = ["Claire_doctrine"]
            return allowed, suppressed

        mixed_with_legal = "legal" in secondary or "legal" in q
        base = ["philosophy", "identity", "sovereignty", "architecture", "runtime", "VSC", "ARE", "policy", "product"]
        if primary in {"architectural", "technical", "operational"}:
            base.extend(["operations", "provenance"])
        if primary == "psychological":
            base.extend(["personal_context"])

        allowed = [lane for lane in dict.fromkeys(base) if lane in LANE_SET]
        if primary in {"mixed", "architectural", "technical", "philosophical", "psychological", "operational"} or mixed_with_legal:
            suppressed = ["legal_case"]
        else:
            suppressed = ["Claire_doctrine"]
        return allowed, [lane for lane in suppressed if lane in LANE_SET]
