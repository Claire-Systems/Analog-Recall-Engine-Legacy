from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GravelArtifact:
    artifact_id: str
    artifact_kind: str
    payload: dict


class GravelStore:
    """Rebuildable secondary artifacts. Never authoritative."""

    def __init__(self) -> None:
        self._artifacts: dict[str, GravelArtifact] = {}

    def put(self, artifact: GravelArtifact) -> None:
        self._artifacts[artifact.artifact_id] = artifact

    def rebuild(self) -> None:
        self._artifacts = {}
