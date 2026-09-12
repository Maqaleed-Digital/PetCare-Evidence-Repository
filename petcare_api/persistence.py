"""Which store the serving path uses — chosen explicitly, never inferred.

```
PETCARE_PERSISTENCE_MODE = memory | postgres
```

## The control this module exists to be

`PERSIST-01`: **a process configured for `postgres` whose database is
unreachable does not serve.** It raises, and the raise is not caught anywhere
that could turn it into a degraded start.

The failure being prevented is specific. A fallback from `postgres` to `memory`
looks like resilience and behaves like data loss with a clean health check: the
service answers, sign-in works, sessions are issued — and every one of them is
invisible to every other instance and gone at the next restart. Worse for W0-F
in particular, revocation silently stops working across instances, because a
session revoked in one process's memory is still live in another's. AC-7's whole
claim is that sessions are revocable; a silent memory fallback would make that
claim false while every test still passed.

So there is no `except` that widens into memory below, and there is no
"degraded" mode. The two modes are separate, explicit, and neither becomes the
other.

## Why `memory` still exists

It is the mode the test suite and local development run in, and it is governed:
selecting it is a deliberate act, and the receipts record which mode a run used.
What it must never be is the *silent* outcome of something else failing.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from audit_repository import InMemoryAuditRepository, PostgresAuditRepository
from postgres_repositories import (
    PersistenceUnavailable,
    PostgresIdentityRepository,
    PostgresInviteCodeRepository,
    PostgresQuarantineRepository,
    PostgresSessionStore,
    PostgresTenantRepository,
    open_pool,
)
from repositories import InMemoryIdentityRepository, InMemoryInviteCodeRepository
from tenants import InMemoryTenantRepository
from session_store import InMemorySessionStore

PERSISTENCE_MODE_ENV_VAR = "PETCARE_PERSISTENCE_MODE"
MODE_MEMORY = "memory"
MODE_POSTGRES = "postgres"
VALID_PERSISTENCE_MODES = frozenset({MODE_MEMORY, MODE_POSTGRES})


@dataclass(frozen=True)
class Persistence:
    """Everything the serving path needs, and the mode that produced it.

    `mode` is carried rather than inferred from the types, so a receipt or a
    status endpoint can state which store served a run without introspecting
    classes — and so a claim about durability cannot be made by looking at
    something that only correlates with it.
    """

    mode: str
    session_store: Any
    identities: Any
    invites: Any
    tenants: Any = None
    audit: Any = None
    quarantine: Optional[Any] = None
    pool: Optional[Any] = None

    @property
    def is_durable(self) -> bool:
        return self.mode == MODE_POSTGRES


def current_persistence_mode(environ: Optional[dict] = None) -> str:
    """The configured mode. Unset and unknown both fail closed.

    Unset does not default to `memory`. A deployment that forgot the variable is
    exactly the deployment that believed it was durable.
    """
    import os

    env = environ if environ is not None else os.environ
    mode = (env.get(PERSISTENCE_MODE_ENV_VAR) or "").strip()
    if not mode:
        raise PersistenceUnavailable(
            f"{PERSISTENCE_MODE_ENV_VAR} is not set. The serving store must be "
            f"chosen explicitly (one of {sorted(VALID_PERSISTENCE_MODES)}); an "
            "unset mode is not assumed to be the weaker one."
        )
    if mode not in VALID_PERSISTENCE_MODES:
        raise PersistenceUnavailable(
            f"{PERSISTENCE_MODE_ENV_VAR}={mode!r} is not a known persistence mode "
            f"(expected one of {sorted(VALID_PERSISTENCE_MODES)}); failing closed "
            "rather than picking one"
        )
    return mode


def build_persistence(
    environ: Optional[dict] = None,
    *,
    connection_url: Optional[str] = None,
    secret_provider: Optional[Any] = None,
) -> Persistence:
    """Build the configured persistence. Never silently substitutes a mode.

    `connection_url` is accepted so an integration test can point at its own
    ephemeral database without going through secret resolution twice. When it is
    absent the URL comes from the governed secret source, which is the only path
    a deployment takes.
    """
    import os

    env = environ if environ is not None else os.environ
    mode = current_persistence_mode(env)

    if mode == MODE_MEMORY:
        # The tenant registry is built FIRST and handed to the write paths, so
        # a tenant-scoped assignment is checked in memory mode exactly as the
        # foreign keys check it in PostgreSQL. A memory mode that skipped the
        # check would let the suite prove the weaker of the two.
        tenants = InMemoryTenantRepository()
        return Persistence(
            mode=MODE_MEMORY,
            session_store=InMemorySessionStore(tenants),
            identities=InMemoryIdentityRepository(tenants),
            invites=InMemoryInviteCodeRepository(),
            tenants=tenants,
            audit=InMemoryAuditRepository(),
        )

    # MODE_POSTGRES from here. Every failure path below raises; none returns a
    # Persistence built on memory.
    url = connection_url
    if url is None:
        from secret_provider import SecretUnavailable, resolve_database_url

        try:
            url = resolve_database_url(provider=secret_provider, environ=env)
        except SecretUnavailable as exc:
            raise PersistenceUnavailable(
                f"the database credential could not be obtained ({exc}); refusing "
                "to start without the store this mode requires"
            ) from None

    pool = open_pool(url)
    tenants = PostgresTenantRepository(pool)
    return Persistence(
        mode=MODE_POSTGRES,
        session_store=PostgresSessionStore(pool, tenants),
        identities=PostgresIdentityRepository(pool, tenants),
        tenants=tenants,
        invites=PostgresInviteCodeRepository(pool),
        audit=PostgresAuditRepository(pool),
        quarantine=PostgresQuarantineRepository(pool),
        pool=pool,
    )
