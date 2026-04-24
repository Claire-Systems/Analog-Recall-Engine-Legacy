from __future__ import annotations


class ContradictionChecker:
    def evaluate(self, proposed_text: str, supports: list[str]) -> dict:
        contradiction = "not" in proposed_text.lower() and any("always" in s.lower() for s in supports)
        return {
            "has_contradiction": contradiction,
            "reason": "heuristic_negation_conflict" if contradiction else "none",
        }
