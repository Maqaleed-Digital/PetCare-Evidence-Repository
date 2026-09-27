"""NFR-08 under Sponsor act SQ-3 — through the SERVED app (MVC-BUILD-RUNNER-001 v1.3 U28).

Authority: governance/sponsor_acts/MVC-SQ3-NFR08-STEP-UP-001.md (sha256 16efd233…85cc). Ratified evidence_definition:
"served-app tests per role plus MFA challenge on each sensitive operation" (NON_PROD). Every test here runs with
step-up enforcement ON (`mfa_enforced`), which is the served default. The MFA clock is injected (`main._mfa_now`), so
the 15-minute boundary is proven exactly and nothing sleeps.
"""
import base64
import logging
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
import mfa  # noqa: E402
from inventory import REGISTRATION_SOURCE, ProductRegistration  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant, grant_practitioner_authority  # noqa: E402

pytestmark = [pytest.mark.served_app, pytest.mark.mfa_enforced]
ROOT = Path(__file__).resolve().parents[2]
ROLES = ("owner", "veterinarian", "partner_clinic_admin", "platform_admin")


class Clock:
    def __init__(self):
        self.t = datetime(2031, 3, 1, 9, 0, tzinfo=timezone.utc)

    def __call__(self):
        return self.t

    def advance(self, seconds):
        self.t += timedelta(seconds=seconds)


@pytest.fixture
def clock(monkeypatch):
    c = Clock()
    monkeypatch.setattr(api, "_mfa_now", c)
    return c


def _client(user_id, role, tenant):
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@sq3.test", "pw", role, tenant_id=tenant)
    if role == "veterinarian":
        grant_practitioner_authority(user_id, tenant)
    return _sign_in(user_id)


def _sign_in(user_id):
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@sq3.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


def _secret(uri):
    b32 = parse_qs(urlparse(uri).query)["secret"][0]
    return base64.b32decode(b32 + "=" * (-len(b32) % 8))


def _code(secret, clock):
    clock.advance(31)                                   # a new TOTP step each time: codes are single-use
    return mfa.totp(secret, clock.t.timestamp())


def _enrol(c, clock):
    r = c.post("/api/me/mfa/enrol", json={"password": "pw"})
    assert r.status_code == 200, r.text
    secret = _secret(r.json()["otpauth_uri"])
    r = c.post("/api/me/mfa/confirm", json={"code": _code(secret, clock)})
    assert r.status_code == 200, r.text
    return secret, r.json()["recovery_codes"]


def _step_up(c, secret, clock):
    r = c.post("/api/me/mfa/step-up", json={"code": _code(secret, clock)})
    assert r.status_code == 200, r.text


def _call(c, op, json=None):
    method, template = op.split(" ", 1)
    path = re.sub(r"\{[^}]+\}", "x-sq3", template)
    return c.request(method, path, json=json if method != "GET" else None)


def _mfa_error(r):
    d = r.json().get("detail")
    return d.get("error") if isinstance(d, dict) and str(d.get("error", "")).startswith("MFA_") else None


# ----------------------------------------------------------------------- MFA challenge on each sensitive operation
@pytest.mark.parametrize("role", ROLES)
def test_every_served_sensitive_operation_challenges_every_role(role, clock):
    tenant = f"t-sq3-{role}"
    unenrolled = _client(f"u-sq3-{role}-new", role, tenant)
    enrolled = _client(f"u-sq3-{role}", role, tenant)
    _enrol(enrolled, clock)
    for op in sorted(mfa.MIDDLEWARE_OPERATIONS):
        r = _call(unenrolled, op, json={})
        assert r.status_code == 403 and r.json()["detail"] == {"error": "MFA_ENROLMENT_REQUIRED", "operation": op}, op
        r = _call(enrolled, op, json={})
        assert r.status_code == 403 and r.json()["detail"]["error"] == "MFA_STEP_UP_REQUIRED", (op, r.text)
        assert r.json()["detail"]["operation"] == op
    if role in api.INVENTORY_ROLES:                        # the in-route one: a prescription-class (POM) supply
        if api.INVENTORY_REPO.supply_class_of("pom-sq3") != "POM":
            api.INVENTORY_REPO.register_product(ProductRegistration(
                product_id="pom-sq3", name="pom-sq3", supply_class="POM", source=REGISTRATION_SOURCE,
                registered_at=datetime.now(timezone.utc)))
        r = enrolled.post("/api/inventory/supplies", json={"location_id": "l", "product_id": "pom-sq3", "batch": "B",
                                                           "quantity": 1, "prescription_id": "rx"})
        assert r.status_code == 403 and r.json()["detail"]["operation"] == mfa.SUPPLY_OF_PRESCRIPTION_CLASS, r.text


