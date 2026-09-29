"""MVC-EPC-D-001 D2d — Sponsor ruling R12: the Lane-D harness removes a scratch PostgreSQL data directory ONLY on
positive proof that this harness created it. Zero client connections, a stopped server and a familiar path are never
proof. Every case uses a synthetic directory under pytest's tmp_path except the last, which starts a real cluster."""
import json
import os
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pg_harness as h  # noqa: E402


def _cluster_like(parent: Path, name: str) -> Path:
    """A stopped cluster's shape: a data directory with PG_VERSION and no postmaster.pid (so zero connections)."""
    d = parent / name
    d.mkdir()
    (d / "PG_VERSION").write_text("16\n")
    return d


def _mark(d: Path, **override) -> str:
    h._write_marker(str(d), "nonce-1")
    if override:
        m = json.loads((d / h.MARKER_NAME).read_text())
        m.update(override)
        (d / h.MARKER_NAME).write_text(json.dumps(m))
    return "nonce-1"


# 1. marked / proven Lane-D scratch resource -> eligible, and removed
def test_a_marked_harness_directory_is_proven_and_removed(tmp_path):
    d = _cluster_like(tmp_path, "petcare-pg-proven")
    nonce = _mark(d)
    assert h.ownership_proof(d, run_nonce=nonce) == (True, "PROVEN_HARNESS_OWNED")
    assert h.cleanup_owned_cluster(d, run_nonce=nonce) == (True, "PROVEN_HARNESS_OWNED") and not d.exists()


# 2. unmarked -> refused (untouched)
def test_an_unmarked_directory_with_the_harness_name_is_refused(tmp_path):
    d = _cluster_like(tmp_path, "petcare-pg-unmarked")
    assert h.cleanup_owned_cluster(d) == (False, "UNMARKED") and (d / "PG_VERSION").exists()


# 3. ambiguous ownership -> refused
@pytest.mark.parametrize("damage, reason", [
    (lambda d: (d / h.MARKER_NAME).write_text("{not json"), "AMBIGUOUS_MARKER_UNREADABLE"),
    (lambda d: _mark(d, owner="someone-else"), "AMBIGUOUS_MARKER_OWNER"),
    (lambda d: _mark(d, run_nonce=""), "AMBIGUOUS_MARKER_OWNER"),
    (lambda d: _mark(d, datadir="/elsewhere/petcare-pg-original"), "AMBIGUOUS_MARKER_NOT_BOUND_TO_THIS_DIRECTORY"),
])
def test_an_ambiguous_marker_is_refused(tmp_path, damage, reason):
    d = _cluster_like(tmp_path, "petcare-pg-ambiguous")
    damage(d)
    assert h.cleanup_owned_cluster(d) == (False, reason) and d.exists()


def test_a_marker_copied_from_a_proven_directory_does_not_transfer_ownership(tmp_path):
    src = _cluster_like(tmp_path, "petcare-pg-source")
    _mark(src)
    dst = _cluster_like(tmp_path, "petcare-pg-copy")
    shutil.copy(src / h.MARKER_NAME, dst / h.MARKER_NAME)
    assert h.cleanup_owned_cluster(dst) == (False, "AMBIGUOUS_MARKER_NOT_BOUND_TO_THIS_DIRECTORY") and dst.exists()


def test_another_runs_marker_is_refused_when_this_run_cleans_up(tmp_path):
    d = _cluster_like(tmp_path, "petcare-pg-other-run")
    _mark(d)
    assert h.cleanup_owned_cluster(d, run_nonce="nonce-2") == (False, "AMBIGUOUS_MARKER_OTHER_RUN") and d.exists()


# 4. unrelated resource -> refused, even when it carries a valid-looking marker
def test_an_unrelated_directory_is_refused(tmp_path):
    d = _cluster_like(tmp_path, "pgdata")
    _mark(d)
    assert h.cleanup_owned_cluster(d) == (False, "UNRELATED_NAME") and d.exists()
    assert h.cleanup_owned_cluster(tmp_path / "does-not-exist") == (False, "NOT_A_DIRECTORY")


# 5. zero connections without an ownership marker -> refused
def test_a_stopped_zero_connection_cluster_without_a_marker_is_refused(tmp_path):
    d = _cluster_like(tmp_path, "petcare-pg-idle")
    assert not (d / "postmaster.pid").exists()                     # stopped: no server, therefore no connections
    assert h.cleanup_owned_cluster(d) == (False, "UNMARKED") and (d / "PG_VERSION").exists()


# the real harness writes a proof-bearing marker and its own stop path removes exactly its own cluster
@pytest.mark.skipif(not (shutil.which("initdb") and shutil.which("pg_ctl")), reason="initdb/pg_ctl not on PATH")
def test_the_harness_marks_its_cluster_before_start_and_removes_only_that(tmp_path, monkeypatch):
    import subprocess
    import tempfile
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    monkeypatch.setattr(h, "_CLUSTER", {})
    stops = []
    monkeypatch.setattr(h.atexit, "register", stops.append)
    h.start_ephemeral_cluster()
    d = Path(h._CLUSTER["datadir"])
    try:
        assert d.name.startswith(h.DATADIR_PREFIX) and (d / "postmaster.pid").exists()
        assert h.ownership_proof(d, run_nonce=h._CLUSTER["run_nonce"]) == (True, "PROVEN_HARNESS_OWNED")
        bystander = _cluster_like(tmp_path, "petcare-pg-bystander")
        (stop,) = stops
        stop()
        assert not d.exists() and bystander.exists()
        assert subprocess.run(["pg_ctl", "-D", str(d), "status"], capture_output=True).returncode != 0
    finally:
        # Test hygiene, not the harness cleanup path: if an assertion above failed, STOP (never delete) the server this
        # test process started seconds ago in its own tmp_path, so a failing run does not leave a postmaster behind.
        if (d / "postmaster.pid").exists():
            subprocess.run(["pg_ctl", "-D", str(d), "-m", "immediate", "stop"], capture_output=True)
