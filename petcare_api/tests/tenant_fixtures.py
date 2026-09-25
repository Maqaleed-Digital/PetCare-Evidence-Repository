"""Provision tenants for tests, EXPLICITLY.

Migration 0034 makes a tenant a governed object: an identity or a session may
only be assigned to one that exists and is active. Tests therefore have to
create the tenants they use, exactly as a deployment would.

This helper does NOT auto-create a tenant inside the write path. That would be
free-form tenant creation, which is the thing PRE-1 found and TENANT-05 forbids —
a typo would again produce a new, empty, perfectly functional scope. It is a test
fixture, called from test code, and the application never reaches it.
"""
from __future__ import annotations

import os
import sys
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tenants import Tenant  # noqa: E402


def ensure_tenant(tenant_id: Optional[str], *, persistence=None) -> None:
    """Create the tenant if it is absent. `None` is a no-op.

    A `None` tenant is the legitimate "no tenant assignment" state W0-C defines,
    and it needs no registry entry — creating one would be inventing a scope for
    an identity that deliberately has none.
    """
    if tenant_id is None:
        return
    if persistence is None:
        from routers import auth

        persistence = auth.PERSISTENCE
    repo = persistence.tenants
    if repo is None:
        raise AssertionError("no tenant registry is configured for this run")
    if repo.get(tenant_id) is None:
        repo.create(Tenant(tenant_id=tenant_id,
                           display_name=f"Fixture tenant {tenant_id}"))


def grant_practitioner_authority(user_id: str, tenant_id: str, *, persistence=None) -> None:
    """FR-01 (U5) fixture: give a test veterinarian a live VETERINARIAN authority grant.

    Regulated acts (prescribing, dispensing) require a live practitioner authority
    attribute in addition to the role (AC-FR-01-02). Suites that exercise those acts
    as a veterinarian call this explicitly — authority is never implied by the role.
    The governed grant route itself is proven in test_practitioner_authority.py.
    """
    from datetime import datetime, timedelta, timezone
    from uuid import uuid4

    from practitioners import CLASS_VETERINARIAN, PractitionerAuthorityGrant

    if persistence is None:
        import main as api
        persistence = api.PERSISTENCE
    now = datetime.now(timezone.utc)
    persistence.practitioners.grant(PractitionerAuthorityGrant(
        grant_id=str(uuid4()), tenant_id=tenant_id, actor_id=user_id,
        professional_class=CLASS_VETERINARIAN, licence_ref="TEST-LICENCE",
        effective_from=now - timedelta(minutes=1), granted_by_actor_id="test-fixture", granted_at=now))


def stock_origin(tenant_id: str, *, product_id: str = "rx-stock-product", batch: str = "RX-BATCH-1",
                 quantity: int = 1, persistence=None) -> dict:
    """FR-19 (U13) fixture: a stocked dispensary location, and the dispense body that draws from it.

    Every dispense now draws from stock and records its batch (AC-FR-19-01). Suites that dispense
    call this explicitly; the receipt is written through the repository the served app uses.
    """
    from datetime import date, datetime, timezone
    from uuid import uuid4

    from inventory import RECEIPT, InventoryLocation, StockMovement

    if persistence is None:
        import main as api
        inv = api.INVENTORY_REPO
    else:
        inv = persistence.inventory
    loc_id = f"loc-dispensary-{tenant_id}"
    if inv.get_location(loc_id, tenant_id=tenant_id) is None:
        now = datetime.now(timezone.utc)
        inv.add_location(InventoryLocation(location_id=loc_id, tenant_id=tenant_id, name="Dispensary", created_at=now))
    if not any(b["product_id"] == product_id and b["batch"] == batch and b["quantity"] >= quantity
               for b in inv.balances(tenant_id=tenant_id, location_id=loc_id)):
        inv.record([StockMovement(movement_id=str(uuid4()), tenant_id=tenant_id, location_id=loc_id,
                                  product_id=product_id, batch=batch, quantity_delta=1000, reason=RECEIPT,
                                  supply_class=inv.supply_class_of(product_id), actor_id="test-fixture",
                                  actor_role="partner_clinic_admin", created_at=datetime.now(timezone.utc),
                                  batch_expiry=date(2099, 12, 31))])
    return {"location_id": loc_id, "product_id": product_id, "batch": batch, "quantity": quantity}