def test_role_enforcement_holds_after_step_up_and_an_allowed_role_proceeds(clock):
    admin = _client("u-sq3-admin-r", "platform_admin", "t-sq3-roles")
    owner = _client("u-sq3-owner-r", "owner", "t-sq3-roles")
    auth.seed_user("u-sq3-vet-r", "u-sq3-vet-r@sq3.test", "pw", "veterinarian", tenant_id="t-sq3-roles")
    a_secret, _ = _enrol(admin, clock)
    o_secret, _ = _enrol(owner, clock)
    grant = "/api/admin/practitioners/u-sq3-vet-r/authority"
    _step_up(owner, o_secret, clock)
    r = owner.post(grant, json={"licence_ref": "MEWA-SQ3"})
    assert r.status_code == 403 and _mfa_error(r) is None                     # MFA passed; the ROLE refuses
    _step_up(admin, a_secret, clock)
    assert admin.post(grant, json={"licence_ref": "MEWA-SQ3"}).status_code == 200
    assert admin.get("/audit/events/tenant").status_code == 200             # a normal step-up serves normal ops


def test_a_step_up_belongs_to_the_session_that_performed_it(clock):
    """A step-up is bound to ONE server-side session: another session of the same person gets no authority from it."""
    first = _client("u-sq3-sess", "partner_clinic_admin", "t-sq3-sess")
    secret, _ = _enrol(first, clock)
    second = _sign_in("u-sq3-sess")                                          # same person, a new session
    _step_up(first, secret, clock)
    r = second.get("/audit/events/tenant")
    assert r.status_code == 403 and r.json()["detail"]["error"] == "MFA_STEP_UP_REQUIRED"
    assert first.get("/audit/events/tenant").status_code == 200


# ---------------------------------------------------------------------------------------------- freshness window
def test_freshness_is_fifteen_minutes_exactly(clock):
    admin = _client("u-sq3-fresh", "partner_clinic_admin", "t-sq3-fresh")
    secret, _ = _enrol(admin, clock)
    _step_up(admin, secret, clock)
    clock.advance(mfa.STEP_UP_FRESHNESS_SECONDS)                             # 15:00 after the step-up — still fresh
    assert admin.get("/audit/events/tenant").status_code == 200
    clock.advance(1)                                                         # 15:01 — stale
    r = admin.get("/audit/events/tenant")
    assert r.status_code == 403 and r.json()["detail"]["error"] == "MFA_STEP_UP_REQUIRED"
    assert mfa.STEP_UP_FRESHNESS_SECONDS == 900


# -------------------------------------------------------------------------------------------------- always-fresh
def test_an_always_fresh_operation_never_reuses_a_step_up(clock):
    t = "t-sq3-af"
    a = _client("u-sq3-af-a", "partner_clinic_admin", t)
    _client("u-sq3-af-b", "partner_clinic_admin", t)
    for s in ("u-sq3-af-s1", "u-sq3-af-s2"):
        auth.seed_user(s, f"{s}@sq3.test", "pw", "veterinarian", tenant_id=t)
    secret, _ = _enrol(a, clock)
    _step_up(a, secret, clock)
    assert a.post("/api/admin/mfa-resets", json={"subject_user_id": "u-sq3-af-s1"}).status_code == 200
    r = a.post("/api/admin/mfa-resets", json={"subject_user_id": "u-sq3-af-s2"})   # same 15 minutes, no new step-up
    assert r.status_code == 403 and r.json()["detail"]["error"] == "MFA_STEP_UP_REQUIRED"
    assert r.json()["detail"]["always_fresh"] is True
    _step_up(a, secret, clock)
    assert a.get("/audit/events/tenant").status_code == 200                  # the step-up has now authorized an op
    r = a.post("/api/admin/mfa-resets", json={"subject_user_id": "u-sq3-af-s2"})
    assert r.status_code == 403                                              # so it is not "new" for an always-fresh op
    _step_up(a, secret, clock)
    assert a.post("/api/admin/mfa-resets", json={"subject_user_id": "u-sq3-af-s2"}).status_code == 200


