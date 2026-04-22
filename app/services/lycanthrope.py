from __future__ import annotations


class Lycanthrope:
    def posture(self, policy_decision: dict, recent_strain: int = 0) -> dict:
        if policy_decision.get("decision") in {"deny", "quarantine"} or recent_strain > 3:
            return {"posture": "heightened", "freeze_writes": True}
        return {"posture": "normal", "freeze_writes": False}
