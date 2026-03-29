from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional

from .models import ApprovalResolutionRecord, ClinicalSignoffBindingRecord


class FileAIResolutionRepository:
    def __init__(self, base_path: str | Path) -> None:
        self.base_path = Path(base_path)
        self.resolutions_dir = self.base_path / "approval_resolutions"
        self.signoffs_dir = self.base_path / "clinical_signoffs"
        self.resolutions_dir.mkdir(parents=True, exist_ok=True)
        self.signoffs_dir.mkdir(parents=True, exist_ok=True)

    def _write_json(self, path: Path, payload: dict) -> None:
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        tmp_path.write_text(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        tmp_path.replace(path)

    def _read_json(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def save_resolution(self, record: ApprovalResolutionRecord) -> ApprovalResolutionRecord:
        path = self.resolutions_dir / f"{record.id}.json"
        self._write_json(path, asdict(record))
        return record

    def get_resolution(self, record_id: str) -> Optional[ApprovalResolutionRecord]:
        path = self.resolutions_dir / f"{record_id}.json"
        if not path.exists():
            return None
        return ApprovalResolutionRecord(**self._read_json(path))

    def list_case_resolutions(self, case_id: str) -> List[ApprovalResolutionRecord]:
        records: List[ApprovalResolutionRecord] = []
        for path in sorted(self.resolutions_dir.glob("*.json")):
            payload = self._read_json(path)
            if payload.get("case_id") == case_id:
                records.append(ApprovalResolutionRecord(**payload))
        return records

    def find_resolution_for_artifact(self, artifact_type: str, artifact_id: str) -> Optional[ApprovalResolutionRecord]:
        for path in sorted(self.resolutions_dir.glob("*.json")):
            payload = self._read_json(path)
            if payload.get("artifact_type") == artifact_type and payload.get("artifact_id") == artifact_id:
                return ApprovalResolutionRecord(**payload)
        return None

    def save_signoff(self, record: ClinicalSignoffBindingRecord) -> ClinicalSignoffBindingRecord:
        path = self.signoffs_dir / f"{record.id}.json"
        self._write_json(path, asdict(record))
        return record

    def get_signoff(self, record_id: str) -> Optional[ClinicalSignoffBindingRecord]:
        path = self.signoffs_dir / f"{record_id}.json"
        if not path.exists():
            return None
        return ClinicalSignoffBindingRecord(**self._read_json(path))

    def list_case_signoffs(self, case_id: str) -> List[ClinicalSignoffBindingRecord]:
        records: List[ClinicalSignoffBindingRecord] = []
        for path in sorted(self.signoffs_dir.glob("*.json")):
            payload = self._read_json(path)
            if payload.get("case_id") == case_id:
                records.append(ClinicalSignoffBindingRecord(**payload))
        return records

    def find_signoff_for_artifact(self, artifact_type: str, artifact_id: str) -> Optional[ClinicalSignoffBindingRecord]:
        for path in sorted(self.signoffs_dir.glob("*.json")):
            payload = self._read_json(path)
            if payload.get("artifact_type") == artifact_type and payload.get("artifact_id") == artifact_id:
                return ClinicalSignoffBindingRecord(**payload)
        return None
