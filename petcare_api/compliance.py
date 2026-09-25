"""FR-30 — SFDA compliance reporting automation (MVC-BUILD-RUNNER-001 U16).

AC-FR-30-01: reports are generated AUTOMATICALLY from recorded events. The controlled-substance report is
derived from the stock ledger (every CONTROLLED movement, including dispenses); every figure carries the
movement ids it sums, and a stored report re-derives to the same content hash (traceability).
AC-FR-30-02: antimicrobial prescribing is recorded as structured data — the prescription names its
product, whose REGISTRATION carries the antimicrobial agent and class — and aggregates by agent, class,
species, practitioner and period with a coverage statement on every output (REQ-MVC-6.20). No text search.
AC-FR-30-03: a notifiable-disease case carries its statutory clock from detection: report_due_at =
detected_at + the window from the notifiable-disease REGISTER (a governed reference, never typed by staff).
AC-FR-30-04/05 (EXTERNAL:SFDA): submission to the regulator is not built; interface not held.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Protocol

from repositories import RepositoryDenied

KIND_CONTROLLED = "CONTROLLED_SUBSTANCE_AUDIT"
GROUP_KEYS = ("agent", "agent_class", "species", "practitioner", "period")


@dataclass(frozen=True)
class NotifiableDisease:
    disease_code: str
    name: str
    report_within_hours: int
    source: str


@dataclass(frozen=True)
class NotifiableCase:
    case_id: str
    tenant_id: str
    pet_id: str
    disease_code: str
    detected_at: datetime
    report_due_at: datetime
    recorded_by: str
    created_at: datetime


@dataclass(frozen=True)
class CaseReport:
    case_id: str
    tenant_id: str
    reported_by: str
    reported_at: datetime
    reference: str


@dataclass(frozen=True)
class ReportHeader:
    report_id: str
    tenant_id: str
    kind: str
    period_from: datetime
    period_to: datetime
    generated_by: str
    generated_at: datetime
    row_count: int
    content_sha256: str


def controlled_rows(movements: list, period_from: datetime, period_to: datetime) -> list:
    """Every CONTROLLED movement in [from, to), one row per recorded movement — nothing assembled by hand."""
    rows = [{"movement_id": m.movement_id, "at": m.created_at.isoformat(), "location_id": m.location_id,
             "product_id": m.product_id, "batch": m.batch, "reason": m.reason, "quantity_delta": m.quantity_delta,
             "actor_id": m.actor_id, "prescription_id": m.prescription_id}
            for m in movements if m.supply_class == "CONTROLLED" and period_from <= m.created_at < period_to]
    return sorted(rows, key=lambda r: (r["at"], r["movement_id"]))


def totals(rows: list) -> list:
    """Per (product, batch) net movement, each carrying the movement ids it sums (traceable figures)."""
    acc: dict = {}
    for r in rows:
        k = (r["product_id"], r["batch"])
        a = acc.setdefault(k, {"product_id": k[0], "batch": k[1], "net_quantity": 0, "movement_ids": []})
        a["net_quantity"] += r["quantity_delta"]
        a["movement_ids"].append(r["movement_id"])
    return [acc[k] for k in sorted(acc)]


def content_hash(rows: list) -> str:
    return hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def antimicrobial_aggregate(records: list, group_by: tuple) -> dict:
    """records: dicts with agent, agent_class, species, practitioner, period, prescription_id.
    Returns grouped counts plus the coverage statement (how many records carry each grouped field)."""
    if not group_by or any(g not in GROUP_KEYS for g in group_by):
        raise RepositoryDenied(f"group_by is a non-empty subset of {GROUP_KEYS}")
    groups: dict = {}
    for r in records:
        k = tuple(r[g] for g in group_by)
        g = groups.setdefault(k, {**{f: r[f] for f in group_by}, "prescriptions": 0, "prescription_ids": []})
        g["prescriptions"] += 1
        g["prescription_ids"].append(r["prescription_id"])
    unresolved = [r["prescription_id"] for r in records if r["species"] == "UNRESOLVED"]
    n = len(records)
    return {"group_by": list(group_by), "rows": [groups[k] for k in sorted(groups, key=lambda x: tuple(map(str, x)))],
            "coverage": {"antimicrobial_prescriptions": n, "species_resolved": n - len(unresolved),
                         "species_unresolved": unresolved,
                         "statement": (f"{n} antimicrobial prescription(s) recorded with a registered product in the "
                                       f"period; {n - len(unresolved)} with the pet's species from its stored profile, "
                                       f"{len(unresolved)} UNRESOLVED (listed). Prescriptions naming no product are "
                                       f"outside this register.")}}


def clock(case: NotifiableCase, reported: Optional[CaseReport], now: datetime) -> dict:
    status = "REPORTED" if reported else ("OVERDUE" if now > case.report_due_at else "OPEN")
    return {"detected_at": case.detected_at.isoformat(), "report_due_at": case.report_due_at.isoformat(),
            "status": status, "reported_at": reported.reported_at.isoformat() if reported else None,
            "hours_remaining": None if reported else round((case.report_due_at - now).total_seconds() / 3600, 2)}


class ComplianceRepository(Protocol):
    def link_product(self, prescription_id: str, tenant_id: str, product_id: str, at: datetime) -> None: ...
    def product_of(self, prescription_id: str, *, tenant_id: str): ...
    def disease(self, code: str): ...
    def add_case(self, c: NotifiableCase) -> NotifiableCase: ...
    def cases(self, *, tenant_id: str) -> list: ...
    def get_case(self, case_id: str, *, tenant_id: str): ...
    def report_case(self, r: CaseReport) -> CaseReport: ...
    def report_of(self, case_id: str, *, tenant_id: str): ...
    def save_report(self, h: ReportHeader) -> ReportHeader: ...
    def get_report(self, report_id: str, *, tenant_id: str): ...


@dataclass
class InMemoryComplianceRepository:
    _links: dict = field(default_factory=dict)
    _diseases: dict = field(default_factory=dict)
    _cases: dict = field(default_factory=dict)
    _reports: dict = field(default_factory=dict)
    _headers: dict = field(default_factory=dict)

    def link_product(self, prescription_id, tenant_id, product_id, at):
        self._links[prescription_id] = (tenant_id, product_id)

    def product_of(self, prescription_id, *, tenant_id):
        v = self._links.get(prescription_id)
        return v[1] if v and v[0] == tenant_id else None

    def register_disease(self, d: NotifiableDisease) -> NotifiableDisease:
        """Governed reference only (the notifiable-disease register). No served route calls this."""
        if d.report_within_hours <= 0:
            raise RepositoryDenied("a statutory window is a positive number of hours")
        self._diseases[d.disease_code] = d
        return d

    def disease(self, code):
        return self._diseases.get(code)

    def add_case(self, c):
        if c.report_due_at is None or c.detected_at is None:
            raise RepositoryDenied("a notifiable case carries its reporting clock")
        self._cases[c.case_id] = c
        return c

    def cases(self, *, tenant_id):
        return sorted((c for c in self._cases.values() if c.tenant_id == tenant_id), key=lambda c: (c.report_due_at, c.case_id))

    def get_case(self, case_id, *, tenant_id):
        c = self._cases.get(case_id)
        return c if c is not None and c.tenant_id == tenant_id else None

    def report_case(self, r):
        if self.get_case(r.case_id, tenant_id=r.tenant_id) is None:
            raise RepositoryDenied("report refers to no case in this tenant")
        if r.case_id in self._reports:
            raise RepositoryDenied("the case is already reported")
        self._reports[r.case_id] = r
        return r

    def report_of(self, case_id, *, tenant_id):
        r = self._reports.get(case_id)
        return r if r is not None and r.tenant_id == tenant_id else None

    def save_report(self, h):
        self._headers[h.report_id] = h
        return h

    def get_report(self, report_id, *, tenant_id):
        h = self._headers.get(report_id)
        return h if h is not None and h.tenant_id == tenant_id else None