# ---------------------------------------------------------------------------------------------------- enrolment
def test_enrolment_needs_reauthentication_without_a_factor_and_a_step_up_with_one(clock):
    c = _client("u-sq3-enrol", "veterinarian", "t-sq3-enrol")
    r = c.post("/api/me/mfa/enrol")
    assert r.status_code == 401 and r.json()["detail"]["error"] == "PRIMARY_REAUTHENTICATION_REQUIRED"
    assert c.post("/api/me/mfa/enrol", json={"password": "wrong"}).status_code == 401
    r = c.post("/api/me/mfa/enrol", json={"factor": "sms", "password": "pw"})      # SMS is not a factor (SQ-3)
    assert r.status_code == 400 and r.json()["detail"]["error"] == "MFA_FACTOR_NOT_SUPPORTED"
    secret, _ = _enrol(c, clock)
    r = c.post("/api/me/mfa/enrol", json={"password": "pw"})                        # an active factor exists
    assert r.status_code == 403 and r.json()["detail"]["error"] == "MFA_STEP_UP_REQUIRED"
    _step_up(c, secret, clock)
    assert c.post("/api/me/mfa/enrol").status_code == 200                           # replaced with the old factor
    assert mfa.FACTORS == ("totp",)


# ----------------------------------------------------------------------------------------------- recovery codes
def test_recovery_codes_are_ten_hashed_single_use_one_operation_each_and_never_logged(clock, caplog):
    c = _client("u-sq3-rc", "platform_admin", "t-sq3-rc")
    with caplog.at_level(logging.DEBUG):
        _secret_, codes = _enrol(c, clock)
        assert len(codes) == 10 and len(set(codes)) == 10
        stored = api.MFA_REPO.recovery_codes("u-sq3-rc")
        assert len(stored) == 10
        blob = repr(stored).encode() + b"".join(rc.digest + rc.salt for rc in stored)
        assert not any(code.encode() in blob or code.replace("-", "").encode() in blob for code in codes)
        assert c.post("/api/me/mfa/recovery", json={"code": codes[0]}).status_code == 200
        assert c.get("/audit/events/tenant").status_code == 200                 # exactly one operation …
        r = c.get("/audit/events/tenant")
        assert r.status_code == 403 and r.json()["detail"]["error"] == "MFA_STEP_UP_REQUIRED"   # … not two
        r = c.post("/api/me/mfa/recovery", json={"code": codes[0]})             # a code works once
        assert r.status_code == 401 and r.json()["detail"]["error"] == "RECOVERY_CODE_INVALID"
        assert c.post("/api/me/mfa/recovery", json={"code": "AAAA-BBBB-CCCC-DDDD"}).status_code == 401
        assert c.post("/api/me/mfa/recovery", json={"code": codes[1].lower()}).status_code == 200
    for code in codes:
        assert code not in caplog.text and code.replace("-", "") not in caplog.text


# --------------------------------------------------------------------------------------------- assisted reset
def test_assisted_reset_needs_a_second_same_tenant_admin_revokes_every_session_and_forces_reenrolment(clock):
    t = "t-sq3-reset"
    a = _client("u-sq3-ra", "partner_clinic_admin", t)
    b = _client("u-sq3-rb", "platform_admin", t)
    subject = _client("u-sq3-rs", "partner_clinic_admin", t)
    subject_2nd_session = _sign_in("u-sq3-rs")
    outsider = _client("u-sq3-rx", "platform_admin", "t-sq3-reset-other")
    sec = {k: _enrol(c, clock)[0] for k, c in (("a", a), ("b", b), ("s", subject), ("x", outsider))}
    _step_up(subject, sec["s"], clock)
    r = subject.post("/api/admin/mfa-resets", json={"subject_user_id": "u-sq3-rs"})
    assert r.status_code == 403 and r.json()["detail"]["error"] == "MFA_RESET_SELF_REQUEST_REFUSED"
    _step_up(a, sec["a"], clock)
    reset_id = a.post("/api/admin/mfa-resets", json={"subject_user_id": "u-sq3-rs"}).json()["reset_id"]
    approve = f"/api/admin/mfa-resets/{reset_id}/approve"
    _step_up(outsider, sec["x"], clock)
    assert outsider.post(approve).status_code == 404                         # another tenant's admin: not found
    _step_up(subject, sec["s"], clock)
    r = subject.post(approve)                                                # the subject cannot approve
    assert r.status_code == 403 and r.json()["detail"]["error"] == "MFA_RESET_SECOND_ADMIN_REQUIRED"
    _step_up(a, sec["a"], clock)
    r = a.post(approve)                                                      # nor can the requester
    assert r.status_code == 403 and r.json()["detail"]["error"] == "MFA_RESET_SECOND_ADMIN_REQUIRED"
    assert subject.get("/api/auth/me").status_code == 200
    _step_up(b, sec["b"], clock)
    r = b.post(approve)
    assert r.status_code == 200 and r.json()["sessions_revoked"] >= 2 and r.json()["reenrolment_required"] is True
    assert subject.get("/api/auth/me").status_code == 401 and subject_2nd_session.get("/api/auth/me").status_code == 401
    again = _sign_in("u-sq3-rs")
    r = again.get("/audit/events/tenant")                                    # sensitive ops refused until re-enrolled
    assert r.status_code == 403 and r.json()["detail"]["error"] == "MFA_ENROLMENT_REQUIRED"
    assert again.post("/api/me/mfa/recovery", json={"code": "x"}).status_code == 403   # old codes are gone
    assert again.post("/api/me/mfa/enrol").status_code == 401                # re-enrolment needs re-authentication
    new_secret, _ = _enrol(again, clock)
    _step_up(again, new_secret, clock)
    assert again.get("/audit/events/tenant").status_code == 200
    _step_up(b, sec["b"], clock)
    assert b.post(approve).json()["detail"]["error"] == "MFA_RESET_ALREADY_APPROVED"


