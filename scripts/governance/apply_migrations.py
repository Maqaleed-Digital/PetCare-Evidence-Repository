#!/usr/bin/env python3
"""Apply the migration chain, once each, with a recorded ledger.

## Why this exists

The estate had thirty-six migrations and no way to apply them. That is not a
missing convenience — it is the reason the chain cannot simply be re-run:
`0001_ep01_ep02_baseline.sql` and `0002_ep01_ep02_wave_02.sql` create nine tables
with unguarded `CREATE TABLE`, so replaying the chain against a database that
already has them fails with `DuplicateTable` at the first one.

Discovered by running it. `MVC-W0F-KSA-MIGRATION-READINESS-001` §2 says the KSA
target is built by **replaying the migration chain**, and the production
activation pack's schema-apply phase says "apply migrations" — both of which
assume something that can apply them exactly once and know it did.

## Why the fix is a ledger and not `IF NOT EXISTS`

Adding `IF NOT EXISTS` to the two historical migrations would make the chain
re-runnable and would be the wrong repair. A migration is a record of what was
done; editing thirty-six of them to be individually idempotent moves the
correctness requirement into every future migration's text, where one omission
is invisible until a cutover. It would also make a partially-applied migration
silently resumable, which is precisely when it must not be.

A ledger puts the requirement in one place: a migration runs at most once, the
runner knows which have run, and each runs inside its own transaction so a
failure leaves either all or none of that file's statements applied.

## Drift detection

The ledger stores each applied file's SHA-256. If a file changes after being
applied, the runner refuses to continue. A migration edited after the fact means
the database and the repository disagree about what the schema IS, and every
later reconciliation compares against the edited text — so the drift would be
invisible in exactly the artefact meant to detect it.

## What this does NOT do

It does not decide WHERE to apply. The connection arrives from the governed
secret source or from an explicit argument; no endpoint, region or account is
named here (D.21). Applying against a production database is `GATE_LIVE_APPLY`
and is not authorised by this script existing.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = ROOT / "petcare_runtime" / "migrations"

#: The ledger. Created by the runner rather than by a migration, because it must
#: exist before the first migration can be recorded — a chicken-and-egg a
#: migration cannot solve for itself.
LEDGER_DDL = """
CREATE TABLE IF NOT EXISTS schema_migration (
    filename TEXT PRIMARY KEY,
    sha256 TEXT NOT NULL,
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""


class MigrationError(RuntimeError):
    """Something about the chain or the ledger is wrong. Never continued past."""


def migration_files() -> list[Path]:
    """The chain, in the order it is applied.

    Sorted by full filename rather than by parsed ordinal: two parallel
    numbering series exist here, so `0008_ep05_wave03_ai_eval.sql` and
    `0008_ep08_financial_execution_checkpoint.sql` share a number. Filename order
    is total and reproducible; an ordinal sort is ambiguous exactly where a
    collision occurs, which is the one place ordering matters.
    """
    return sorted(MIGRATIONS_DIR.glob("*.sql"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve_url(explicit: str | None) -> str:
    if explicit:
        return explicit
    sys.path.insert(0, str(ROOT / "petcare_api"))
    from secret_provider import resolve_database_url

    return resolve_database_url()


def plan(conn) -> tuple[list[Path], dict[str, str]]:
    """What has been applied, and what remains. Refuses on drift."""
    conn.execute(LEDGER_DDL)
    conn.commit()
    applied = {
        row[0]: row[1]
        for row in conn.execute("SELECT filename, sha256 FROM schema_migration").fetchall()
    }
    files = migration_files()
    if not files:
        raise MigrationError(
            f"no migrations found under {MIGRATIONS_DIR}; refusing to report an "
            "empty chain as fully applied"
        )
    by_name = {p.name: p for p in files}

    missing = sorted(set(applied) - set(by_name))
    if missing:
        raise MigrationError(
            f"the ledger records migrations that no longer exist in the "
            f"repository: {missing}. The database and the chain disagree about "
            "what the schema is."
        )

    drifted = [
        name for name, sha in applied.items() if digest(by_name[name]) != sha
    ]
    if drifted:
        raise MigrationError(
            f"these migrations were edited after being applied: {sorted(drifted)}. "
            "Refusing to continue: every later reconciliation compares against "
            "the edited text, so the drift would be invisible in the artefact "
            "meant to detect it."
        )

    pending = [p for p in files if p.name not in applied]
    return pending, applied


def apply_chain(url: str, *, dry_run: bool = False) -> dict:
    import psycopg

    with psycopg.connect(url) as conn:
        pending, applied = plan(conn)
        result = {
            "total": len(migration_files()),
            "already_applied": len(applied),
            "pending": [p.name for p in pending],
            "applied_now": [],
            "dry_run": dry_run,
        }
        if dry_run:
            return result

        for path in pending:
            # One transaction per migration. A file that fails leaves none of
            # its own statements applied and is not recorded, so the next run
            # retries exactly it — rather than resuming halfway through it.
            try:
                conn.execute(path.read_text(encoding="utf-8"))
                conn.execute(
                    "INSERT INTO schema_migration (filename, sha256) VALUES (%s, %s)",
                    (path.name, digest(path)),
                )
                conn.commit()
            except Exception as exc:
                conn.rollback()
                raise MigrationError(
                    f"{path.name} failed to apply ({type(exc).__name__}: {exc}). "
                    "Nothing from this file was applied and it is not recorded."
                ) from None
            result["applied_now"].append(path.name)
        return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--database-url",
        default=os.environ.get("PETCARE_MIGRATION_TARGET_URL"),
        help="target connection URL; omitted, it is resolved from the governed "
             "secret source",
    )
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would be applied and apply nothing")
    args = ap.parse_args(argv)

    try:
        result = apply_chain(_resolve_url(args.database_url), dry_run=args.dry_run)
    except MigrationError as exc:
        print(f"MIGRATION_RUN=REFUSED\n{exc}", file=sys.stderr)
        return 2

    print(f"MIGRATION_TOTAL={result['total']}")
    print(f"MIGRATION_ALREADY_APPLIED={result['already_applied']}")
    print(f"MIGRATION_PENDING={len(result['pending'])}")
    print(f"MIGRATION_APPLIED_NOW={len(result['applied_now'])}")
    print(f"MIGRATION_DRY_RUN={'YES' if result['dry_run'] else 'NO'}")
    for name in result["applied_now"]:
        print(f"  applied {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
