from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional

from .models import ModelRegistryRecord, OutputLogRecord, PromptLogRecord


class FileAITraceRepository:
    def __init__(self, base_path: str | Path) -> None:
        self.base_path = Path(base_path)
        self.prompts_dir = self.base_path / "prompt_logs"
        self.outputs_dir = self.base_path / "output_logs"
        self.models_dir = self.base_path / "model_registry"
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def _write_json(self, path: Path, payload: dict) -> None:
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        tmp_path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        tmp_path.replace(path)

    def _read_json(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def save_prompt(self, record: PromptLogRecord) -> PromptLogRecord:
        path = self.prompts_dir / f"{record.id}.json"
        self._write_json(path, asdict(record))
        return record

    def save_output(self, record: OutputLogRecord) -> OutputLogRecord:
        path = self.outputs_dir / f"{record.id}.json"
        self._write_json(path, asdict(record))
        return record

    def save_model(self, record: ModelRegistryRecord) -> ModelRegistryRecord:
        key = f"{record.provider}__{record.model_name}__{record.model_version}.json"
        path = self.models_dir / key
        self._write_json(path, asdict(record))
        return record

    def get_prompt(self, prompt_id: str) -> Optional[PromptLogRecord]:
        path = self.prompts_dir / f"{prompt_id}.json"
        if not path.exists():
            return None
        return PromptLogRecord(**self._read_json(path))

    def get_output(self, output_id: str) -> Optional[OutputLogRecord]:
        path = self.outputs_dir / f"{output_id}.json"
        if not path.exists():
            return None
        return OutputLogRecord(**self._read_json(path))

    def list_models(self) -> List[ModelRegistryRecord]:
        records: List[ModelRegistryRecord] = []
        for path in sorted(self.models_dir.glob("*.json")):
            records.append(ModelRegistryRecord(**self._read_json(path)))
        return records

    def list_case_prompts(self, case_id: str) -> List[PromptLogRecord]:
        records: List[PromptLogRecord] = []
        for path in sorted(self.prompts_dir.glob("*.json")):
            payload = self._read_json(path)
            if payload.get("case_id") == case_id:
                records.append(PromptLogRecord(**payload))
        return records

    def list_case_outputs(self, case_id: str) -> List[OutputLogRecord]:
        prompt_ids = {record.id for record in self.list_case_prompts(case_id)}
        records: List[OutputLogRecord] = []
        for path in sorted(self.outputs_dir.glob("*.json")):
            payload = self._read_json(path)
            if payload.get("prompt_id") in prompt_ids:
                records.append(OutputLogRecord(**payload))
        return records
