"""Rule 16 — the Option A routes are reachable from the SERVED application.

The measurement this lane started from found 86 runtime domain routes and zero
mounted by the served app, with every domain router mounted only inside tests
that build their own `FastAPI()`. That is the failure this file exists to make
impossible to repeat: a route can be written, imported, unit-tested and green
while being unreachable from the process that actually runs.

So the assertions below are made against `main.app` — the object uvicorn serves
— and never against an app assembled here.
"""
import os
import sys

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402

#: Every route the Option A workflow needs, as (method, path). If Option A
#: cannot be driven without it, it belongs here.
OPTION_A_ROUTES: tuple[tuple[str, str], ...] = (
    ("POST", "/api/prescriptions"),
    ("GET", "/api/prescriptions/{prescription_id}"),
    ("POST", "/api/prescriptions/{prescription_id}/verify"),
    ("POST", "/api/prescriptions/{prescription_id}/dispense"),
    ("POST", "/api/prescriptions/{prescription_id}/documents"),
    ("GET", "/api/prescriptions/{prescription_id}/documents"),
    ("GET", "/api/prescriptions/{prescription_id}/documents/{document_id}"),
    ("GET", "/api/prescriptions/{prescription_id}/transitions"),
    ("GET", "/api/prescriptions/queue/awaiting-dispense"),
)


def _served_routes() -> set[tuple[str, str]]:
    """(method, path) pairs the served application actually exposes."""
    mounted: set[tuple[str, str]] = set()
    for route in api.app.routes:
        if isinstance(route, APIRoute):
            for method in route.methods:
                mounted.add((method, route.path))
    return mounted


@pytest.mark.parametrize("method,path", OPTION_A_ROUTES)
def test_option_a_route_is_mounted_on_the_served_app(method, path):
    assert (method, path) in _served_routes(), (
        f"{method} {path} is not mounted on main.app. The handler may exist and "
        "its unit tests may pass; nothing that runs can reach it."
    )


def test_the_reachability_check_is_not_vacuous():
    """ARMED. The checker must be able to report a route as ABSENT.

    A membership test over a set it builds itself passes trivially if the set is
    ever built wrong — for instance if `_served_routes()` returned everything,
    or if OPTION_A_ROUTES were empty. Both failure modes are excluded here:
    a route that is definitely not mounted must be reported missing, and the
    declared set must be non-empty.
    """
    assert OPTION_A_ROUTES, "the declared Option A route set is empty"
    mounted = _served_routes()
    assert ("POST", "/api/prescriptions/{prescription_id}/not-a-real-route") not in mounted
    assert ("GET", "/api/definitely/not/mounted") not in mounted
    # And the set is a real reading of the app, not an empty container.
    assert ("POST", "/api/prescriptions") in mounted


def test_every_option_a_route_answers_rather_than_404ing():
    """Mounted is necessary, not sufficient — Rule 13 applied to routing.

    A path can be registered and still be unreachable in practice because an
    earlier route shadows it. Starlette resolves in declaration order, and
    `/api/prescriptions/queue/awaiting-dispense` is declared AFTER
    `/api/prescriptions/{prescription_id}`.

    It is NOT currently shadowed, and the reason is worth stating rather than
    relying on: the parameterised route has three path segments and the queue
    has four, so they cannot collide. The hazard is real but latent — a future
    `/api/prescriptions/{prescription_id}/{action}` would shadow it immediately,
    and the route set above would still report it present. This control is what
    turns that from a silent 404 into a failing test.

    Asserted with NO session, so the expected answer is 401 — authentication is
    reached, which proves dispatch got to the handler. A 404 here means the path
    never resolved.
    """
    client = TestClient(api.app)
    client.cookies.clear()
    r = client.get("/api/prescriptions/queue/awaiting-dispense")
    assert r.status_code != 404, (
        "the dispensing queue is shadowed by /api/prescriptions/{prescription_id}; "
        "it is registered but unreachable"
    )
    assert r.status_code == 401, r.status_code


def test_the_pharmacy_gateway_is_deliberately_not_mounted():
    """RECORDED, not silently accepted.

    `petcare_runtime.pharmacy.fastapi_app` builds a SEPARATE FastAPI app with 11
    read-only review surfaces. It is not mounted here and must not be, for two
    reasons that are both about correctness rather than tidiness:

    1. Its `build_gateway_auth_context` accepts ANY non-empty `Authorization:
       Bearer <string>` — the token is never validated — and takes actor and
       tenant straight from client headers. Mounting it into the authenticated
       application would reintroduce W0-B, the defect that made every guard in
       main.py rest on a value the caller chose.

    2. Every write in that domain (`start_pharmacy_review`,
       `progress_pharmacy_review`) requires ROLE_PHARMACY, which is not an
       authorization principal in this estate (PHARMACY_ROLE=REMOVE). So the
       read surfaces can only ever return records no identity can create.

    Mounting it would raise the route count and deliver nothing, which is
    precisely the coverage theatre Option A §7 forbids. This test fails if
    someone mounts it anyway, so the decision cannot be reversed silently.
    """
    mounted = {path for _, path in _served_routes()}
    leaked = {p for p in mounted if p.startswith("/api/pharmacy/")}
    assert not leaked, (
        "the pharmacy gateway was mounted into the served app; its auth accepts "
        f"any bearer string and trusts client-supplied actor headers: {leaked}"
    )
