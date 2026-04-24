from __future__ import annotations


class ScraperBots:
    def acquire(self, text: str, source_ref: str) -> dict:
        return {"raw_text": text, "source_ref": source_ref, "source_type": "session"}


class EchoShield:
    def scrub(self, payload: dict) -> dict:
        raw = payload["raw_text"]
        redacted = raw.replace("API_KEY", "[REDACTED]")
        return {"clean_text": redacted, "flags": ["redacted"] if raw != redacted else []}


class CrownJewelParser:
    def parse(self, clean_text: str) -> dict:
        return {
            "canonical_text": clean_text,
            "entities": ["VSC"] if "vsc" in clean_text.lower() else [],
            "lane_tags": ["runtime"] if "runtime" in clean_text.lower() else ["operations"],
        }
