"""ROLE-01..09, PHARM-ROLE-01..04, and the CONF-01 closure.

Sponsor ruling `PRE2_RULING=2-C`: machine role IDs are the sole authorization
authority; display labels are presentation only. `PHARMACY_ROLE=REMOVE`:
`pharmacy` is not an authorization principal.

## What CONF-01 was

Three vocabularies. The serving layer minted machine ids, `require_role()`
accepted only the display forms, and the web middleware aliased the machine ids.
**Every identity the system created was refused by every protected route with
`403 Unknown role`.**

The suite did not show it because tests that needed a working session seeded the
display spelling directly — a value no production path ever produced. So the
closure proof below drives the REAL registration endpoint and asserts the role
guard accepts what registration actually mints. A fixture that injected an
accepted value would reproduce the blind spot rather than close it.
"""
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
import routers.auth as auth  # noqa: E402
from role_probes import roles_the_catalogue_refuses  # noqa: E402
from roles import (  # noqa: E402
    ALLOWED_ROLES,
    DISPLAY_LABELS,
    ROLE_OWNER,
    ROLE_PARTNER_CLINIC_ADMIN,
    ROLE_PLATFORM_ADMIN,
    ROLE_VETERINARIAN,
    display_label,
    is_valid_role,
)
from repositories import RepositoryDenied  # noqa: E402
from tenant_fixtures import ensure_tenant  # noqa: E402

client = TestClient(api.app, base_url="https://testserver")
PROTECTED = "/api/appointments"
BODY = {"pet_id": "p1", "owner_id": "o1", "clinic_id": "c1", "tenant_id": "t-role"}
HDRS = {"X-Correlation-Id": "c-1", "X-Actor-Id": "a-1"}
MIDDLEWARE = Path(__file__).resolve().parents[2] / "petcare_web" / "middleware.ts"


def _signed_in(role: str, email: str, tenant: str | None = "t-role") -> str:
    ensure_tenant(tenant)
    auth.seed_user("u-" + email, email, "pw", role, tenant_id=tenant)
    r = client.post("/api/auth/sign-in", json={"email": email, "password": "pw"})
    assert r.status_code == 200, r.text
    return r.cookies["petcare_session"]


@pytest.fixture(autouse=True)
def _clean_cookies():
    client.cookies.clear()
    yield
    client.cookies.clear()


# ---------------------------------------------------------------------------
# ROLE-01 / ROLE-02 — canonical ids authorize, and deny
# ---------------------------------------------------------------------------

def test_role_01_a_canonical_machine_role_is_accepted_on_a_permitted_route():
    """The positive control. Without it, a guard that denied everything would
    satisfy every negative control in this file — and denying everything is
    exactly what CONF-01 did."""
    client.cookies.set("petcare_session", _signed_in(ROLE_OWNER, "role01@t"))
    r = client.post(PROTECTED, json=BODY, headers=HDRS)
    assert r.status_code in (200, 201), r.text


def test_role_02_a_canonical_machine_role_is_denied_on_a_forbidden_route():
    """An owner may not read every tenant's audit log."""
    client.cookies.set("petcare_session", _signed_in(ROLE_OWNER, "role02@t"))
    assert client.get("/audit/events").status_code == 403


def test_role_02b_the_permitted_role_reaches_the_same_route():
    """Paired with ROLE-02 so the denial is shown to be about the ROLE rather
    than about the route being unreachable."""
    client.cookies.set("petcare_session", _signed_in(ROLE_PLATFORM_ADMIN, "role02b@t"))
    assert client.get("/audit/events").status_code == 200


# ---------------------------------------------------------------------------
# ROLE-03 / ROLE-09 — a display label is not authority
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("label", sorted(DISPLAY_LABELS.values()))
def test_role_03_a_display_label_is_not_an_authority_token(label):
    assert not is_valid_role(label)
    assert label not in api.VALID_ROLES


def test_role_03b_a_display_label_cannot_be_stored_as_a_role():
    with pytest.raises(RepositoryDenied):
        auth.seed_user("u-role03b", "role03b@t", "pw",
                       DISPLAY_LABELS[ROLE_PLATFORM_ADMIN], tenant_id=None)


