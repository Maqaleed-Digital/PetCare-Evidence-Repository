"""FR-20 — cash on delivery with digital receipting (MVC-BUILD-RUNNER-001 U14).

AC-FR-20-01: an owner chooses cash on delivery at checkout and the order records COD as its payment
method. Eligible orders are GENERAL/OTC lines priced from the tenant's price list; POM/RESTRICTED/
CONTROLLED products are dispensed against a prescription through the pharmacy, not ordered here.
AC-FR-20-02: on delivery the owner receives a digital receipt in their chosen language, persisted
against the order and retrievable later. A "digital receipt" is not ZATCA e-invoicing (ratified).
AC-FR-20-03/04 (EXTERNAL:LOGISTICS_PARTNER): an order is PAID only with a recorded collection
confirmation for its exact total; today the confirmation is recorded by tenant staff (source STAFF)
through the same boundary the partner adapter will use.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Protocol

from repositories import RepositoryDenied

COD = "COD"
PAYMENT_METHODS = (COD,)
PLACED, DELIVERED = "PLACED", "DELIVERED"
SOURCE_STAFF, SOURCE_PARTNER = "STAFF", "PARTNER"
MAX_LINES, MAX_QTY = 50, 1000


@dataclass(frozen=True)
class PriceEntry:
    tenant_id: str
    product_id: str
    unit_price_halalas: int
    set_by_actor_id: str
    set_at: datetime


@dataclass(frozen=True)
class OrderLine:
    product_id: str
    quantity: int
    unit_price_halalas: int


@dataclass(frozen=True)
class Order:
    order_id: str
    tenant_id: str
    owner_id: str
    payment_method: str
    lines: tuple
    created_at: datetime

    @property
    def total_halalas(self) -> int:
        return sum(l.quantity * l.unit_price_halalas for l in self.lines)


@dataclass(frozen=True)
class Collection:
    order_id: str
    tenant_id: str
    amount_halalas: int
    reference: str
    source: str
    confirmed_by: str
    confirmed_at: datetime


@dataclass(frozen=True)
class Receipt:
    receipt_id: str
    order_id: str
    tenant_id: str
    owner_id: str
    language: str
    rendered: str
    total_halalas: int
    issued_at: datetime


def sar(halalas: int) -> str:
    return f"{halalas // 100}.{halalas % 100:02d}"


def render_receipt(order: Order, collection: Collection, language: str, issued_at: datetime) -> str:
    """The receipt text, in the owner's language. Arabic is the primary language (FR-09)."""
    if language == "ar":
        lines = [f"إيصال رقمي — الطلب {order.order_id}", "طريقة الدفع: الدفع عند الاستلام",
                 *[f"{l.product_id} × {l.quantity} — {sar(l.quantity * l.unit_price_halalas)} ر.س" for l in order.lines],
                 f"الإجمالي المحصّل: {sar(collection.amount_halalas)} ر.س", f"مرجع التحصيل: {collection.reference}",
                 f"تاريخ الإصدار: {issued_at.date().isoformat()}"]
    else:
        lines = [f"Digital receipt — order {order.order_id}", "Payment method: cash on delivery",
                 *[f"{l.product_id} x {l.quantity} — SAR {sar(l.quantity * l.unit_price_halalas)}" for l in order.lines],
                 f"Total collected: SAR {sar(collection.amount_halalas)}", f"Collection reference: {collection.reference}",
                 f"Issued: {issued_at.date().isoformat()}"]
    return "\n".join(lines)


def validate_collection(order: Order, c: Collection) -> None:
    """AC-FR-20-03: an order is paid only by a confirmation of its exact total, with a reference."""
    if c.amount_halalas != order.total_halalas:
        raise RepositoryDenied(f"collected {c.amount_halalas} halalas does not equal the order total {order.total_halalas}")
    if not c.reference.strip() or not c.confirmed_by.strip():
        raise RepositoryDenied("a collection confirmation names its reference and who confirmed it")
    if c.source not in (SOURCE_STAFF, SOURCE_PARTNER):
        raise RepositoryDenied("unknown collection source")


class OrderRepository(Protocol):
    def set_price(self, p: PriceEntry) -> PriceEntry: ...
    def price_of(self, product_id: str, *, tenant_id: str) -> Optional[int]: ...
    def prices(self, *, tenant_id: str) -> dict: ...
    def create(self, o: Order) -> Order: ...
    def get(self, order_id: str, *, tenant_id: str): ...
    def for_tenant(self, tenant_id: str) -> list: ...
    def deliver(self, c: Collection, r: Receipt) -> Receipt: ...
    def collection_of(self, order_id: str, *, tenant_id: str): ...
    def receipt_of(self, order_id: str, *, tenant_id: str): ...


@dataclass
class InMemoryOrderRepository:
    tenants: object
    _prices: list = field(default_factory=list)
    _orders: dict = field(default_factory=dict)
    _collections: dict = field(default_factory=dict)
    _receipts: dict = field(default_factory=dict)

    def set_price(self, p):
        if p.unit_price_halalas <= 0:
            raise RepositoryDenied("a price is a positive number of halalas")
        self._prices.append(p)
        return p

    def price_of(self, product_id, *, tenant_id):
        hits = [p for p in self._prices if p.tenant_id == tenant_id and p.product_id == product_id]
        # Latest set_at wins; among equal instants the later write (stable sort keeps insertion order).
        return sorted(hits, key=lambda p: p.set_at)[-1].unit_price_halalas if hits else None

    def prices(self, *, tenant_id):
        out = {}
        for p in sorted((p for p in self._prices if p.tenant_id == tenant_id), key=lambda p: p.set_at):
            out[p.product_id] = p.unit_price_halalas
        return out

    def create(self, o):
        if self.tenants.get(o.tenant_id) is None:
            raise RepositoryDenied(f"tenant {o.tenant_id!r} is not registered")
        self._orders[o.order_id] = o
        return o

    def get(self, order_id, *, tenant_id):
        o = self._orders.get(order_id)
        return o if o is not None and o.tenant_id == tenant_id else None

    def for_tenant(self, tenant_id):
        return sorted((o for o in self._orders.values() if o.tenant_id == tenant_id), key=lambda o: (o.created_at, o.order_id))

    def deliver(self, c, r):
        o = self.get(c.order_id, tenant_id=c.tenant_id)
        if o is None:
            raise RepositoryDenied("collection refers to no order in this tenant")
        if c.order_id in self._collections:
            raise RepositoryDenied("the order is already delivered")
        validate_collection(o, c)
        self._collections[c.order_id] = c
        self._receipts[c.order_id] = r
        return r

    def collection_of(self, order_id, *, tenant_id):
        c = self._collections.get(order_id)
        return c if c is not None and c.tenant_id == tenant_id else None

    def receipt_of(self, order_id, *, tenant_id):
        r = self._receipts.get(order_id)
        return r if r is not None and r.tenant_id == tenant_id else None
