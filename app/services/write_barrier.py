from __future__ import annotations

from app.domain.types import DurableRecord
from app.storage.sqlite_store import SQLiteStore


class WriteBarrier:
    def __init__(self, store: SQLiteStore) -> None:
        self.store = store

    def commit(self, records: list[DurableRecord], approved: bool) -> list[str]:
        if not approved:
            return []
        self.store.append_records(records)
        return [record.record_id for record in records]