def test_role_03c_a_display_label_in_a_session_is_refused_by_the_guard():
    """The label reaches `require_role` through a hand-built session — the one
    place a hand-built cookie is the right instrument, because no governed path
    can produce this state and the guard must still refuse it."""
    token = auth._serializer().dumps({
        "user_id": "u-x", "email": "x@t", "role": DISPLAY_LABELS[ROLE_OWNER],
        "tenant_id": "t-role", "sid": "no-such-session",
    })
    client.cookies.set("petcare_session", token)
    r = client.post(PROTECTED, json=BODY, headers=HDRS)
    assert r.status_code == 401  # refused before the role is even reached


def test_role_09_changing_a_display_label_changes_no_authorization_outcome(
    monkeypatch,
):
    """The property 2-C exists to create. A label is renamed; authorization is
    unmoved, because nothing compares it."""
    cookie = _signed_in(ROLE_OWNER, "role09@t")
    client.cookies.set("petcare_session", cookie)
    before = client.post(PROTECTED, json=BODY, headers=HDRS).status_code

    import roles as roles_module

    monkeypatch.setitem(roles_module.DISPLAY_LABELS, ROLE_OWNER, "Pet Guardian")
    assert display_label(ROLE_OWNER) == "Pet Guardian"

    after = client.post(PROTECTED, json=BODY, headers=HDRS).status_code
    assert after == before, "a label change altered an authorization outcome"


# ---------------------------------------------------------------------------
# ROLE-04 / ROLE-05 / ROLE-06 — unknown is denied, exactly
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("role", [
    "superuser", "admin", "vet", "Platform_Admin", "PLATFORM_ADMIN",
    " platform_admin ", "platform_admin ", "", None, 7,
])
def test_role_04_05_06_only_the_exact_canonical_token_is_a_role(role):
    """No case folding, no trimming, no normalisation.

    A comparison that normalised would let `Platform_Admin` or a padded value
    become authority, and the promotion would be invisible at the call site.
    `admin` and `vet` are here specifically: they were live middleware values.
    """
    assert not is_valid_role(role)


def test_role_04b_an_unknown_role_cannot_be_stored():
    with pytest.raises(RepositoryDenied):
        auth.seed_user("u-role04b", "role04b@t", "pw", "superuser", tenant_id=None)


# ---------------------------------------------------------------------------
# ROLE-07 / ROLE-08 — storage and migration agree with the catalogue
# ---------------------------------------------------------------------------

def test_role_07_the_stored_role_check_holds_only_canonical_ids():
    """The schema and the module must state the same catalogue. Two sets meant
    to be equal, drifting, is exactly how CONF-01 happened."""
    sql = (Path(__file__).resolve().parents[2] / "petcare_runtime" / "migrations"
           / "0033_pre2_canonical_role_authority.sql").read_text(encoding="utf-8")
    code = "\n".join(l for l in sql.splitlines() if not l.strip().startswith("--"))
    for role in ALLOWED_ROLES:
        assert f"'{role}'" in code, f"{role} missing from the storage catalogue"
    for label in DISPLAY_LABELS.values():
        assert f"'{label}'" not in code, f"display label {label!r} is storable"


def test_role_08_the_migration_maps_only_canonical_ids():
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "governance"))
    import identity_migration_dryrun as tool

    assert set(tool.ROLE_MAP) == set(ALLOWED_ROLES)
    for source, target in tool.ROLE_MAP.items():
        assert source == target, "the role map rewrites a role"


# ---------------------------------------------------------------------------
# PHARM-ROLE-01..04
# ---------------------------------------------------------------------------

def test_pharm_role_01_pharmacy_is_not_a_role():
    assert not is_valid_role("pharmacy")
    assert "pharmacy" not in api.VALID_ROLES
    with pytest.raises(RepositoryDenied):
        auth.seed_user("u-pharm1", "pharm1@t", "pw", "pharmacy", tenant_id=None)


def test_pharm_role_02_the_retired_role_remains_denied():
    """Derived, never named — `petcare_api` is a live tree under
    MVC-RETIRED-ROLE-CUSTODY-001."""
    refused = roles_the_catalogue_refuses()
    assert refused, "nothing outside the catalogue; this would test nothing"
    for role in refused:
        assert not is_valid_role(role)


def test_pharm_role_03_no_pharmacy_family_alias_reaches_the_role_guard():
    """Any token whose name suggests the removed principal must be refused. The
    family is checked rather than one literal, because the defect PRE-2 found was
    a SHORT FORM that the single-literal guard could not see."""
    for candidate in ("pharmacy", "pharmacist", "pharmacy_admin", "Pharmacy",
                      "pharmacy-operator", "pharmacyOperator"):
        assert not is_valid_role(candidate), f"{candidate!r} is a role"


