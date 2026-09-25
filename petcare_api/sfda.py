"""FR-14 AC-FR-14-06 — the SFDA prescription-validation port (MVC-BUILD-RUNNER-001 U9).

Ratified: "SFDA integration remains adapter/contract-testable before live API access.
Absence of external API access does not permit fabricated integration proof."
This module is the PORT and its contract, not an integration. Dependency
EXTERNAL:SFDA_API stays open until a live adapter exists and is proven.

CONTRACT: only an explicit VALID answer is valid. INVALID, UNKNOWN (SFDA does not know
the prescription) and UNAVAILABLE (no adapter configured, or the interface did not
answer) are all NOT valid. The served deployment has no live adapter, so it answers
UNAVAILABLE for every prescription.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

VALID, INVALID, UNKNOWN, UNAVAILABLE = "VALID", "INVALID", "UNKNOWN", "UNAVAILABLE"
STATUSES = (VALID, INVALID, UNKNOWN, UNAVAILABLE)


@dataclass(frozen=True)
class SfdaResult:
    status: str
    detail: str = ""

    @property
    def valid(self) -> bool:
        return self.status == VALID


class SfdaValidationPort(Protocol):
    def validate(self, *, prescription_id: str, medication_name: str) -> SfdaResult: ...


class UnconfiguredSfdaAdapter:
    """The only adapter the served app is built with: no live SFDA access exists."""

    def validate(self, *, prescription_id, medication_name):
        return SfdaResult(UNAVAILABLE, "no SFDA prescription-validation adapter is configured (EXTERNAL:SFDA_API)")


def normalise(raw: object) -> SfdaResult:
    """Map any adapter answer onto the contract, failing closed on anything unexpected."""
    if isinstance(raw, SfdaResult) and raw.status in STATUSES:
        return raw
    return SfdaResult(UNKNOWN, "unrecognised adapter answer")
