from __future__ import annotations

from app.domain.types import TrailEdge


class TrailLink:
    def build_edges(self, parent_ids: list[str], child_id: str, trace_id: str) -> list[TrailEdge]:
        return [TrailEdge(parent_record_id=pid, child_record_id=child_id, edge_kind="derived_from", trace_id=trace_id) for pid in parent_ids]
