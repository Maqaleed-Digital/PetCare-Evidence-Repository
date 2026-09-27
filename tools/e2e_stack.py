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
PORT = int(os.environ.get("PETCARE_E2E_API_PORT", "8090"))
WEB_ORIGIN = os.environ.get("PETCARE_E2E_WEB_ORIGIN", "http://localhost:3100")


def _env(db_url: str) -> None:
    os.environ.update({
        "SECRET_KEY": "e2e-only-session-signing-key-not-a-deployed-secret",
        "PETCARE_SECRET_MODE": "environment",
        "PETCARE_PERSISTENCE_MODE": "postgres",
        "PETCARE_DB_URL": db_url,
        "PETCARE_DOCUMENT_STORE_MODE": "local",
        "PETCARE_DOCUMENT_ROOT": str(Path(os.environ.get("TMPDIR", "/tmp")) / "petcare-e2e-documents"),
        "PETCARE_MFA_ENCRYPTION_KEY": "e2e-only-mfa-key-not-a-deployed-secret",
        # The journey suite drives many requests from one browser; NFR-15 limits stay enforced, just generous here.
        "PETCARE_RATE_LIMIT_PRINCIPAL_PER_MIN": "100000",
        "PETCARE_RATE_LIMIT_ANONYMOUS_PER_MIN": "100000",
        "ALLOWED_ORIGINS": WEB_ORIGIN,
    })


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
    print(f"[e2e] seeded tenant {TENANT} and {len(USERS)} synthetic users", flush=True)


def main() -> None:
    _env(_database())
    _seed()
    import uvicorn
    import main as api
    uvicorn.run(api.app, host="127.0.0.1", port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
