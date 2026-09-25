"""FR-16 — temperature-controlled delivery tracking (MVC-BUILD-RUNNER-001 U12).

AC-FR-16-01: a delivery of a product whose storage requirement needs temperature control (BRD P393 —
the storage range on the product's registration) carries a temperature log (P401) the owner can see
(Journey 1 P272); such a delivery cannot complete with an empty log.
AC-FR-16-04: an out-of-range reading raises an alert to the pharmacy (the tenant's staff) and is
audited. Readings are append-only and an out-of-range reading is NEVER dropped.
AC-FR-16-02/03 (EXTERNAL:LOGISTICS_PARTNER): `normalise_partner_reading` is the adapter boundary —
it refuses a reading without a timestamp or value and keeps out-of-range readings; the partner's own
interface contract is not held, so no evidence is claimed for it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Protocol

from repositories import RepositoryDenied

IN_TRANSIT, DELIVERED = "IN_TRANSIT", "DELIVERED"
SOURCE_STAFF, SOURCE_PARTNER = "STAFF", "PARTNER"
ALERT_OUT_OF_RANGE = "TEMPERATURE_OUT_OF_RANGE"


@dataclass(frozen=True)
class Delivery:
    delivery_id: str
    tenant_id: str
    owner_id: str
    product_id: str
    created_by_actor_id: str
    created_at: datetime
    temp_min_c: Optional[float] = None
    temp_max_c: Optional[float] = None

    @property
    def cold_chain(self) -> bool:
        return self.temp_min_c is not None and self.temp_max_c is not None


@dataclass(frozen=True)
class TemperatureReading:
    reading_id: str
    delivery_id: str
    tenant_id: str
    recorded_at: datetime
    celsius: float
    source: str
    recorded_by: str
    out_of_range: bool


@dataclass(frozen=True)
class DeliveryAlert:
    alert_id: str
    delivery_id: str
    tenant_id: str
    reading_id: str
    kind: str
    raised_at: datetime


@dataclass(frozen=True)
class DeliveryCompletion:
    delivery_id: str
    tenant_id: str
    completed_by_actor_id: str
    completed_at: datetime


def out_of_range(d: Delivery, celsius: float) -> bool:
    return d.cold_chain and not (d.temp_min_c <= celsius <= d.temp_max_c)


def normalise_partner_reading(raw: dict) -> tuple:
    """(recorded_at, celsius) from a partner payload, or RepositoryDenied. Never drops a value for
    being out of range — range is judged against the delivery, not here."""
    if not isinstance(raw, dict):
        raise RepositoryDenied("a reading is an object")
    ts, val = raw.get("recorded_at"), raw.get("celsius")
    if ts in (None, "") or val in (None, ""):
        raise RepositoryDenied("a reading carries a timestamp and a value")
    try:
        when = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        c = float(val)
    except (TypeError, ValueError):
        raise RepositoryDenied("a reading's timestamp or value is malformed") from None
    if when.tzinfo is None:
        raise RepositoryDenied("a reading's timestamp carries its offset")
    if c != c or c in (float("inf"), float("-inf")):
        raise RepositoryDenied("a reading's value is not a number")
    return when, c


class DeliveryRepository(Protocol):
    def create(self, d: Delivery) -> Delivery: ...
    def get(self, delivery_id: str, *, tenant_id: str): ...
    def for_tenant(self, tenant_id: str) -> list: ...
    def add_reading(self, r: TemperatureReading, alert: Optional[DeliveryAlert]) -> TemperatureReading: ...
    def readings(self, delivery_id: str, *, tenant_id: str) -> list: ...
    def alerts(self, *, tenant_id: str) -> list: ...
    def complete(self, c: DeliveryCompletion) -> DeliveryCompletion: ...
    def completion_of(self, delivery_id: str, *, tenant_id: str): ...


@dataclass
class InMemoryDeliveryRepository:
    tenants: object
    _deliveries: dict = field(default_factory=dict)
    _readings: list = field(default_factory=list)
    _alerts: list = field(default_factory=list)
    _completions: dict = field(default_factory=dict)

    def create(self, d):
        if self.tenants.get(d.tenant_id) is None:
            raise RepositoryDenied(f"tenant {d.tenant_id!r} is not registered")
        self._deliveries[d.delivery_id] = d
        return d

    def get(self, delivery_id, *, tenant_id):
        d = self._deliveries.get(delivery_id)
        return d if d is not None and d.tenant_id == tenant_id else None

    def for_tenant(self, tenant_id):
        return sorted((d for d in self._deliveries.values() if d.tenant_id == tenant_id),
                      key=lambda d: (d.created_at, d.delivery_id))

    def add_reading(self, r, alert):
        if self.get(r.delivery_id, tenant_id=r.tenant_id) is None:
            raise RepositoryDenied("reading refers to no delivery in this tenant")
        if r.delivery_id in self._completions:
            raise RepositoryDenied("the delivery is complete")
        self._readings.append(r)
        if alert is not None:
            self._alerts.append(alert)
        return r

    def readings(self, delivery_id, *, tenant_id):
        return sorted((r for r in self._readings if r.delivery_id == delivery_id and r.tenant_id == tenant_id),
                      key=lambda r: (r.recorded_at, r.reading_id))

    def alerts(self, *, tenant_id):
        return [a for a in self._alerts if a.tenant_id == tenant_id]

    def complete(self, c):
        if self.get(c.delivery_id, tenant_id=c.tenant_id) is None:
            raise RepositoryDenied("completion refers to no delivery in this tenant")
        if c.delivery_id in self._completions:
            raise RepositoryDenied("the delivery is already complete")
        self._completions[c.delivery_id] = c
        return c

    def completion_of(self, delivery_id, *, tenant_id):
        c = self._completions.get(delivery_id)
        return c if c is not None and c.tenant_id == tenant_id else None
