from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List


TIMELINE_ORDER = [
    "clinical_notes",
    "labs",
    "medications",
    "allergies",
    "vaccinations",
    "documents",
]


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

    @staticmethod
    def paginate(items: List[dict], page: int, page_size: int) -> List[dict]:
        start = max(page - 1, 0) * page_size
        end = start + page_size
        return items[start:end]

    @staticmethod
    def page_count(total_items: int, page_size: int) -> int:
        if page_size <= 0:
            return 0
        return (total_items + page_size - 1) // page_size

    @staticmethod
    def ordered_timeline_keys(keys: List[str]) -> List[str]:
        order_index = {name: idx for idx, name in enumerate(TIMELINE_ORDER)}
        return sorted(keys, key=lambda key: order_index.get(key, 999))
