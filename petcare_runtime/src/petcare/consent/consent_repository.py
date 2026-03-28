from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List

from petcare.consent.consent_service import ConsentRecord


class ConsentRepository:
    def __init__(self, storage_path: str) -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> Dict[str, List[dict]]:
        if not self.storage_path.exists():
            return {"consent_records": {}}
        return json.loads(self.storage_path.read_text(encoding="utf-8"))

    def save(self, data: Dict[str, List[dict]]) -> None:
        tmp = self.storage_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp.replace(self.storage_path)

    def add_record(self, record: ConsentRecord) -> None:
        data = self.load()
        pet_bucket = data.setdefault("consent_records", {})
        pet_bucket.setdefault(record.pet_id, []).append(asdict(record))
        self.save(data)

    def list_records_for_pet(self, pet_id: str) -> List[ConsentRecord]:
        data = self.load()
        raw = data.get("consent_records", {}).get(pet_id, [])
        return [ConsentRecord(**item) for item in raw]

    def latest_matching_record(
        self,
        pet_id: str,
        required_scope: str,
        required_purpose: str,
        required_role: str,
    ) -> ConsentRecord | None:
        candidates = self.list_records_for_pet(pet_id)
        matches = [
            record for record in candidates
            if record.consent_scope == required_scope
            and record.purpose_of_use == required_purpose
            and record.granted_to_role == required_role
        ]
        if not matches:
            return None
        matches.sort(key=lambda item: item.granted_at, reverse=True)
        return matches[0]
