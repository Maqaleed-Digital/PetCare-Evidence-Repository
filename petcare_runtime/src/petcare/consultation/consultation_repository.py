from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional

from petcare.consultation.consultation_service import ConsultationNote, ConsultationSession


class ConsultationRepository:
    def __init__(self, storage_path: str) -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict:
        if not self.storage_path.exists():
            return {"sessions": {}, "notes": {}}
        return json.loads(self.storage_path.read_text(encoding="utf-8"))

    def save(self, data: dict) -> None:
        tmp = self.storage_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp.replace(self.storage_path)

    def add_session(self, session: ConsultationSession) -> None:
        data = self.load()
        data.setdefault("sessions", {})[session.session_id] = asdict(session)
        self.save(data)

    def update_session(self, session: ConsultationSession) -> None:
        data = self.load()
        data.setdefault("sessions", {})[session.session_id] = asdict(session)
        self.save(data)

    def get_session(self, session_id: str) -> Optional[ConsultationSession]:
        data = self.load()
        raw = data.get("sessions", {}).get(session_id)
        if raw is None:
            return None
        return ConsultationSession(**raw)

    def add_note(self, note: ConsultationNote) -> None:
        data = self.load()
        data.setdefault("notes", {}).setdefault(note.session_id, []).append(asdict(note))
        self.save(data)

    def update_note(self, note: ConsultationNote) -> None:
        """Replace existing note in-place by note_id. Appends if not found."""
        data = self.load()
        entries = data.setdefault("notes", {}).setdefault(note.session_id, [])
        for idx, entry in enumerate(entries):
            if entry.get("note_id") == note.note_id:
                entries[idx] = asdict(note)
                self.save(data)
                return
        entries.append(asdict(note))
        self.save(data)

    def list_notes_for_session(self, session_id: str) -> List[ConsultationNote]:
        data = self.load()
        raw = data.get("notes", {}).get(session_id, [])
        return [ConsultationNote(**item) for item in raw]
