from __future__ import annotations

import hashlib
import os
import re
import uuid
from typing import Iterable, Optional

from .models import ModelRegistryRecord, OutputLogRecord, PromptLogRecord, utc_now_iso
from .repository import FileAITraceRepository


class AITraceService:
    REDACTION_PATTERNS = [
        (re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE), "[REDACTED_EMAIL]"),
        (re.compile(r"(?<!\w)\+?\d[\d\-\s]{7,}\d(?!\w)"), "[REDACTED_PHONE]"),
        (re.compile(r"\b(?:[A-Fa-f0-9]{32,}|sk-[A-Za-z0-9_\-]{12,})\b"), "[REDACTED_SECRET]"),
    ]

    def __init__(self, repository: FileAITraceRepository) -> None:
        self.repository = repository

    def sanitize_text(self, value: str) -> str:
        sanitized = value.strip()
        for pattern, replacement in self.REDACTION_PATTERNS:
            sanitized = pattern.sub(replacement, sanitized)
        return sanitized

    def _hash_text(self, value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def register_model(
        self,
        *,
        model_name: str,
        model_version: str,
        provider: str,
        status: str,
        safety_level: str,
    ) -> ModelRegistryRecord:
        record = ModelRegistryRecord(
            model_name=model_name,
            model_version=model_version,
            provider=provider,
            status=status,
            safety_level=safety_level,
            registered_at=utc_now_iso(),
        )
        return self.repository.save_model(record)

    def log_prompt(
        self,
        *,
        actor_id: str,
        actor_role: str,
        tenant_id: str,
        case_id: str,
        pet_id: Optional[str],
        prompt_text: str,
        model_name: str,
        model_version: str,
        provider: str,
        context_type: str,
    ) -> PromptLogRecord:
        sanitized = self.sanitize_text(prompt_text)
        record = PromptLogRecord(
            id=str(uuid.uuid4()),
            timestamp=utc_now_iso(),
            actor_id=actor_id,
            actor_role=actor_role,
            tenant_id=tenant_id,
            case_id=case_id,
            pet_id=pet_id,
            prompt_text=sanitized,
            prompt_hash=self._hash_text(sanitized),
            model_name=model_name,
            model_version=model_version,
            provider=provider,
            context_type=context_type,
        )
        return self.repository.save_prompt(record)

    def log_output(
        self,
        *,
        prompt_id: str,
        output_text: str,
        confidence: Optional[float],
        risk_flags: Optional[Iterable[str]],
        requires_approval: bool,
        approved_by: Optional[str] = None,
        approved_at: Optional[str] = None,
    ) -> OutputLogRecord:
        if self.repository.get_prompt(prompt_id) is None:
            raise ValueError(f"Unknown prompt_id: {prompt_id}")

        sanitized = self.sanitize_text(output_text)
        normalized_flags = sorted({flag.strip() for flag in (risk_flags or []) if flag and flag.strip()})

        record = OutputLogRecord(
            id=str(uuid.uuid4()),
            prompt_id=prompt_id,
            timestamp=utc_now_iso(),
            output_text=sanitized,
            output_hash=self._hash_text(sanitized),
            confidence=confidence,
            risk_flags=normalized_flags,
            requires_approval=requires_approval,
            approved_by=approved_by,
            approved_at=approved_at,
        )
        return self.repository.save_output(record)

    def list_models(self) -> list[ModelRegistryRecord]:
        return self.repository.list_models()

    def get_prompt(self, prompt_id: str) -> Optional[PromptLogRecord]:
        return self.repository.get_prompt(prompt_id)

    def get_output(self, output_id: str) -> Optional[OutputLogRecord]:
        return self.repository.get_output(output_id)

    def get_case_trace(self, case_id: str) -> dict:
        return {
            "case_id": case_id,
            "prompts": self.repository.list_case_prompts(case_id),
            "outputs": self.repository.list_case_outputs(case_id),
        }


def build_default_trace_service() -> AITraceService:
    base_path = os.environ.get(
        "PETCARE_AI_TRACE_DIR",
        "petcare_runtime/runtime_data/ai_logging",
    )
    repository = FileAITraceRepository(base_path)
    return AITraceService(repository)
