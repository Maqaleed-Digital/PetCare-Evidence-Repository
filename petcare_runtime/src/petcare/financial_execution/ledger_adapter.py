from __future__ import annotations

from dataclasses import asdict
from typing import List

from .models import LedgerEntry


def build_ledger_entry(
    entry_id: str,
    settlement_id: str,
    reference_id: str,
    event_type: str,
    occurred_at: str,
    payload_checksum: str,
    metadata: dict[str, str],
) -> LedgerEntry:
    return LedgerEntry(
        entry_id=entry_id,
        settlement_id=settlement_id,
        reference_id=reference_id,
        event_type=event_type,
        occurred_at=occurred_at,
        payload_checksum=payload_checksum,
        metadata=metadata,
    )


class LedgerTraceStore:
    def __init__(self) -> None:
        self._entries: List[LedgerEntry] = []

    def append(self, entry: LedgerEntry) -> None:
        self._entries.append(entry)

    def list_entries(self) -> List[LedgerEntry]:
        return list(self._entries)

    def as_dicts(self) -> list[dict]:
        return [asdict(item) for item in self._entries]
