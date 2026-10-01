"""X-27 precondition fixture (MVC-EPC-D-001 D2f, Sponsor ruling R16.4 — the R13 precondition-only method).

A consultation now refuses a pet that is not the selected owner's pet in the session tenant. Frozen tests that started
consultations with a placeholder pet id ("p1", "pet-6", "p") get a REAL pet instead, created through the governed path:
the owner signs in and creates it with POST /api/pets, so the served application — not the test — binds it to that
owner (from the session) in that owner's tenant. No assertion of any frozen test changes.
"""
import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import main as api  # noqa: E402
from routers import auth  # noqa: E402


def owned_pet(owner_id: str, password: str = "pw", name: str = "Luna") -> str:
    """Sign in as the (already seeded) owner and create their pet through the served route; return its pet_id.

    An identity that does not exist can own nothing: for it (a frozen test asserting that a non-existent participant is
    refused) the id returned names no pet, and the participant refusal stays the behaviour under test."""
    ident = auth.IDENTITY_REPO.get_by_user_id(owner_id)
    if ident is None:
        return f"no-pet-of-{owner_id}"
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": ident.email, "password": password})
    if r.status_code != 200:
        raise AssertionError(f"precondition: owner sign-in failed: {r.status_code} {r.text}")
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    pet = c.post("/api/pets", json={"name": name, "species": "cat"})
    if pet.status_code != 200 or pet.json().get("owner_id") != owner_id:
        raise AssertionError(f"precondition: governed pet creation failed: {pet.status_code} {pet.text}")
    return pet.json()["pet_id"]
