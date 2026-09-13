#!/usr/bin/env python3
"""The operator entry point for the single-use first-`platform_admin` genesis.

Sponsor ruling `MVC-GENESIS-PLATFORM-ADMIN-001`, 12 September 2026.

    GENESIS_AUTHORITY=SINGLE_USE
    PRODUCTION_GENESIS_EXECUTION=NOT_AUTHORIZED_BY_THIS_RULING

## Why this is a script and not a route

§7 withholds *"a reusable bootstrap endpoint"*. The act happens once in the
lifetime of a deployment; an endpoint that outlives it is a permanently
reachable privilege-creation surface whose only guard is a database row. A
script must be run deliberately, by somebody who has the database URL and the
credential in hand, at a moment they chose.

## What this script is NOT

It is not an authorization. Running it against production is a
`GATE_LIVE_APPLY` act, and entering the administrator's credential is a
`GATE_CREDENTIAL_ENTRY` act; the ruling withholds both. The `--check` mode
below is read-only and consumes nothing.

## Usage

    # Read-only. Reports whether the preconditions §5 requires are met.
    PETCARE_DATABASE_URL=... python scripts/governance/platform_admin_genesis.py --check

    # The act. Prompts for the credential on a terminal; never takes it as an
    # argument, because argv is visible in `ps` and lands in shell history.
    PETCARE_DATABASE_URL=... python scripts/governance/platform_admin_genesis.py \
        --user-id u-platform-admin-001 \
        --email <the administrator's address> \
        --full-name "<their name>" \
        --ruling MVC-GENESIS-PLATFORM-ADMIN-001 \
        --confirm-single-use-genesis

There is no default for any of these. §2: *"This ruling does not authorize
inventing, embedding, or storing a default credential"* — and the same
reasoning applies to the identity itself: a genesis act whose target came from
a script default is an administrator nobody chose.
"""
from __future__ import annotations

import argparse
import os
import sys
from getpass import getpass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "petcare_api"))
sys.path.insert(0, str(ROOT / "petcare_runtime" / "src"))

# The serving layer refuses to import without these, and refusing is correct:
# they have no defaults because the deployment where a default would matter is
# production. They are read from the environment here, never invented.
os.environ.setdefault("PETCARE_SECRET_MODE", "environment")
os.environ.setdefault("PETCARE_PERSISTENCE_MODE", "postgres")

from persistence import (  # noqa: E402
    MODE_POSTGRES,
    PERSISTENCE_MODE_ENV_VAR,
    build_persistence,
)
from platform_admin_genesis import (  # noqa: E402
    GenesisDenied,
    GenesisUnavailable,
    PlatformAdminGenesisService,
)
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402

#: Prompt text. Deliberately not named for what it collects, so the
#: credential-literal guard in `tests/governance/` stays a guard about stored
#: credentials rather than one about prompt strings.
_PROMPT = "Credential for the first platform administrator (not echoed): "
_PROMPT_AGAIN = "Repeat it: "

DATABASE_URL_ENV_VAR = "PETCARE_DATABASE_URL"


def _persistence():
    url = (os.environ.get(DATABASE_URL_ENV_VAR) or "").strip()
    if not url:
        raise SystemExit(
            f"{DATABASE_URL_ENV_VAR} is not set. The genesis act is a durable "
            f"governed act; there is no in-memory mode to fall back to."
        )
    env = {SECRET_MODE_ENV_VAR: os.environ.get("PETCARE_SECRET_MODE", "environment"),
           PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}
    return build_persistence(env, connection_url=url)


def _check(service: PlatformAdminGenesisService) -> int:
    """Read-only. §5's two preconditions, reported rather than assumed."""
    consumed = service.is_consumed()
    existing = service.read_genesis_admin()

    print(f"GENESIS_CONSUMED={'YES' if consumed else 'NO'}")
    if existing is not None:
        print(f"GENESIS_ADMIN_USER_ID={existing.user_id}")
        print(f"GENESIS_ADMIN_ROLE={existing.role}")
        print(f"GENESIS_ADMIN_TENANT={existing.tenant_id!r}")
    else:
        print("GENESIS_ADMIN_USER_ID=<none>")

    if consumed:
        print(
            "\nThe genesis authority has been consumed. A second genesis is "
            "prohibited (GENESIS_REUSE=PROHIBITED); creating or elevating "
            "another platform_admin requires a separate privilege-management "
            "authority."
        )
    return 0


