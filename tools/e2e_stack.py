"""Full-stack E2E backend for the journey suite (MVC-EPC-D-001 Lane D, unit D0).

Real browser -> canonical web app (petcare_web) -> FastAPI `main:app` -> PostgreSQL. This process:
  1. obtains a PostgreSQL server — `PETCARE_E2E_PG_URL` (CI service) or a throwaway local cluster (pg_harness);
  2. creates a FRESH database `petcare_e2e`, replays EVERY migration from empty;
  3. seeds SYNTHETIC, clearly labelled non-production data (tenants, one user per role, grants);
  4. serves `main:app` with persistence mode `postgres` on 127.0.0.1:8090 (web origin http://localhost:3100).

Nothing here reaches a real provider, a real secret or any deployed system. Seeded passwords are test-only literals.
Run: python3 tools/e2e_stack.py            (blocks, serving the API)
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "petcare_api"), str(ROOT / "petcare_api" / "tests"), str(ROOT / "petcare_runtime" / "src")]

#: Synthetic identities. Password is a test-only literal; every account lives in a tenant labelled E2E.
SEED_PASSWORD = "E2E-only-Passw0rd!"
TENANT = "t-e2e-clinic"
USERS = (
    ("u-e2e-owner", "owner@e2e.test", "owner", "مالك تجريبي"),
    ("u-e2e-vet", "vet@e2e.test", "veterinarian", "طبيب تجريبي"),
    ("u-e2e-clinic-admin", "clinic-admin@e2e.test", "partner_clinic_admin", "مدير عيادة تجريبي"),
    ("u-e2e-platform-admin", "platform-admin@e2e.test", "platform_admin", "مدير منصة تجريبي"),
)
#: D2m (J-O8): synthetic registered products (id, name, supply class). Names are clearly synthetic.
PRODUCTS = (
    ("e2e-shampoo", "E2E Synthetic Shampoo", "GENERAL"),
    ("e2e-amoxicillin", "E2E Synthetic Amoxicillin", "POM"),
)
PORT = int(os.environ.get("PETCARE_E2E_API_PORT", "8090"))
WEB_ORIGIN = os.environ.get("PETCARE_E2E_WEB_ORIGIN", "http://localhost:3100")
OUTBOX = os.environ.get("PETCARE_E2E_OUTBOX") or str(Path(os.environ.get("TMPDIR", "/tmp")) / "petcare-e2e-outbox.jsonl")
#: Per-run TOTP secrets of seeded staff (D2g), beside the outbox in TMPDIR — never in the repository.
MFA_FILE = os.environ.get("PETCARE_E2E_MFA_FILE") or str(Path(OUTBOX).with_suffix(".mfa.json"))


#: R19.4: production configuration is `PETCARE_SECRET_MODE=aws_secrets_manager` (petcare_api/secret_provider.py; `environment`
#: is admissible only off production). This tool — and above all its per-run TOTP seeding, which writes a CONFIRMED factor
#: without enrolment — never runs under it. Standing test: tests/governance/test_r19_4_step_up_seeding_unreachable.py.
PRODUCTION_SECRET_MODE = "aws_secrets_manager"


def _refuse_production() -> None:
    if (os.environ.get("PETCARE_SECRET_MODE") or "").strip() == PRODUCTION_SECRET_MODE:
        raise SystemExit("R19.4: tools/e2e_stack.py is test-only and refuses production configuration "
                         f"(PETCARE_SECRET_MODE={PRODUCTION_SECRET_MODE}); nothing was started or seeded")


def _env(db_url: str) -> None:
    os.environ.update({
        "SECRET_KEY": "e2e-only-session-signing-key-not-a-deployed-secret",
        "PETCARE_SECRET_MODE": "environment",
        "PETCARE_PERSISTENCE_MODE": "postgres",
        "PETCARE_DB_URL": db_url,
        "PETCARE_DOCUMENT_STORE_MODE": "local",
        "PETCARE_DOCUMENT_ROOT": str(Path(os.environ.get("TMPDIR", "/tmp")) / "petcare-e2e-documents"),
        "PETCARE_MFA_ENCRYPTION_KEY": "e2e-only-mfa-key-not-a-deployed-secret",
        "PETCARE_FINANCE_ENCRYPTION_KEY": "e2e-only-finance-key-not-a-deployed-secret",
        # The journey suite drives many requests from one browser; NFR-15 limits stay enforced, just generous here.
        "PETCARE_RATE_LIMIT_PRINCIPAL_PER_MIN": "100000",
        "PETCARE_RATE_LIMIT_ANONYMOUS_PER_MIN": "100000",
        "ALLOWED_ORIGINS": WEB_ORIGIN,
        # Sponsor ruling 1: owner self-registration is ON in test/staging (production default OFF). Email goes to the
        # FAKE adapter, which writes a JSON-lines outbox the journey suite reads.
        "PETCARE_OWNER_SELF_REGISTRATION": "on",
        "PETCARE_SELF_REGISTRATION_TENANT": TENANT,
        "PETCARE_EMAIL_ADAPTER": "fake",
        "PETCARE_FAKE_EMAIL_OUTBOX": OUTBOX,
        "PETCARE_PUBLIC_WEB_ORIGIN": WEB_ORIGIN,
    })
    Path(OUTBOX).write_text("", encoding="utf-8")            # a fresh outbox per stack


def _database() -> str:
    import pg_harness
    admin = os.environ.get("PETCARE_E2E_PG_URL") or pg_harness.start_ephemeral_cluster()
    pg_harness.create_database(admin, "petcare_e2e")
    from urllib.parse import urlsplit, urlunsplit
    parts = urlsplit(admin)                       # the server's resolver takes a URL, not a key=value conninfo
    url = urlunsplit(parts._replace(path="/petcare_e2e"))
    applied = pg_harness.replay_migrations(url)
    print(f"[e2e] fresh database petcare_e2e; {applied} migrations applied from empty", flush=True)
    return url


def _seed() -> None:
    # R19.4: the seeding runs only under the test secret mode `_env` sets; anything else (production, or unset) is refused.
    if (os.environ.get("PETCARE_SECRET_MODE") or "").strip() != "environment":
        raise SystemExit("R19.4: test-only step-up seeding refused outside PETCARE_SECRET_MODE=environment")
    from datetime import datetime, timedelta, timezone
    from uuid import uuid4

    import main as api
    from practitioners import CLASS_VETERINARIAN, PractitionerAuthorityGrant
    from routers import auth
    from tenant_fixtures import ensure_tenant

    ensure_tenant(TENANT, persistence=api.PERSISTENCE)
    for user_id, email, role, name in USERS:
        auth.seed_user(user_id, email, SEED_PASSWORD, role, full_name=name, tenant_id=TENANT)
    now = datetime.now(timezone.utc)
    api.PERSISTENCE.practitioners.grant(PractitionerAuthorityGrant(
        grant_id=str(uuid4()), tenant_id=TENANT, actor_id="u-e2e-vet", professional_class=CLASS_VETERINARIAN,
        licence_ref="E2E-SYNTHETIC-LICENCE", effective_from=now - timedelta(minutes=1),
        granted_by_actor_id="e2e-seed", granted_at=now))
    # D2g (J-O7): issuing a prescription is an SQ-3 operation (MFA enrolment + step-up). The seeded veterinarian gets a
    # confirmed TOTP factor whose secret is random PER STACK RUN and is written only next to the run's outbox (TMPDIR),
    # never into the repository; journeys read it to step up through the real /api/me/mfa/step-up.
    import base64
    import json
    import mfa as mfa_mod
    secret = os.urandom(20)
    nonce, ct = mfa_mod.encrypt(api._mfa_key(), secret)
    api.MFA_REPO.put_factor(mfa_mod.Factor(user_id="u-e2e-vet", nonce=nonce, ciphertext=ct, created_at=now, confirmed_at=now))
    Path(MFA_FILE).write_text(json.dumps({"u-e2e-vet": base64.b32encode(secret).decode()}), encoding="utf-8")
    # D2m (J-O8): product registration has no served route (registration feed only, AC-FR-04-03). Two SYNTHETIC products: one
    # GENERAL an owner may buy, one POM an owner must never be able to buy. Prices, stock, location and licence are set by
    # the journey itself through the served routes (clinic admin / platform admin).
    from inventory import REGISTRATION_SOURCE, ProductRegistration
    for pid, name, cls in PRODUCTS:
        api.INVENTORY_REPO.register_product(ProductRegistration(product_id=pid, name=name, supply_class=cls,
                                                                source=REGISTRATION_SOURCE, registered_at=now))
    print(f"[e2e] seeded tenant {TENANT}, {len(USERS)} synthetic users and {len(PRODUCTS)} synthetic products", flush=True)


def _exit_on_signal(*_args) -> None:
    raise SystemExit(0)


def main() -> None:
    # pg_harness stops its throwaway cluster via atexit, which a SIGTERM/SIGHUP does not run. Playwright ends its web
    # servers with a signal, so without this every journey run leaked one running cluster (and its SysV shared-memory
    # segment) until the machine's segment limit refused new clusters (D2d finding D2D-E2E-CLUSTER-LEAK).
    import signal
    for sig in (signal.SIGTERM, signal.SIGHUP):
        signal.signal(sig, _exit_on_signal)
    _refuse_production()                      # R19.4 — before any database is created or touched
    _env(_database())
    _seed()
    import uvicorn
    import main as api
    uvicorn.run(api.app, host="127.0.0.1", port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
