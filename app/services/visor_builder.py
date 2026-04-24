from __future__ import annotations


class VisorBuilder:
    def build(self, query: str, plan: dict, trace: dict) -> dict:
        return {
            "query": query,
            "answer_support": plan["supports"],
            "reasoning_support": plan["skeleton"],
            "trace_id": trace["trace_id"],
        }
