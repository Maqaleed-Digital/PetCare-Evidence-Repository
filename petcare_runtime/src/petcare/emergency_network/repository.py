from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional

from .models import EmergencyPartnerAvailabilityRecord


class FileEmergencyPartnerAvailabilityRepository:
    def __init__(self, base_path: str | Path) -> None:
        self.base_path = Path(base_path)
        self.records_dir = self.base_path / "partner_availability"
        self.records_dir.mkdir(parents=True, exist_ok=True)

    def _write_json(self, path: Path, payload: dict) -> None:
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        tmp_path.write_text(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        tmp_path.replace(path)

    def _read_json(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def save(self, record: EmergencyPartnerAvailabilityRecord) -> EmergencyPartnerAvailabilityRecord:
        path = self.records_dir / f"{record.id}.json"
        self._write_json(path, asdict(record))
        return record

    def get(self, record_id: str) -> Optional[EmergencyPartnerAvailabilityRecord]:
        path = self.records_dir / f"{record_id}.json"
        if not path.exists():
            return None
        return EmergencyPartnerAvailabilityRecord(**self._read_json(path))

    def list_all(self) -> List[EmergencyPartnerAvailabilityRecord]:
        records: List[EmergencyPartnerAvailabilityRecord] = []
        for path in sorted(self.records_dir.glob("*.json")):
            records.append(EmergencyPartnerAvailabilityRecord(**self._read_json(path)))
        return records

    def list_for_tenant(self, tenant_id: str) -> List[EmergencyPartnerAvailabilityRecord]:
        return [record for record in self.list_all() if record.tenant_id == tenant_id]

    def find_by_partner_clinic_id(
        self,
        tenant_id: str,
        partner_clinic_id: str,
    ) -> Optional[EmergencyPartnerAvailabilityRecord]:
        for record in self.list_for_tenant(tenant_id):
            if record.partner_clinic_id == partner_clinic_id:
                return record
        return None
