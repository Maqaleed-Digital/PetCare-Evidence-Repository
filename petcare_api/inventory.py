"""FR-13 — real-time multi-location inventory (MVC-BUILD-RUNNER-001 U8).

AC-FR-13-01: stock is visible per location for every pharmacy location in the tenant;
a change at one location reaches every authorised session of the tenant within the
ratified bound (REAL_TIME_BOUND = 5 s, p95), and never another tenant.
AC-FR-13-02: stock is an immutable movement ledger with a DERIVED balance
(REQ-MVC-7.30). Nothing here stores a quantity; a balance is the sum of the
movements for (location, product, batch). No repository method updates or deletes a
movement; a correction is a new compensating movement.
AC-FR-13-04 (MVC-PHARM-001 §5, dependency COUNSEL:L-2): POM, RESTRICTED and
CONTROLLED stock is excluded from non-veterinarian handling until counsel. The class
comes from product registration, never from the caller or tenant staff
(AC-FR-04-03); an unregistered product is treated as POM (fail closed).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Optional, Protocol

from repositories import RepositoryDenied

GENERAL, OTC, POM, RESTRICTED, CONTROLLED = "GENERAL", "OTC", "POM", "RESTRICTED", "CONTROLLED"
SUPPLY_CLASSES = (GENERAL, OTC, POM, RESTRICTED, CONTROLLED)
#: MVC-PHARM-001 §5: handled by a veterinarian only, until counsel (L-2) determines otherwise.
VETERINARIAN_ONLY = frozenset({POM, RESTRICTED, CONTROLLED})
#: AC-FR-04-03: a product with no verified registration is treated as POM.
UNREGISTERED_CLASS = POM
REGISTRATION_SOURCE = "SFDA_REGISTRATION"

RECEIPT, ADJUSTMENT, TRANSFER_OUT, TRANSFER_IN = "RECEIPT", "ADJUSTMENT", "TRANSFER_OUT", "TRANSFER_IN"
#: FR-14 (U9, migration 0042): stock leaving to a customer.
SUPPLY = "SUPPLY"
REASONS = (RECEIPT, ADJUSTMENT, TRANSFER_OUT, TRANSFER_IN, SUPPLY)


def prescription_required(supply_class: str) -> bool:
    """AC-FR-14-03: the prescription gate applies to POM/RESTRICTED/CONTROLLED only."""
    return supply_class in VETERINARIAN_ONLY


@dataclass(frozen=True)
class InventoryLocation:
    location_id: str
    tenant_id: str
    name: str
    created_at: datetime

    def to_read_model(self) -> dict:
        d = asdict(self); d["created_at"] = self.created_at.isoformat(); return d


@dataclass(frozen=True)
class ProductRegistration:
    product_id: str
    name: str
    supply_class: str
    source: str
    registered_at: datetime
    #: FR-16 (U12): storage requirement (BRD P393); both set = temperature-controlled.
    storage_min_c: Optional[float] = None
    storage_max_c: Optional[float] = None


@dataclass(frozen=True)
class StockMovement:
    movement_id: str
    tenant_id: str
    location_id: str
    product_id: str
    batch: str
    quantity_delta: int
    reason: str
    supply_class: str
    actor_id: str
    actor_role: str
    created_at: datetime
    transfer_id: Optional[str] = None
    prescription_id: Optional[str] = None
    #: FR-19 (U13): BRD P392 expiry of the batch, recorded on receipt.
    batch_expiry: Optional[date] = None

    def to_read_model(self) -> dict:
        d = asdict(self); d["created_at"] = self.created_at.isoformat()
        d["batch_expiry"] = self.batch_expiry.isoformat() if self.batch_expiry else None
        return d


def validate_movement(m: StockMovement) -> None:
    if m.reason not in REASONS:
        raise RepositoryDenied(f"unknown movement reason {m.reason!r}")
    if m.supply_class not in SUPPLY_CLASSES:
        raise RepositoryDenied(f"unknown supply class {m.supply_class!r}")
    if not isinstance(m.quantity_delta, int) or m.quantity_delta == 0:
        raise RepositoryDenied("a movement changes stock by a non-zero whole quantity")
    if not m.product_id.strip() or not m.batch.strip():
        raise RepositoryDenied("a movement names a product and a batch")
    if m.reason == SUPPLY and (m.quantity_delta >= 0
                               or (prescription_required(m.supply_class) and not m.prescription_id)):
        raise RepositoryDenied("a supply removes stock, and POM/RESTRICTED/CONTROLLED supply cites a prescription")


def balance_rows(movements, supply_class_of) -> list:
    """The derived balance: SUM(quantity_delta) per (location, product, batch)."""
    totals: dict = {}
    expiry: dict = {}
    for m in movements:
        k = (m.location_id, m.product_id, m.batch)
        totals[k] = totals.get(k, 0) + m.quantity_delta
        if m.batch_expiry is not None:
            expiry[k] = max(expiry.get(k, m.batch_expiry), m.batch_expiry)
    return [{"location_id": k[0], "product_id": k[1], "batch": k[2], "quantity": q,
             "supply_class": supply_class_of(k[1]),
             "batch_expiry": expiry[k].isoformat() if k in expiry else None} for k, q in sorted(totals.items())]


class InventoryRepository(Protocol):
    def add_location(self, loc: InventoryLocation) -> InventoryLocation: ...
    def locations(self, *, tenant_id: str) -> list: ...
    def get_location(self, location_id: str, *, tenant_id: str): ...
    def supply_class_of(self, product_id: str) -> str: ...
    def record(self, movements: list) -> list: ...
    def movements(self, *, tenant_id: str, location_id: Optional[str] = None) -> list: ...
    def balances(self, *, tenant_id: str, location_id: Optional[str] = None,
                 product_id: Optional[str] = None) -> list: ...


@dataclass
class InMemoryInventoryRepository:
    tenants: object
    _locations: dict = field(default_factory=dict)
    _products: dict = field(default_factory=dict)
    _movements: list = field(default_factory=list)

    def add_location(self, loc):
        if self.tenants.get(loc.tenant_id) is None:
            raise RepositoryDenied(f"tenant {loc.tenant_id!r} is not registered")
        if not loc.name.strip():
            raise RepositoryDenied("a location needs a name")
        self._locations[loc.location_id] = loc
        return loc

    def locations(self, *, tenant_id):
        return sorted((x for x in self._locations.values() if x.tenant_id == tenant_id),
                      key=lambda x: (x.name, x.location_id))

    def get_location(self, location_id, *, tenant_id):
        x = self._locations.get(location_id)
        return x if x is not None and x.tenant_id == tenant_id else None

    def register_product(self, p: ProductRegistration) -> ProductRegistration:
        """Registration feed only (AC-FR-04-03). No served route calls this."""
        if p.supply_class not in SUPPLY_CLASSES or p.source != REGISTRATION_SOURCE:
            raise RepositoryDenied("a registration carries a known class from the registration source")
        self._products[p.product_id] = p
        return p

    def supply_class_of(self, product_id):
        p = self._products.get(product_id)
        return p.supply_class if p is not None else UNREGISTERED_CLASS

    def storage_range_of(self, product_id):
        """(min, max) °C when the registration requires temperature control, else None."""
        p = self._products.get(product_id)
        return (p.storage_min_c, p.storage_max_c) if p is not None and p.storage_min_c is not None else None

    def _balance(self, tenant_id, location_id, product_id, batch):
        return sum(m.quantity_delta for m in self._movements if (m.tenant_id, m.location_id, m.product_id, m.batch)
                   == (tenant_id, location_id, product_id, batch))

    def record(self, movements):
        """All-or-nothing: every movement is validated and no balance may go negative."""
        for m in movements:
            validate_movement(m)
            if self.get_location(m.location_id, tenant_id=m.tenant_id) is None:
                raise RepositoryDenied("movement refers to no location in this tenant")
        pending: dict = {}
        for m in movements:
            k = (m.tenant_id, m.location_id, m.product_id, m.batch)
            pending[k] = pending.get(k, self._balance(*k)) + m.quantity_delta
            if pending[k] < 0:
                raise RepositoryDenied("insufficient stock: a balance may not go below zero")
        self._movements.extend(movements)
        return list(movements)

    def movements(self, *, tenant_id, location_id=None):
        return [m for m in self._movements
                if m.tenant_id == tenant_id and (location_id is None or m.location_id == location_id)]

    def supplies_of_batch(self, *, tenant_id, product_id, batch):
        """FR-19: the SUPPLY movements (dispenses) of one product batch in the tenant."""
        return [m for m in self._movements if m.tenant_id == tenant_id and m.reason == SUPPLY
                and m.product_id == product_id and m.batch == batch]

    def balances(self, *, tenant_id, location_id=None, product_id=None):
        return [b for b in balance_rows(self.movements(tenant_id=tenant_id, location_id=location_id),
                                        self.supply_class_of)
                if b["quantity"] != 0 and (product_id is None or b["product_id"] == product_id)]
