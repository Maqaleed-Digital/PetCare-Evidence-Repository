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
