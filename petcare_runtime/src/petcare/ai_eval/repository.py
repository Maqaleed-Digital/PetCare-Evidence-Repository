from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional

from .models import DriftSnapshotRecord, EvalCaseRecord, EvalRunRecord


class FileAIEvalRepository:
    def __init__(self, base_path: str | Path) -> None:
        self.base_path = Path(base_path)
        self.cases_dir = self.base_path / "eval_cases"
        self.runs_dir = self.base_path / "eval_runs"
        self.drift_dir = self.base_path / "drift_snapshots"
        self.cases_dir.mkdir(parents=True, exist_ok=True)
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.drift_dir.mkdir(parents=True, exist_ok=True)

    def _write_json(self, path: Path, payload: dict) -> None:
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        tmp_path.write_text(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        tmp_path.replace(path)

    def _read_json(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def save_case(self, record: EvalCaseRecord) -> EvalCaseRecord:
        path = self.cases_dir / f"{record.id}.json"
        self._write_json(path, asdict(record))
        return record

    def get_case(self, case_id: str) -> Optional[EvalCaseRecord]:
        path = self.cases_dir / f"{case_id}.json"
        if not path.exists():
            return None
        return EvalCaseRecord(**self._read_json(path))

    def list_cases(self) -> List[EvalCaseRecord]:
        records: List[EvalCaseRecord] = []
        for path in sorted(self.cases_dir.glob("*.json")):
            records.append(EvalCaseRecord(**self._read_json(path)))
        return records

    def save_run(self, record: EvalRunRecord) -> EvalRunRecord:
        path = self.runs_dir / f"{record.id}.json"
        self._write_json(path, asdict(record))
        return record

    def get_run(self, run_id: str) -> Optional[EvalRunRecord]:
        path = self.runs_dir / f"{run_id}.json"
        if not path.exists():
            return None
        return EvalRunRecord(**self._read_json(path))

    def list_runs(self) -> List[EvalRunRecord]:
        records: List[EvalRunRecord] = []
        for path in sorted(self.runs_dir.glob("*.json")):
            records.append(EvalRunRecord(**self._read_json(path)))
        return records

    def save_drift_snapshot(self, record: DriftSnapshotRecord) -> DriftSnapshotRecord:
        path = self.drift_dir / f"{record.id}.json"
        self._write_json(path, asdict(record))
        return record

    def get_drift_snapshot(self, snapshot_id: str) -> Optional[DriftSnapshotRecord]:
        path = self.drift_dir / f"{snapshot_id}.json"
        if not path.exists():
            return None
        return DriftSnapshotRecord(**self._read_json(path))

    def list_drift_snapshots(self) -> List[DriftSnapshotRecord]:
        records: List[DriftSnapshotRecord] = []
        for path in sorted(self.drift_dir.glob("*.json")):
            records.append(DriftSnapshotRecord(**self._read_json(path)))
        return records
