from __future__ import annotations


class Sentinel:
    def decide(self, candidate_facts: list[dict]) -> dict:
        if not candidate_facts:
            return {"decision": "deny", "reason": "no_candidate_facts"}
        redactions = [f for f in candidate_facts if "secret" in f.get("text", "").lower()]
        if redactions:
            return {"decision": "allow_with_redaction", "reason": "contains_sensitive_content", "redactions": len(redactions)}
        return {"decision": "allow", "reason": "policy_clean"}
