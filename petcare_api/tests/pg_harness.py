"""Ephemeral PostgreSQL harness for the W0-F integration suite.

Kept out of `conftest.py` so the helpers can be imported by name: a root-level
`conftest.py` also exists in this repository, so `from conftest import ...`
resolves to the wrong module — a collision that surfaces as an import error
several directories from its cause.

Local loopback, a temporary data directory, trust auth, nothing that outlives
the run. No credential, no external endpoint, no production reachability.
"""
from __future__ import annotations

import atexit
import os
import shutil
import socket
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = ROOT / "petcare_runtime" / "migrations"

_CLUSTER: dict = {}


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def start_ephemeral_cluster() -> str:
    """Start a throwaway local cluster and return an admin connection URL.

    `pg_ctl stop` is registered with `atexit`, so an interrupted run does not
    leave a postmaster and a data directory behind.
    """
    if "url" in _CLUSTER:
        return _CLUSTER["url"]
    initdb = shutil.which("initdb")
    pg_ctl = shutil.which("pg_ctl")
    if not initdb or not pg_ctl:
        raise RuntimeError("initdb/pg_ctl not found on PATH")

    datadir = tempfile.mkdtemp(prefix="petcare-pg-")
    user = "petcare_test"
    subprocess.run(
        [initdb, "-D", datadir, "-U", user, "--auth=trust",
         "--encoding=UTF8", "--locale=C"],
        check=True, capture_output=True, text=True,
    )
    port = _free_port()
    subprocess.run(
        [pg_ctl, "-D", datadir, "-w", "-o",
         # Unix sockets are disabled rather than pointed at the data directory:
         # libpq refuses a socket path longer than 103 bytes, and a temporary
         # directory is easily longer than that.
         f"-p {port} -c listen_addresses=127.0.0.1 -c unix_socket_directories=",
         "-l", os.path.join(datadir, "server.log"), "start"],
        check=True, capture_output=True, text=True,
    )

    def _stop() -> None:
        subprocess.run([pg_ctl, "-D", datadir, "-m", "immediate", "stop"],
                       capture_output=True, text=True)
        shutil.rmtree(datadir, ignore_errors=True)

    atexit.register(_stop)
    _CLUSTER["url"] = f"postgresql://{user}@127.0.0.1:{port}/postgres"
    return _CLUSTER["url"]


def migration_files() -> list[Path]:
    """The chain, in the order it is replayed.

    Sorted by full filename rather than by parsed ordinal, because two parallel
    numbering series exist in this estate — `0008_ep05_wave03_ai_eval.sql` and
    `0008_ep08_financial_execution_checkpoint.sql` are different migrations with
    the same number. Filename order is total and reproducible; an ordinal sort
    is ambiguous exactly where a collision occurs, which is the one place
    ordering matters.
    """
    return sorted(MIGRATIONS_DIR.glob("*.sql"))


def replay_migrations(url: str) -> int:
    """Apply every migration to a database. Returns the count applied."""
    import psycopg

    applied = 0
    with psycopg.connect(url, autocommit=True) as conn:
        for path in migration_files():
            conn.execute(path.read_text(encoding="utf-8"))
            applied += 1
    return applied


def create_database(admin_url: str, name: str) -> str:
    import psycopg

    with psycopg.connect(admin_url, autocommit=True) as conn:
        conn.execute(f'DROP DATABASE IF EXISTS "{name}"')
        conn.execute(f'CREATE DATABASE "{name}"')
    return psycopg.conninfo.make_conninfo(admin_url, dbname=name)


def drop_database(admin_url: str, name: str) -> None:
    import psycopg

    with psycopg.connect(admin_url, autocommit=True) as conn:
        conn.execute(
            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
            "WHERE datname = %s AND pid <> pg_backend_pid()", (name,)
        )
        conn.execute(f'DROP DATABASE IF EXISTS "{name}"')


def reset_w0f_tables(url: str) -> None:
    """Empty the W0-F and W0-G tables, in dependency order.

    Rows are removed rather than the schema recreated: recreating would re-prove
    the migration rather than the adapter, and would hide a constraint that only
    exists on a table the tests never rebuilt.
    """
    import psycopg

    with psycopg.connect(url, autocommit=True) as conn:
        # FR-13 (migration 0041): stock_movement refuses row DELETE by trigger (an
        # immutable ledger), so the fixture reset TRUNCATEs it, which fires no row
        # trigger. This is the test owner emptying a scratch database, not an
        # application path; both reference tenant, so they go first.
        conn.execute("TRUNCATE recall_notification, recall, delivery_completion, delivery_alert, "
                     "temperature_reading, delivery, stock_movement, inventory_location, "
                     "product_registration")  # + FR-16 (0045), FR-19 (0046)
        for table in ("app_session", "invite_code",
                      "identity_migration_quarantine", "audit_event",
                      # Option A (migration 0036). These reference BOTH
                      # prescription and tenant, so they are emptied before
                      # either — the same dependency trap platform_admin_genesis
                      # documents below, and with the same failure mode: the
                      # tenant delete raises and every suite sharing this
                      # database errors in teardown rather than in the test that
                      # created the row.
                      # FR-02 pet profile (migration 0037). Children before
                      # pet_profile, and all three before tenant.
                      # FR-23 (migration 0048): reminders and completions before the due
                      # item, which references pet_profile.
                      "care_reminder", "pet_care_completion", "pet_care_due",
                      "pet_identification", "pet_medical_record", "pet_profile",
                      # FR-09 (migration 0038) references user_identity and tenant.
                      "user_preference",
                      # FR-20 (migration 0047): receipt before collection before order.
                      "order_receipt", "order_collection", "customer_order_line", "customer_order",
                      "tenant_price",
                      # FR-05 (migration 0043): the verification references the licence,
                      # the grant and tenant; the licence references user_identity.
                      "vet_licence_verification", "vet_licence",
                      # FR-01 (migration 0039) references user_identity and tenant.
                      "practitioner_authority_grant",
                      # FR-06 (migration 0044): the outcome before the consultation; both
                      # reference tenant, the consultation references user_identity.
                      "consultation_outcome", "consultation", "regulatory_determination",
                      # FR-07 (migration 0040): children before consultation_message.
                      "notification_delivery_record", "consultation_message_attachment",
                      "consultation_message",
                      "prescription_document",
                      "prescription_status_transition", "prescription",
                      # The genesis consumption record references user_identity
                      # (migration 0035), so it is emptied before its parent.
                      # Omitting it does not merely leave a stale row: the FK
                      # makes the user_identity delete fail, and every suite
                      # sharing this database errors in teardown.
                      "platform_admin_genesis",
                      # Children before parents: user_identity and app_session
                      # both reference tenant (migration 0034).
                      "user_identity", "tenant"):
            conn.execute(f"DELETE FROM {table}")
        # The chain needs its HEAD reset too, not only its rows. Clearing the
        # table alone leaves the head pointing at the digest of a row that no
        # longer exists, so the next test's first append links to a vanished
        # predecessor and verify_chain reports prev_hash_mismatch — a clean chain
        # reported as tampering, in a test that did nothing wrong. Observed:
        # six controls failed together in one file and every one passed alone.
        conn.execute(
            "UPDATE audit_chain_head SET head_hash = %s, next_seq = 1 "
            "WHERE chain_id = %s", ("GENESIS", "default"),
        )
