from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional

from .models import AIIntakeRecord, VetCopilotDraftRecord


class FileAIRuntimeRepository:
    def __init__(self, base_path: str | Path) -> None:
        self.base_path = Path(base_path)
        self.intake_dir = self.base_path / "ai_intake"
        self.copilot_dir = self.base_path / "vet_copilot"
        self.intake_dir.mkdir(parents=True, exist_ok=True)
        self.copilot_dir.mkdir(parents=True, exist_ok=True)

    def _write_json(self, path: Path, payload: dict) -> None:
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        tmp_path.write_text(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        tmp_path.replace(path)

    def _read_json(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def save_intake(self, record: AIIntakeRecord) -> AIIntakeRecord:
        path = self.intake_dir / f"{record.id}.json"
        self._write_json(path, asdict(record))
        return record

    def get_intake(self, record_id: str) -> Optional[AIIntakeRecord]:
        path = self.intake_dir / f"{record_id}.json"
        if not path.exists():
            return None
        return AIIntakeRecord(**self._read_json(path))

    def list_case_intake(self, case_id: str) -> List[AIIntakeRecord]:
        records: List[AIIntakeRecord] = []
        for path in sorted(self.intake_dir.glob("*.json")):
            payload = self._read_json(path)
            if payload.get("case_id") == case_id:
                records.append(AIIntakeRecord(**payload))
        return records

    def save_copilot_draft(self, record: VetCopilotDraftRecord) -> VetCopilotDraftRecord:
        path = self.copilot_dir / f"{record.id}.json"
        self._write_json(path, asdict(record))
        return record

    def get_copilot_draft(self, record_id: str) -> Optional[VetCopilotDraftRecord]:
        path = self.copilot_dir / f"{record_id}.json"
        if not path.exists():
            return None
        return VetCopilotDraftRecord(**self._read_json(path))

    def list_case_copilot_drafts(self, case_id: str) -> List[VetCopilotDraftRecord]:
        records: List[VetCopilotDraftRecord] = []
        for path in sorted(self.copilot_dir.glob("*.json")):
            payload = self._read_json(path)
            if payload.get("case_id") == case_id:
                records.append(VetCopilotDraftRecord(**payload))
        return records
