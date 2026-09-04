"""The CI verification contract, after an empty check set was read as green.

PR #3 merged into `main` with `statusCheckRollup = []`, and the run that merged
it recorded CI as green. Nothing was green; nothing had run. Three things had to
be true at once for that to happen, and all three were:

  1. Both root workflows trigger only on `release: published`, so neither can
     ever produce a pull-request check.
  2. The one workflow that DOES trigger on push and pull_request sits at
     `petcare_execution/.github/workflows/ci.yml` — a NESTED `.github`
     directory, which GitHub Actions does not read. Three workflow files, zero
     pull-request checks.
  3. The predicate in use was "no check failed", which an empty set satisfies
     perfectly.

The repository cannot make GitHub enforce a required check; that is branch
protection, which is external configuration and a Sponsor gate. What it can do
is refuse to call an empty rollup a pass, and keep a workflow where GitHub will
actually read it. Both are asserted here.

A note on the parser: `on:` is the YAML 1.1 boolean `True`, so `doc.get("on")`
returns None and any trigger assertion written that way passes vacuously
against every workflow ever written. The key is looked up as `True` with a
string fallback.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "governance"))

from ci_verdict import REQUIRED_CHECKS, Verdict, ci_verdict  # noqa: E402

WORKFLOW_DIR = ROOT / ".github" / "workflows"
VERIFY_WORKFLOW = WORKFLOW_DIR / "verify.yml"


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _triggers(doc: dict) -> dict:
    """The `on:` block, whatever YAML decided to call the key."""
    block = doc.get(True, doc.get("on"))
    if isinstance(block, str):
        return {block: None}
    if isinstance(block, list):
        return {k: None for k in block}
    return block or {}


# ---------------------------------------------------------------------------
# The verdict semantics — the defect itself
# ---------------------------------------------------------------------------

def test_an_empty_check_set_is_not_a_pass():
    """The exact PR #3 condition. This is the assertion whose absence let a
    merge be recorded as CI-green."""
    assert ci_verdict([]) is Verdict.NOT_PROVEN


def test_all_required_checks_green_is_a_pass():
    runs = [{"name": "verify", "conclusion": "SUCCESS"}]
    assert ci_verdict(runs) is Verdict.PASS


def test_a_failing_required_check_is_a_fail():
    runs = [{"name": "verify", "conclusion": "failure"}]
    assert ci_verdict(runs) is Verdict.FAIL


def test_a_skipped_required_check_is_not_a_pass():
    """`skipped`, `neutral` and `cancelled` each finish without evaluating the
    thing the check exists to evaluate. Only `success` counts."""
    for conclusion in ("skipped", "neutral", "cancelled", "stale", ""):
        assert ci_verdict([{"name": "verify", "conclusion": conclusion}]) is not Verdict.PASS


def test_unrelated_green_checks_do_not_substitute_for_a_required_one():
    """A rollup full of successes that does not contain the required check is
    still NOT_PROVEN. This is the empty case wearing a disguise."""
    runs = [
        {"name": "lint", "conclusion": "success"},
        {"name": "some-other-bot", "conclusion": "success"},
    ]
    assert ci_verdict(runs) is Verdict.NOT_PROVEN


def test_a_verdict_over_no_required_checks_is_refused():
    """An empty requirement set would make every rollup a pass — the same
    vacuity one level up."""
    with pytest.raises(ValueError):
        ci_verdict([{"name": "verify", "conclusion": "success"}], required=[])


# ---------------------------------------------------------------------------
# The workflow must exist where GitHub reads it, and trigger on pull requests
# ---------------------------------------------------------------------------

def test_a_verification_workflow_exists_at_the_repository_root():
    assert VERIFY_WORKFLOW.exists(), (
        "no verify workflow at .github/workflows/ — a workflow anywhere else is "
        "not read by GitHub Actions"
    )


def test_the_verification_workflow_triggers_on_pull_request():
    """The property PR #3 lacked. Without it a pull request can never carry a
    check, and the rollup is empty by construction."""
    triggers = _triggers(_load(VERIFY_WORKFLOW))
    assert "pull_request" in triggers, (
        f"verify.yml does not trigger on pull_request; triggers are {sorted(triggers)}"
    )


def test_the_trigger_parser_is_not_reading_none():
    """Positive control for the YAML 1.1 `on:`-is-True trap.

    `doc.get("on")` returns None on every one of these files, so a trigger
    assertion written that way passes against a workflow with no triggers at
    all. Proven here against a synthetic document rather than a real one.
    """
    doc = yaml.safe_load("name: x\non:\n  pull_request:\njobs: {}\n")
    assert doc.get("on") is None, "the trap has stopped being a trap; revisit"
    assert True in doc
    assert "pull_request" in _triggers(doc)
    assert _triggers(yaml.safe_load("name: x\njobs: {}\n")) == {}


def test_the_required_check_name_matches_a_real_job():
    """`REQUIRED_CHECKS` is what branch protection would be configured with. If
    it names a job that does not exist, the required check can never go green
    and the gate becomes unpassable rather than unmet."""
    jobs = _load(VERIFY_WORKFLOW)["jobs"]
    for check in REQUIRED_CHECKS:
        assert check in jobs, f"required check {check!r} names no job in verify.yml"


def test_the_release_only_workflows_are_recorded_as_unable_to_gate_a_pull_request():
    """Both pre-existing root workflows trigger only on `release: published`.
    They are legitimate; they simply cannot produce a pull-request check, and
    counting workflow FILES rather than pull-request triggers is what made the
    repository look covered."""
    pr_capable = [
        wf.name
        for wf in sorted(WORKFLOW_DIR.glob("*.yml"))
        if "pull_request" in _triggers(_load(wf))
    ]
    assert pr_capable == ["verify.yml"], (
        f"expected exactly verify.yml to gate pull requests, found {pr_capable}"
    )


def test_a_nested_dot_github_directory_is_not_counted_as_ci():
    """`petcare_execution/.github/workflows/ci.yml` triggers on push and
    pull_request and has never run once: GitHub Actions reads only the
    repository-root `.github/workflows`. It is left in place — deleting it is a
    separate decision — but it must never be counted as coverage.
    """
    nested = list(ROOT.glob("*/.github/workflows/*.yml"))
    for path in nested:
        assert path.parent.parent.parent != ROOT.parent, "sanity: path shape"
        assert not str(path).startswith(str(WORKFLOW_DIR)), (
            f"{path} is nested and is not read by GitHub Actions"
        )
    # Vacuity guard: if the nested file is ever removed this test must not
    # quietly stop asserting anything.
    assert nested, (
        "no nested .github workflows found; if they were removed, delete this "
        "test rather than letting it pass over an empty set"
    )


# ---------------------------------------------------------------------------
# The workflow must actually run the acceptance surface
# ---------------------------------------------------------------------------

def _verify_steps() -> list[dict]:
    return _load(VERIFY_WORKFLOW)["jobs"]["verify"]["steps"]


def test_the_workflow_runs_the_proven_acceptance_surface():
    """Each command is the one the evidence packs record. A workflow that
    installed dependencies and asserted nothing would still go green."""
    body = "\n".join(str(s.get("run", "")) for s in _verify_steps())
    for fragment in (
        "pytest tests petcare_runtime/tests petcare_api/tests",
        "npm run typecheck",
        "npm test",
        "npm run e2e",
        "verify_evidence_bundles.py",
    ):
        assert fragment in body, f"verify.yml does not run: {fragment}"


def test_the_workflow_uses_the_scripted_scanners_not_shell_one_liners():
    """Both scanners were shell one-liners and both were wrong.

    The secret scan matched its own regex and failed on a repository containing
    no secrets. The literal grep matched the docstring on the FIXED file and
    reported every ref as vulnerable. Scripts can be unit-tested against
    synthetic positives; a `grep` buried in YAML cannot.
    """
    body = "\n".join(str(s.get("run", "")) for s in _verify_steps())
    assert "scripts/governance/prohibited_literal_scan.py" in body
    assert "scripts/governance/secret_scan.py" in body
    assert "grep -rInE" not in body, "a shell secret grep has come back"


def test_the_workflow_carries_no_credentials():
    raw = VERIFY_WORKFLOW.read_text(encoding="utf-8")
    assert "${{ secrets." not in raw, (
        "verify.yml references a repository secret; the verification surface "
        "must run without one"
    )


def test_the_step_set_is_not_empty():
    steps = _verify_steps()
    assert len(steps) >= 10, f"verify job has only {len(steps)} steps"
    assert sum(1 for s in steps if s.get("run")) >= 6
