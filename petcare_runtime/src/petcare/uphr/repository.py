from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List


class FileBackedRepository:
    def __init__(self, storage_path: str) -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> Dict[str, Any]:
        if not self.storage_path.exists():
            return {
                "pets": {},
                "allergies": {},
                "medications": {},
                "vaccinations": {},
                "labs": {},
                "clinical_notes": {},
                "documents": {},
            }
        return json.loads(self.storage_path.read_text(encoding="utf-8"))

    def save(self, data: Dict[str, Any]) -> None:
        tmp = self.storage_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp.replace(self.storage_path)

    @staticmethod
    def append_record(bucket: Dict[str, List[Dict[str, Any]]], pet_id: str, record: Any) -> None:
        bucket.setdefault(pet_id, []).append(asdict(record))
