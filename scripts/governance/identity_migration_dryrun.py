#!/usr/bin/env python3
"""The identity migration, rehearsed. Nothing production is touched.

`MVC-W0F-IDENTITY-MIGRATION-PLAN-001` §11 specifies this tool and §14 keeps its
production application behind `GATE_LIVE_APPLY` + `GATE_IRREVERSIBLE_ACTION`.
The plan's own §1 states the fact that makes rehearsing it cheap now and
expensive later:

> **there are no persisted credentials today.** Everything is re-seeded at each
> start. The migration is therefore not a data move at all in the current state —
> it is a change of where future identity is written.

## The one rule everything below follows

**Nothing is guessed.** A record that cannot be mapped deterministically is
quarantined with its reason, and quarantined records are not written to the
authoritative identity table — the database refuses them structurally, so the
rule does not depend on this file continuing to obey it.

The reason is stated in the plan and is worth repeating: an inferred value is
indistinguishable from a verified one once written. Afterwards nobody can tell
which identities were migrated and which were reconstructed.

## Why the role map is identity-preserving

Each known role spelling maps to ITSELF. That looks like a no-op and is the
point: the estate currently mints two vocabularies for the same roles (recorded
authority conflict CONF-01), and a migration that normalised them would change
which identities `require_role()` accepts. Changing who may act is a Sponsor
product decision, and a migration is the worst place to take one — the change
would be invisible afterwards, since the target would simply show the new
spelling as though it had always been held.

## Why duplicates quarantine ALL sides

When an email appears more than once in the source, every record carrying it is
quarantined. Keeping the first, or the most recently modified, is a guess about
which identity is the real one — and the survivor would be indistinguishable
from an uncontested record.

## Apply mode

`--apply` requires an explicit `--database-url` and will NOT resolve one from the
governed secret source. A tool that could find production by reading the same
configuration the application reads is one flag away from writing to it.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "petcare_api"))

from roles import VALID_ROLES, is_privilege_elevation  # noqa: E402

# -- quarantine reasons, mirroring migration 0031's CHECK -------------------
UNRESOLVED_NO_TENANT = "UNRESOLVED_NO_TENANT"
UNRESOLVED_UNKNOWN_TENANT = "UNRESOLVED_UNKNOWN_TENANT"
UNRESOLVED_UNKNOWN_ROLE = "UNRESOLVED_UNKNOWN_ROLE"
UNRESOLVED_DUPLICATE = "UNRESOLVED_DUPLICATE"
UNRESOLVED_MALFORMED_RECORD = "UNRESOLVED_MALFORMED_RECORD"

#: The explicit role map. Identity-preserving by construction — see the module
#: docstring. Built from the catalogue rather than typed out, so a role added to
#: the catalogue cannot be silently absent here, and no role can be mapped to a
#: different one by editing a table.
ROLE_MAP: Mapping[str, str] = {role: role for role in sorted(VALID_ROLES)}

#: Password hash formats this estate knows. `scrypt` is what W0-J produces; the
#: other two are legacy formats `_verify_password` still accepts precisely so a
#: credential can upgrade itself on next login. Anything else is not carried:
#: an unrecognised hash is a credential nobody can verify, and migrating it
#: produces an account that can never be signed into and never be told why.
_SCRYPT = re.compile(r"^scrypt\$\d+\$\d+\$\d+\$[0-9a-f]+\$[0-9a-f]+$")
_BCRYPT = re.compile(r"^\$2[aby]?\$\d{2}\$[./A-Za-z0-9]{53}$")
_LEGACY_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def classify_password_hash(value: object) -> Optional[str]:
    """`GOVERNED`, `LEGACY_UPGRADES_ON_LOGIN`, or None if unrecognised."""
    if not isinstance(value, str) or not value:
        return None
    if _SCRYPT.match(value):
        return "GOVERNED"
    if _BCRYPT.match(value) or _LEGACY_SHA256.match(value):
        return "LEGACY_UPGRADES_ON_LOGIN"
    return None


@dataclass
class SourceRecord:
    """One identity as it exists in the source. Read, never repaired."""

    source_record_id: str
    user_id: Optional[str] = None
    email: Optional[str] = None
    password_hash: Optional[str] = None
    role: Optional[str] = None
    tenant_id: Optional[str] = None
    full_name: Optional[str] = None


@dataclass
class Quarantined:
    source_record_id: str
    reason: str
    source_role: Optional[str] = None
    source_tenant: Optional[str] = None
    source_email: Optional[str] = None


@dataclass
class Migratable:
    source_record_id: str
    user_id: str
    email: str
    password_hash: str
    role: str
    tenant_id: str
    full_name: str
    hash_format: str


@dataclass
class Reconciliation:
    source_count: int = 0
    migratable_count: int = 0
    quarantined_count: int = 0
    rejected_count: int = 0
    quarantine_reasons: dict = field(default_factory=dict)
    duplicate_emails: list = field(default_factory=list)
    checks: dict = field(default_factory=dict)


def _normalise_email(value: object) -> Optional[str]:
    """Case-folded and stripped — for COMPARISON only.

    The stored address keeps its original form. Normalising what is written
    would silently rewrite an identifier users type, and an address that changed
    during a migration is indistinguishable from one that was always different.
    What normalisation is for here is collision detection: `A@x` and `a@x` are
    the same login and must be seen as a duplicate rather than migrated as two
    identities.
    """
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped.casefold() if stripped else None


def plan_migration(
    records: Iterable[SourceRecord],
    *,
    tenant_map: Optional[Mapping[str, str]],
) -> tuple[list[Migratable], list[Quarantined], Reconciliation]:
    """Map every source record. Pure: reads nothing, writes nothing.

    `tenant_map` is REQUIRED and has no default, though `None` is a legitimate
    value for it. The difference matters and it is the estate's own rule
    (`tests/governance/test_tenant_scope_signatures.py`): a tenant-bearing
    parameter that may be omitted is one that may be forgotten, and forgetting
    this one silently disables MIG-04 — every unrecognised tenant would be
    migrated instead of quarantined, and afterwards the migrated rows would be
    indistinguishable from verified ones.

    Passing `None` explicitly means "copy tenants verbatim", which is the plan's
    §4 rule — tenant is copied, never inferred. Passing a map additionally
    quarantines any tenant outside it. What never happens in either mode is a
    tenant being invented for a record that has none.
    """
    records = list(records)
    recon = Reconciliation(source_count=len(records))

    # Duplicate detection first, over the whole set: a duplicate is a property
    # of the set, not of a record, so it cannot be decided while streaming.
    seen: dict[str, int] = {}
    for rec in records:
        key = _normalise_email(rec.email)
        if key:
            seen[key] = seen.get(key, 0) + 1
    duplicates = {k for k, n in seen.items() if n > 1}
    recon.duplicate_emails = sorted(duplicates)

    migratable: list[Migratable] = []
    quarantined: list[Quarantined] = []

    def hold(rec: SourceRecord, reason: str) -> None:
        quarantined.append(Quarantined(
            source_record_id=rec.source_record_id, reason=reason,
            source_role=rec.role, source_tenant=rec.tenant_id,
            source_email=rec.email,
        ))

    for rec in records:
        email_key = _normalise_email(rec.email)

        # A record missing anything it needs is malformed, not repairable.
        if not rec.user_id or not email_key or not rec.full_name:
            hold(rec, UNRESOLVED_MALFORMED_RECORD)
            continue

        hash_format = classify_password_hash(rec.password_hash)
        if hash_format is None:
            hold(rec, UNRESOLVED_MALFORMED_RECORD)
            continue

        if email_key in duplicates:
            # Every side, not just the later ones. See the module docstring.
            hold(rec, UNRESOLVED_DUPLICATE)
            continue

        target_role = ROLE_MAP.get(rec.role) if isinstance(rec.role, str) else None
        if target_role is None:
            hold(rec, UNRESOLVED_UNKNOWN_ROLE)
            continue

        # MIG-03, checked rather than assumed. The map is identity-preserving, so
        # this can only fire if someone edits it — which is exactly when a silent
        # promotion would be introduced.
        if is_privilege_elevation(source_role=rec.role, target_role=target_role):
            hold(rec, UNRESOLVED_UNKNOWN_ROLE)
            continue

        tenant = rec.tenant_id
        if tenant is None or not str(tenant).strip():
            hold(rec, UNRESOLVED_NO_TENANT)
            continue
        if tenant_map is not None:
            mapped = tenant_map.get(tenant)
            if mapped is None:
                # Present but unrecognised — a different disposition from absent,
                # and recorded as such so a reviewer can tell them apart.
                hold(rec, UNRESOLVED_UNKNOWN_TENANT)
                continue
            tenant = mapped

        migratable.append(Migratable(
            source_record_id=rec.source_record_id,
            user_id=rec.user_id,
            email=rec.email.strip(),
            password_hash=rec.password_hash,
            role=target_role,
            tenant_id=tenant,
            full_name=rec.full_name,
            hash_format=hash_format,
        ))

    recon.migratable_count = len(migratable)
    recon.quarantined_count = len(quarantined)
    reasons: dict[str, int] = {}
    for q in quarantined:
        reasons[q.reason] = reasons.get(q.reason, 0) + 1
    recon.quarantine_reasons = reasons
    recon.checks = reconcile(records, migratable, quarantined)
    return migratable, quarantined, recon


def reconcile(
    records: list[SourceRecord], migratable: list[Migratable],
    quarantined: list[Quarantined],
) -> dict:
    """Plan §12, as booleans. Every one must be True before an apply."""
    by_id = {r.source_record_id: r for r in records}
    return {
        "no_row_lost": len(records) == len(migratable) + len(quarantined),
        "no_row_invented": all(m.source_record_id in by_id for m in migratable),
        "no_role_elevated": all(
            not is_privilege_elevation(
                source_role=by_id[m.source_record_id].role, target_role=m.role
            )
            for m in migratable
        ),
        "no_migrated_row_without_tenant": all(
            m.tenant_id and m.tenant_id.strip() for m in migratable
        ),
        "no_email_appears_twice": len({m.email.casefold() for m in migratable})
        == len(migratable),
        "every_hash_is_a_known_format": all(
            classify_password_hash(m.password_hash) is not None for m in migratable
        ),
        "no_plaintext_password_present": all(
            classify_password_hash(m.password_hash) is not None for m in migratable
        ),
    }


# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------

def records_from_json(path: Path) -> list[SourceRecord]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("the source export must be a JSON array of records")
    out = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"source record {i} is not an object")
        out.append(SourceRecord(
            source_record_id=str(item.get("source_record_id") or item.get("id") or i),
            user_id=item.get("user_id") or item.get("id"),
            email=item.get("email"),
            password_hash=item.get("password_hash"),
            role=item.get("role"),
            tenant_id=item.get("tenant_id"),
            full_name=item.get("full_name"),
        ))
    return out


def records_from_serving_registry() -> list[SourceRecord]:
    """The live in-memory registry — the plan's actual source (§1).

    Importing the serving module runs its seeding, which is what the source IS:
    there is no persisted credential store to read instead.
    """
    import os

    sys.path.insert(0, str(ROOT / "petcare_api"))

    # Importing the serving module runs its seeding, and that seeding IS the
    # source. The module refuses to import without these three, which is correct
    # for a process that will serve — and this process will not.
    #
    # `setdefault`, never an override: an operator who has configured the
    # environment keeps their configuration. The signing key below signs
    # nothing — this tool mints no cookie and issues no session — and is named so
    # that it cannot be mistaken for a deployed value in a log or a traceback.
    # It is deliberately not one of the placeholder tokens the provider refuses,
    # because it is a real value chosen for a real purpose rather than a value
    # somebody typed to make a process start.
    os.environ.setdefault("PETCARE_PERSISTENCE_MODE", "memory")
    os.environ.setdefault("PETCARE_SECRET_MODE", "environment")
    os.environ.setdefault("SECRET_KEY", "identity-migration-dryrun-signs-nothing")

    import main  # noqa: F401  — importing seeds the registry
    import routers.auth as auth

    repo = auth.IDENTITY_REPO
    identities = getattr(repo, "_by_id", None)
    if identities is None:
        raise RuntimeError(
            "the configured identity repository exposes no in-memory registry; "
            "point --source-json at an export instead of guessing at its internals"
        )
    return [
        SourceRecord(
            source_record_id=identity.user_id, user_id=identity.user_id,
            email=identity.email, password_hash=identity.password_hash,
            role=identity.role, tenant_id=identity.tenant_id,
            full_name=identity.full_name,
        )
        for identity in identities.values()
    ]


# ---------------------------------------------------------------------------
# Apply — ephemeral targets only, and never a configured one
# ---------------------------------------------------------------------------

def apply_to(url: str, migratable: list[Migratable],
             quarantined: list[Quarantined]) -> dict:
    """Write the planned migration to an EXPLICITLY NAMED database.

    One transaction for the whole set. A partially applied identity migration is
    worse than none: some identities can sign in, some cannot, and the difference
    is invisible from either side.
    """
    import psycopg

    written = 0
    held = 0
    with psycopg.connect(url) as conn:
        for m in migratable:
            conn.execute(
                "INSERT INTO user_identity (user_id, email, password_hash, role, "
                "full_name, tenant_id, provenance, source_record_id, created_at) "
                "VALUES (%s,%s,%s,%s,%s,%s,'IDENTITY_MIGRATION',%s,CURRENT_TIMESTAMP)",
                (m.user_id, m.email, m.password_hash, m.role, m.full_name,
                 m.tenant_id, m.source_record_id),
            )
            written += 1
        for q in quarantined:
            conn.execute(
                "INSERT INTO identity_migration_quarantine "
                "(source_record_id, reason, source_role, source_tenant, source_email) "
                "VALUES (%s,%s,%s,%s,%s) ON CONFLICT (source_record_id) DO NOTHING",
                (q.source_record_id, q.reason, q.source_role, q.source_tenant,
                 q.source_email),
            )
            held += 1
        conn.commit()
    return {"identities_written": written, "quarantine_written": held}


def render_report(recon: Reconciliation, migratable: list[Migratable],
                  quarantined: list[Quarantined], *, applied: Optional[dict]) -> str:
    lines = [
        "# Identity migration — reconciliation report",
        "",
        "```",
        f"IDENTITY_SOURCE_COUNT={recon.source_count}",
        f"IDENTITY_MIGRATABLE_COUNT={recon.migratable_count}",
        f"IDENTITY_QUARANTINED_COUNT={recon.quarantined_count}",
        f"IDENTITY_REJECTED_COUNT={recon.rejected_count}",
        f"APPLIED={'YES' if applied else 'NO (dry run — zero authoritative rows written)'}",
        "```",
        "",
        "## Reconciliation checks (plan §12)",
        "",
        "| check | result |",
        "|---|---|",
    ]
    for name, ok in recon.checks.items():
        lines.append(f"| {name} | {'PASS' if ok else 'FAIL'} |")
    lines += ["", "## Quarantine", ""]
    if quarantined:
        lines += ["| source_record_id | reason | source_role | source_tenant |",
                  "|---|---|---|---|"]
        for q in quarantined:
            lines.append(
                f"| `{q.source_record_id}` | {q.reason} | "
                f"`{q.source_role}` | `{q.source_tenant}` |"
            )
    else:
        lines.append("None.")
    lines += ["", "## Counts by reason", "", "```"]
    for reason, n in sorted(recon.quarantine_reasons.items()):
        lines.append(f"{reason}={n}")
    lines += ["```", ""]
    if recon.duplicate_emails:
        lines += ["## Duplicate identifiers", "",
                  "Every side of a duplicate is quarantined; choosing one would be a "
                  "guess about which identity is real.", ""]
        for e in recon.duplicate_emails:
            lines.append(f"- `{e}`")
        lines.append("")
    if applied:
        lines += ["## Applied", "", "```",
                  f"identities_written={applied['identities_written']}",
                  f"quarantine_written={applied['quarantine_written']}", "```", ""]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--source-json", type=Path,
                    help="a JSON export of source identities; default is the live "
                         "in-memory serving registry, which is the plan's source")
    ap.add_argument("--tenant-map", type=Path,
                    help="explicit source-tenant -> target-tenant map; without it "
                         "tenants are copied verbatim and never inferred")
    ap.add_argument("--apply", action="store_true",
                    help="write to --database-url. Requires it explicitly.")
    ap.add_argument("--database-url",
                    help="an EXPLICIT target. Never resolved from configuration: a "
                         "tool that could find production by reading the same "
                         "configuration the application reads is one flag away "
                         "from writing to it.")
    ap.add_argument("--report", type=Path, help="write the report here")
    args = ap.parse_args(argv)

    if args.apply and not args.database_url:
        print("APPLY_REFUSED: --apply requires an explicit --database-url",
              file=sys.stderr)
        return 2

    records = (records_from_json(args.source_json) if args.source_json
               else records_from_serving_registry())
    tenant_map = (json.loads(args.tenant_map.read_text(encoding="utf-8"))
                  if args.tenant_map else None)

    migratable, quarantined, recon = plan_migration(records, tenant_map=tenant_map)

    applied = None
    if args.apply:
        if not all(recon.checks.values()):
            failed = [k for k, v in recon.checks.items() if not v]
            print(f"APPLY_REFUSED: reconciliation checks failed: {failed}",
                  file=sys.stderr)
            return 2
        applied = apply_to(args.database_url, migratable, quarantined)

    report = render_report(recon, migratable, quarantined, applied=applied)
    if args.report:
        args.report.write_text(report, encoding="utf-8")
    print(report)
    return 0 if all(recon.checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