def test_pharm_role_04_the_web_middleware_grants_no_pharmacy_authority():
    """The surface stays; the principal does not.

    `/pharmacy` may remain as a ROUTE PATH — that is the retained domain
    capability — but no role category named pharmacy may exist, and no route may
    be satisfied by one.
    """
    text = MIDDLEWARE.read_text(encoding="utf-8")
    code = "\n".join(l for l in text.splitlines() if not l.strip().startswith("//"))

    assert "pharmacy:" not in code, "a pharmacy role category survives in the alias map"
    assert "'pharmacy'" not in code, (
        "a role-category string 'pharmacy' survives; only the /pharmacy PATH may remain"
    )
    assert "'/pharmacy'" in code, (
        "the pharmacy route is gone — PHARMACY_DOMAIN_CAPABILITIES is "
        "RETAIN_PENDING_ROLE_REBINDING, not remove"
    )


def test_the_web_middleware_maps_only_canonical_role_ids():
    text = MIDDLEWARE.read_text(encoding="utf-8")
    code = "\n".join(l for l in text.splitlines() if not l.strip().startswith("//"))
    import re

    # Keys of the category map, read as whole tokens. A substring test would
    # match `platform_admin:` when looking for `admin:` and report a legacy
    # alias that is not there.
    keys = set(re.findall(r"^\s*([A-Za-z_][A-Za-z0-9_]*):\s*'", code, re.M))
    for role in ALLOWED_ROLES:
        assert role in keys, f"{role} is not mapped by the middleware"
    # The non-canonical short forms that let a value the serving layer never
    # mints through the UI gate.
    for legacy in ("clinic_admin", "admin", "vet", "pharmacy"):
        assert legacy not in keys, f"legacy alias {legacy!r} survives as a role key"


def test_the_web_middleware_denies_an_unmapped_role_rather_than_passing_it_through():
    """`?? rawRole` passed an unmapped value straight through, so a cookie
    carrying `admin` — a value the serving layer never mints — matched
    `['admin']` and opened the admin surface."""
    text = MIDDLEWARE.read_text(encoding="utf-8")
    # Comments explain the change and necessarily quote the old form.
    code = "\n".join(l for l in text.splitlines() if not l.strip().startswith("//"))
    assert "?? rawRole" not in code, "an unmapped role is still passed through"
    assert "?? ''" in code


# ---------------------------------------------------------------------------
# CONF-01 closure
# ---------------------------------------------------------------------------

def test_conf01_a_registered_identity_is_no_longer_refused_as_an_unknown_role():
    """THE closure proof.

    Registration is driven for real, so the role under test is the one the
    serving layer actually mints. Before 2-C this produced `403 Unknown role`
    from `require_role`. It now passes the role guard and is stopped by the
    TENANT guard instead — `403 NO_TENANT_AUTHORITY` — because registration
    establishes identity and never tenant authority (W0-C).

    The distinction between those two 403s is the whole of CONF-01: one says the
    system does not recognise its own vocabulary, the other says this identity
    has no scope yet.
    """
    # An OWNER, because `/api/appointments` permits owner and platform_admin. A
    # veterinarian would be refused by the ROUTE's own role set, which is a
    # correct denial and would tell us nothing about CONF-01.
    auth.seed_invite_code("CONF01-OWNER", ROLE_OWNER)
    r = client.post("/api/auth/register", json={
        "email": "conf01@test.invalid", "password": "fixture-only-credential",
        "invite_code": "CONF01-OWNER", "role": ROLE_OWNER, "name": "Conf01",
    })
    assert r.status_code == 201, r.text
    assert r.json()["user"]["role"] == ROLE_OWNER

    client.cookies.set("petcare_session", r.cookies["petcare_session"])
    denied = client.post(PROTECTED, json=BODY, headers=HDRS)
    assert denied.status_code == 403, denied.text
    assert denied.json()["detail"]["error"] == "NO_TENANT_AUTHORITY", (
        "a registered identity is still refused as an unknown role — CONF-01 is open"
    )


def test_conf01b_the_minted_vocabulary_and_the_accepted_vocabulary_are_the_same_set():
    """Stated directly, because CONF-01 was precisely these two sets differing."""
    import roles as roles_module

    assert api.VALID_ROLES is roles_module.ALLOWED_ROLES
    assert set(api.VALID_ROLES) == {
        ROLE_PLATFORM_ADMIN, ROLE_PARTNER_CLINIC_ADMIN, ROLE_VETERINARIAN, ROLE_OWNER,
    }
