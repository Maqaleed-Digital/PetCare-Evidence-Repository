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
    """Empty the W0-F tables, in dependency order.

    Rows are removed rather than the schema recreated: recreating would re-prove
    the migration rather than the adapter, and would hide a constraint that only
    exists on a table the tests never rebuilt.
    """
    import psycopg

    with psycopg.connect(url, autocommit=True) as conn:
        for table in ("app_session", "invite_code",
                      "identity_migration_quarantine", "user_identity"):
            conn.execute(f"DELETE FROM {table}")
