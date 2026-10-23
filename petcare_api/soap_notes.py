"""J-V3 — the consultation workspace: SOAP note drafts with templates (MVC-EPC-D-001 Lane D, D3c; R21.4 D3 veterinarian journeys;
screen CV-05).

The consultation's OWN veterinarian writes a clinical note in four SOAP sections (subjective, objective, assessment, plan) while
working the consultation. Each save is a new insert-only VERSION; the latest version is the draft in force and earlier versions
stay as the record of what was written when. A draft is UNSIGNED: signing a note and making it immutable is journey J-V4
(BRD #3), which is not built here, so nothing in this module signs, locks or finalises a note.

Templates are STRUCTURAL only (recorded assumption D3C-SOAP-TEMPLATES-STRUCTURAL): each gives per-section starter lines — headings
with nothing after them — in Arabic and English. A template never carries a finding, a diagnosis, a dose or any clinical value,
and applying one never overwrites what the veterinarian has already written (the web screen fills empty sections only).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Protocol

from repositories import RepositoryDenied

SECTIONS = ("subjective", "objective", "assessment", "plan")
MAX_SECTION = 4000
STATUS_DRAFT = "DRAFT"

#: template_id -> {"name": {lang: str}, "sections": {section: {lang: str}}}. Headings only — no clinical content.
TEMPLATES = {
    "SOAP_GENERAL": {
        "name": {"ar": "استشارة عامة", "en": "General consultation"},
        "sections": {
            "subjective": {"ar": "سبب الزيارة:\nمدة العلامات:\nالأكل والشرب:", "en": "Reason for visit:\nDuration of signs:\nEating and drinking:"},
            "objective": {"ar": "الوزن (كغ):\nالحرارة:\nنتائج الفحص:", "en": "Weight (kg):\nTemperature:\nExamination findings:"},
            "assessment": {"ar": "التقييم:\nالتشخيصات التفريقية:", "en": "Assessment:\nDifferential diagnoses:"},
            "plan": {"ar": "العلاج:\nالرعاية المنزلية:\nالمتابعة:", "en": "Treatment:\nHome care:\nFollow-up:"},
        },
    },
    "SOAP_FOLLOW_UP": {
        "name": {"ar": "زيارة متابعة", "en": "Follow-up visit"},
        "sections": {
            "subjective": {"ar": "التطور منذ الزيارة السابقة:\nملاحظات المالك:", "en": "Progress since the last visit:\nOwner's observations:"},
            "objective": {"ar": "الوزن (كغ):\nنتائج إعادة الفحص:", "en": "Weight (kg):\nRe-examination findings:"},
            "assessment": {"ar": "الاستجابة للعلاج:", "en": "Response to treatment:"},
            "plan": {"ar": "تعديلات العلاج:\nالمتابعة القادمة:", "en": "Changes to treatment:\nNext follow-up:"},
        },
    },
}


def templates_read_model() -> list:
    return [{"template_id": tid, "name": t["name"], "sections": t["sections"]} for tid, t in TEMPLATES.items()]


@dataclass(frozen=True)
class SoapDraft:
    draft_id: str
    session_id: str
    tenant_id: str
    veterinarian_id: str
    template_id: Optional[str]
    subjective: str
    objective: str
    assessment: str
    plan: str
    saved_at: datetime

    def to_read_model(self) -> dict:
        return {"draft_id": self.draft_id, "status": STATUS_DRAFT, "template_id": self.template_id,
                "subjective": self.subjective, "objective": self.objective, "assessment": self.assessment, "plan": self.plan,
                "saved_by_actor_id": self.veterinarian_id, "saved_at": self.saved_at.isoformat()}


def validate_draft(d: SoapDraft) -> None:
    if not (d.draft_id and d.session_id and d.tenant_id and d.veterinarian_id and d.veterinarian_id.strip()):
        raise RepositoryDenied("a SOAP draft names its consultation, tenant and veterinarian")
    if d.template_id is not None and d.template_id not in TEMPLATES:
        raise RepositoryDenied(f"unknown SOAP template {d.template_id!r}")
    texts = [getattr(d, s) for s in SECTIONS]
    if any(len(t) > MAX_SECTION for t in texts):
        raise RepositoryDenied(f"a SOAP section is at most {MAX_SECTION} characters")
    if not any(t.strip() for t in texts):
        raise RepositoryDenied("a SOAP draft has at least one written section")


class SoapDraftRepository(Protocol):
    def save(self, d: SoapDraft) -> SoapDraft: ...
    def latest(self, session_id: str, *, tenant_id: str) -> Optional[SoapDraft]: ...
    def versions(self, session_id: str, *, tenant_id: str) -> int: ...


@dataclass
class InMemorySoapDraftRepository:
    _rows: list = field(default_factory=list)

    def save(self, d):
        validate_draft(d)
        self._rows.append(d)
        return d

    def _of(self, session_id, tenant_id):
        return [d for d in self._rows if d.session_id == session_id and d.tenant_id == tenant_id]

    def latest(self, session_id, *, tenant_id):
        mine = self._of(session_id, tenant_id)
        return max(mine, key=lambda d: (d.saved_at, d.draft_id)) if mine else None

    def versions(self, session_id, *, tenant_id):
        return len(self._of(session_id, tenant_id))
