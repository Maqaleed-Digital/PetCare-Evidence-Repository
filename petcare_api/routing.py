"""FR-15 — smart order routing to the nearest/optimal pharmacy (MVC-BUILD-RUNNER-001 U18).

Ratified OPTIMAL_ROUTING_RULE (AC-FR-15-01):
  1. the pharmacy is eligible/licensed for every applicable supply class of the basket;
  2. it can fulfil the complete basket from stock;
  3. choose the lowest route ETA;
  4. tie-break by route distance;
  5. final deterministic tie-break by stable pharmacy identifier.
Step 1 reads the pharmacy-licence register — governed data with no served write path. Until MVC-PHARM-001 §6c
defines establishment licences, it is populated only by test fixtures: no pharmacy is live-eligible.
ETA and distance come from the maps port (AC-FR-15-02/03, EXTERNAL:MAPS_API); the served app has no maps adapter,
so routing fails closed rather than guess a distance. AC-FR-15-04: every decision is recorded with its inputs
and the chosen pharmacy, and is visible to the owner.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Protocol

from repositories import RepositoryDenied

RULE_VERSION = "OPTIMAL_ROUTING_RULE/v1 (licence, basket, ETA, distance, id)"


class RoutingUnavailable(Exception):
    """The maps provider could not produce a route (EXTERNAL:MAPS_API)."""


class MapsPort(Protocol):
    def route(self, *, origin: tuple, destination: tuple) -> tuple: ...  # (eta_seconds, distance_metres)


class UnavailableMapsAdapter:
    """The only adapter the served app is built with: no maps provider is integrated."""

    def route(self, *, origin, destination):
        raise RoutingUnavailable("no maps provider adapter is configured (EXTERNAL:MAPS_API)")


@dataclass(frozen=True)
class Candidate:
    location_id: str
    name: str
    licensed: bool
    has_basket: bool
    eta_seconds: Optional[int] = None
    distance_metres: Optional[int] = None


def choose(candidates: list) -> Optional[Candidate]:
    """Steps 1-5, deterministically. None when no pharmacy qualifies."""
    qualified = [c for c in candidates if c.licensed and c.has_basket and c.eta_seconds is not None]
    if not qualified:
        return None
    return sorted(qualified, key=lambda c: (c.eta_seconds, c.distance_metres, c.location_id))[0]


@dataclass(frozen=True)
class RoutingDecision:
    decision_id: str
    order_id: str
    tenant_id: str
    owner_latitude: float
    owner_longitude: float
    candidates: tuple  # of dicts, the inputs as evaluated
    chosen_location_id: Optional[str]
    rule_version: str
    decided_by: str
    decided_at: datetime

    def to_read_model(self) -> dict:
        return {"decision_id": self.decision_id, "order_id": self.order_id,
                "owner_location": {"latitude": self.owner_latitude, "longitude": self.owner_longitude},
                "candidates": list(self.candidates), "chosen_location_id": self.chosen_location_id,
                "rule_version": self.rule_version, "decided_at": self.decided_at.isoformat()}


class RoutingRepository(Protocol):
    def licensed(self, location_id: str, supply_class: str) -> bool: ...
    def record(self, d: RoutingDecision) -> RoutingDecision: ...
    def latest_for(self, order_id: str, *, tenant_id: str): ...


@dataclass
class InMemoryRoutingRepository:
    _licences: set = field(default_factory=set)
    _decisions: list = field(default_factory=list)

    def license(self, location_id: str, supply_class: str) -> None:
        """Governed register only (MVC-PHARM-001 §6c). No served route calls this."""
        self._licences.add((location_id, supply_class))

    def licensed(self, location_id, supply_class):
        return (location_id, supply_class) in self._licences

    def record(self, d):
        if not d.candidates:
            raise RepositoryDenied("a routing decision records the candidates it evaluated")
        self._decisions.append(d)
        return d

    def latest_for(self, order_id, *, tenant_id):
        hits = [d for d in self._decisions if d.order_id == order_id and d.tenant_id == tenant_id]
        return hits[-1] if hits else None
