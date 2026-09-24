"""MVC-BUILD-W1 standing controls for served routes, bindings and asserted engineering status.

REACHABLE_TESTED is engineering evidence only. These controls hold the measurement
current and honest; none of them asserts that a requirement is complete, and one
of them fails if any requirement claims acceptance.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True).strip())
REGISTER = ROOT / "requirements" / "register.yaml"
BINDINGS = ROOT / "requirements" / "bindings.json"
SERVED = ROOT / "requirements" / "served_routes.json"
STATUS = ROOT / "requirements" / "status.json"
LISTER = ROOT / "tools" / "list_served_routes.py"
CHECKER = ROOT / "tools" / "check_register.py"

#: The served object: petcare_api/Dockerfile runs `uvicorn main:app`.
SERVED_APP = "main:app"

EMITTABLE_STATES = {
    "ABSENT",
    "BINDING_BROKEN",
    "BUILT_UNWIRED",
    "REACHABLE_UNTESTED",
    "REACHABLE_TESTED",
}
FORBIDDEN_CLAIMS = {"ACCEPTED", "CLIENT_ACCEPTED"}
FITNESS_ENUMS = {
    "storage": {"PERSISTENT_POSTGRES", "IN_MEMORY", "FILE", "NONE", "UNKNOWN"},
    "tenant_source": {"SESSION", "CLIENT_SUPPLIED", "NONE", "UNKNOWN"},
    "audit_actor_source": {"SESSION", "CLIENT_SUPPLIED", "NONE", "UNKNOWN"},
}

# TEST/LOCAL configuration only, forced rather than defaulted: a regeneration
# must never be able to reach a deployed store.
NONPROD_ENV = {
    "SECRET_KEY": "test-only-not-a-deployed-secret",
    "PETCARE_SECRET_MODE": "environment",
    "PETCARE_PERSISTENCE_MODE": "memory",
    "PETCARE_DOCUMENT_STORE_MODE": "local",
    "PETCARE_DOCUMENT_ROOT": str(Path(tempfile.gettempdir()) / "petcare-test-documents"),
}


def _spine_ids():
    return re.findall(r"^  - id: (FR-\d{2})$", REGISTER.read_text(encoding="utf-8"), re.M)


@pytest.fixture(scope="module")
def checker_run():
    """One fresh run of the checker against the files as they are now."""
    return subprocess.run([sys.executable, str(CHECKER)], cwd=ROOT,
                          capture_output=True, text=True)


def test_served_routes_are_current():
    env = dict(os.environ, PYTHONPATH="petcare_api", **NONPROD_ENV)
    out = subprocess.run([sys.executable, str(LISTER), SERVED_APP], cwd=ROOT, env=env,
                         capture_output=True, text=True, check=True).stdout
    assert out == SERVED.read_text(encoding="utf-8"), (
        "requirements/served_routes.json drifted from the served application; regenerate it")


def test_status_is_current(checker_run):
    assert checker_run.returncode == 0, checker_run.stderr
    assert checker_run.stdout == STATUS.read_text(encoding="utf-8"), (
        "requirements/status.json drifted from its checker or inputs; regenerate it")


def test_no_binding_is_broken(checker_run):
    assert checker_run.returncode == 0, checker_run.stderr
    broken = {r["id"]: r["reasons"] for r in json.loads(checker_run.stdout)["requirements"]
              if r["status"] == "BINDING_BROKEN"}
    assert not broken, broken


def test_every_spine_requirement_has_a_binding_entry():
    pairs = []
    json.loads(BINDINGS.read_text(encoding="utf-8"), object_pairs_hook=lambda p: pairs.append(p) or dict(p))
    top = [k for k, _ in pairs[-1]]
    spine = _spine_ids()
    assert len(spine) == 31
    assert sorted(top) == sorted(spine), {
        "missing": sorted(set(spine) - set(top)), "unknown": sorted(set(top) - set(spine))}
    assert len(top) == len(set(top)), "an FR has more than one binding entry"


def test_no_requirement_claims_acceptance():
    doc = json.loads(STATUS.read_text(encoding="utf-8"))
    rows = doc["requirements"]
    assert sorted(r["id"] for r in rows) == sorted(_spine_ids())
    for r in rows:
        assert r["status"] in EMITTABLE_STATES, (r["id"], r["status"])
        assert r["acceptance_state"] == "CRITERIA_NOT_RATIFIED", (r["id"], r["acceptance_state"])
    claims = set(re.findall(r'"(?:status|acceptance_state)": "([A-Z_]+)"', STATUS.read_text(encoding="utf-8")))
    assert not claims & FORBIDDEN_CLAIMS, claims & FORBIDDEN_CLAIMS


def test_every_requirement_has_fitness_fields():
    bindings = json.loads(BINDINGS.read_text(encoding="utf-8"))
    for fr, entry in bindings.items():
        fit = entry["fitness"]
        assert set(fit) == set(FITNESS_ENUMS) | {"ui_surface", "basis"}, (fr, sorted(fit))
        for field, allowed in FITNESS_ENUMS.items():
            assert fit[field] in allowed, (fr, field, fit[field])
        assert isinstance(fit["ui_surface"], list), fr
        assert isinstance(fit["basis"], list) and fit["basis"], fr