def test_a_sole_admin_cannot_perform_an_in_product_assisted_reset(clock):
    t = "t-sq3-sole"
    a = _client("u-sq3-sole-a", "partner_clinic_admin", t)
    auth.seed_user("u-sq3-sole-v", "u-sq3-sole-v@sq3.test", "pw", "veterinarian", tenant_id=t)
    secret, _ = _enrol(a, clock)
    _step_up(a, secret, clock)
    r = a.post("/api/admin/mfa-resets", json={"subject_user_id": "u-sq3-sole-v"})
    assert r.status_code == 409
    assert r.json()["detail"] == {"error": "SOLE_ADMIN_MFA_RECOVERY", "dependency": "OPERATIONS:SOLE_ADMIN_MFA_RECOVERY"}


# ------------------------------------------------------------------------------------------ the served default
def test_step_up_is_enforced_by_default_and_has_no_off_switch():
    """A fresh interpreter that never loads the test conftest: the served app enforces SQ-3, and environment
    variables named like an off switch change nothing."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("PETCARE_MFA_")}
    env.update(SECRET_KEY="t", PETCARE_SECRET_MODE="environment", PETCARE_PERSISTENCE_MODE="memory",
               PETCARE_DOCUMENT_STORE_MODE="local", PETCARE_DOCUMENT_ROOT=str(Path(tempfile.gettempdir()) / "sq3-probe-docs"),
               PETCARE_MFA_STEP_UP_ENFORCED="false", PETCARE_MFA_SENSITIVE_OPERATIONS="",
               PETCARE_MFA_STEP_UP_MAX_AGE_SECONDS="99999", PYTHONPATH=str(ROOT / "petcare_api"))
    out = subprocess.run([sys.executable, "-c", "import main, mfa; print(main.MFA_STEP_UP_ENFORCED, "
                          "mfa.STEP_UP_FRESHNESS_SECONDS, len(mfa.MIDDLEWARE_OPERATIONS))"],
                         cwd=ROOT / "petcare_api", env=env, capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stderr[-2000:]
    assert out.stdout.split()[-3:] == ["True", "900", str(len(mfa.MIDDLEWARE_OPERATIONS))]
    source = (ROOT / "petcare_api" / "mfa.py").read_text() + (ROOT / "petcare_api" / "main.py").read_text()
    assert not re.search(r"environ[^\n]*(STEP_UP|SENSITIVE|MAX_AGE|ENFORCED)", source)


def test_every_mapped_sq3_operation_is_served_and_no_unmapped_sensitive_route_exists():
    served = {f"{m} {r.path}" for r in api.app.routes for m in (getattr(r, "methods", None) or ())}
    assert mfa.ALL_OPERATIONS <= served
    tokens = re.compile(r"role|permission|payout|bank|api-?key|credential|export|mfa-reset|membership", re.I)
    # MVC-EPC-D-001 D1 extended SQ-3 to every item: a name-matched route must be MAPPED or DECLARED not sensitive
    # (with its reason, mfa.DECLARED_NOT_SENSITIVE) — and every declaration must name a served route.
    unmapped = sorted(op for op in served if tokens.search(op.split(" ", 1)[1]) and op not in mfa.ALL_OPERATIONS
                      and op not in mfa.DECLARED_NOT_SENSITIVE)
    assert unmapped == [], unmapped
    assert set(mfa.DECLARED_NOT_SENSITIVE) <= served and not set(mfa.DECLARED_NOT_SENSITIVE) & mfa.ALL_OPERATIONS
    assert mfa.NOT_CURRENTLY_SERVED == ()                       # all fifteen SQ-3 operations are served (D1)