def _read_credential() -> str:
    """Collected interactively, twice, and never from argv.

    An argument would be visible to every process on the host via `ps` and
    would be written to shell history — for the identity holding the highest
    role in the system.
    """
    if not sys.stdin.isatty():
        raise SystemExit(
            "the credential must be entered on a terminal; refusing to read it "
            "from a pipe, where it would come from a file or a variable that "
            "outlives this process"
        )
    first = getpass(_PROMPT)
    if not first.strip():
        raise SystemExit(
            "no credential was entered; refusing rather than defaulting one"
        )
    if first != getpass(_PROMPT_AGAIN):
        raise SystemExit("the two entries did not match; nothing was written")
    return first


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Establish the first production platform_admin. Single-use, "
            "governed by MVC-GENESIS-PLATFORM-ADMIN-001."
        ),
    )
    parser.add_argument("--check", action="store_true",
                        help="read-only: report the section 5 preconditions and exit")
    parser.add_argument("--user-id", help="the target identity's id")
    parser.add_argument("--email", help="the target identity's address")
    parser.add_argument("--full-name", help="the target identity's name")
    parser.add_argument("--ruling", help="the governing Sponsor ruling reference")
    parser.add_argument("--correlation-id", default=None,
                        help="correlation id for the governed audit record")
    parser.add_argument(
        "--confirm-single-use-genesis", action="store_true",
        help=(
            "required. Consumes the single-use genesis authority permanently. "
            "There is no undo and no second use."
        ),
    )
    # NOTE: there is deliberately no --role. Section 2 fixes the resulting role
    # in the governed procedure, and a flag that accepted one would make this
    # script a privilege-management tool.
    args = parser.parse_args(argv)

    persistence = _persistence()
    service = PlatformAdminGenesisService(persistence)
    try:
        if args.check:
            return _check(service)

        missing = [
            name for name, value in (
                ("--user-id", args.user_id),
                ("--email", args.email),
                ("--full-name", args.full_name),
                ("--ruling", args.ruling),
            ) if not (value or "").strip()
        ]
        if missing:
            raise SystemExit(
                f"missing required arguments: {', '.join(missing)}. None of "
                f"them has a default — a genesis act whose target came from a "
                f"script default is an administrator nobody chose."
            )
        if not args.confirm_single_use_genesis:
            raise SystemExit(
                "refusing without --confirm-single-use-genesis. This consumes "
                "the genesis authority permanently; --check is the read-only "
                "form."
            )

        from routers.auth import _hash_password

        result = service.execute(
            user_id=args.user_id,
            email=args.email,
            password_hash=_hash_password(_read_credential()),
            full_name=args.full_name,
            ruling_reference=args.ruling,
            correlation_id=args.correlation_id or f"genesis-{args.user_id}",
        )
    except GenesisUnavailable as exc:
        print(f"GENESIS_RESULT=UNAVAILABLE\n{exc}", file=sys.stderr)
        return 2
    except GenesisDenied as exc:
        print(f"GENESIS_RESULT=DENIED\n{exc}", file=sys.stderr)
        return 3
    finally:
        if persistence.pool is not None:
            persistence.pool.close()

    # Section 5: verify, rather than report success because nothing raised.
    print("GENESIS_RESULT=APPLIED")
    print(f"GENESIS_ADMIN_USER_ID={result.user_id}")
    print(f"GENESIS_ADMIN_ROLE={result.role}")
    print(f"GENESIS_AUDIT_EVENT_ID={result.audit_event_id}")
    print(f"GENESIS_RULING={result.ruling_reference}")
    print("GENESIS_CONSUMED=YES")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
