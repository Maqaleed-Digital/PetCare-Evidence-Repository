from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional

from .models import EvidenceExportRecord, GovernanceReportRecord


class FileAIEvidenceRepository:
    def __init__(self, base_path: str | Path) -> None:
        self.base_path = Path(base_path)
        self.exports_dir = self.base_path / "evidence_exports"
        self.reports_dir = self.base_path / "governance_reports"
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def _write_json(self, path: Path, payload: dict) -> None:
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        tmp_path.write_text(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        tmp_path.replace(path)

    def _read_json(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def save_export(self, record: EvidenceExportRecord) -> EvidenceExportRecord:
        path = self.exports_dir / f"{record.id}.json"
        self._write_json(path, asdict(record))
        return record

    def get_export(self, record_id: str) -> Optional[EvidenceExportRecord]:
        path = self.exports_dir / f"{record_id}.json"
        if not path.exists():
            return None
        return EvidenceExportRecord(**self._read_json(path))

    def list_case_exports(self, case_id: str) -> List[EvidenceExportRecord]:
        records: List[EvidenceExportRecord] = []
        for path in sorted(self.exports_dir.glob("*.json")):
            payload = self._read_json(path)
            if payload.get("case_id") == case_id:
                records.append(EvidenceExportRecord(**payload))
        return records

    def save_report(self, record: GovernanceReportRecord) -> GovernanceReportRecord:
        path = self.reports_dir / f"{record.id}.json"
        self._write_json(path, asdict(record))
        return record

    def get_report(self, record_id: str) -> Optional[GovernanceReportRecord]:
        path = self.reports_dir / f"{record_id}.json"
        if not path.exists():
            return None
        return GovernanceReportRecord(**self._read_json(path))

    def list_reports(self) -> List[GovernanceReportRecord]:
        records: List[GovernanceReportRecord] = []
        for path in sorted(self.reports_dir.glob("*.json")):
            records.append(GovernanceReportRecord(**self._read_json(path)))
        return records
