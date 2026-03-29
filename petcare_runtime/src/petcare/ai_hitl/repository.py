from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional

from .models import ApprovalDecisionRecord, ApprovalGateRecord


class FileAIHITLRepository:
    def __init__(self, base_path: str | Path) -> None:
        self.base_path = Path(base_path)
        self.gates_dir = self.base_path / "approval_gates"
        self.decisions_dir = self.base_path / "approval_decisions"
        self.gates_dir.mkdir(parents=True, exist_ok=True)
        self.decisions_dir.mkdir(parents=True, exist_ok=True)

    def _write_json(self, path: Path, payload: dict) -> None:
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        tmp_path.write_text(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        tmp_path.replace(path)

    def _read_json(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def save_gate(self, record: ApprovalGateRecord) -> ApprovalGateRecord:
        path = self.gates_dir / f"{record.output_id}.json"
        self._write_json(path, asdict(record))
        return record

    def get_gate(self, output_id: str) -> Optional[ApprovalGateRecord]:
        path = self.gates_dir / f"{output_id}.json"
        if not path.exists():
            return None
        return ApprovalGateRecord(**self._read_json(path))

    def save_decision(self, record: ApprovalDecisionRecord) -> ApprovalDecisionRecord:
        path = self.decisions_dir / f"{record.id}.json"
        self._write_json(path, asdict(record))
        return record

    def list_output_decisions(self, output_id: str) -> List[ApprovalDecisionRecord]:
        records: List[ApprovalDecisionRecord] = []
        for path in sorted(self.decisions_dir.glob("*.json")):
            payload = self._read_json(path)
            if payload.get("output_id") == output_id:
                records.append(ApprovalDecisionRecord(**payload))
        return records

    def list_case_gates(self, case_id: str) -> List[ApprovalGateRecord]:
        records: List[ApprovalGateRecord] = []
        for path in sorted(self.gates_dir.glob("*.json")):
            payload = self._read_json(path)
            if payload.get("case_id") == case_id:
                records.append(ApprovalGateRecord(**payload))
        return records
