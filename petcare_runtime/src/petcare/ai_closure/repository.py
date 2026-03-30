from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional

from .models import EPClosureChecklistRecord, EPGovernanceSealRecord


class FileAIClosureRepository:
    def __init__(self, base_path: str | Path) -> None:
        self.base_path = Path(base_path)
        self.checklists_dir = self.base_path / "ep_closure_checklists"
        self.seals_dir = self.base_path / "ep_governance_seals"
        self.checklists_dir.mkdir(parents=True, exist_ok=True)
        self.seals_dir.mkdir(parents=True, exist_ok=True)

    def _write_json(self, path: Path, payload: dict) -> None:
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        tmp_path.write_text(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        tmp_path.replace(path)

    def _read_json(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def save_checklist(self, record: EPClosureChecklistRecord) -> EPClosureChecklistRecord:
        path = self.checklists_dir / f"{record.tenant_id}__{record.epic_id}.json"
        self._write_json(path, asdict(record))
        return record

    def get_checklist(self, tenant_id: str, epic_id: str) -> Optional[EPClosureChecklistRecord]:
        path = self.checklists_dir / f"{tenant_id}__{epic_id}.json"
        if not path.exists():
            return None
        return EPClosureChecklistRecord(**self._read_json(path))

    def save_seal(self, record: EPGovernanceSealRecord) -> EPGovernanceSealRecord:
        path = self.seals_dir / f"{record.id}.json"
        self._write_json(path, asdict(record))
        return record

    def get_seal(self, record_id: str) -> Optional[EPGovernanceSealRecord]:
        path = self.seals_dir / f"{record_id}.json"
        if not path.exists():
            return None
        return EPGovernanceSealRecord(**self._read_json(path))

    def find_seal(self, tenant_id: str, epic_id: str) -> Optional[EPGovernanceSealRecord]:
        for path in sorted(self.seals_dir.glob("*.json")):
            payload = self._read_json(path)
            if payload.get("tenant_id") == tenant_id and payload.get("epic_id") == epic_id:
                return EPGovernanceSealRecord(**payload)
        return None

    def list_seals(self) -> List[EPGovernanceSealRecord]:
        records: List[EPGovernanceSealRecord] = []
        for path in sorted(self.seals_dir.glob("*.json")):
            records.append(EPGovernanceSealRecord(**self._read_json(path)))
        return records
