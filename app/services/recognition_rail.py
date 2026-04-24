from __future__ import annotations


class RecognitionRail:
    def build_payload(self, visor: dict) -> dict:
        return {
            "controlled_context": visor,
            "write_access": False,
        }
