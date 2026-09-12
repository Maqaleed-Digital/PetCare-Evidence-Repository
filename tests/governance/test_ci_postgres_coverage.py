"""Every PostgreSQL suite must be named in the CI non-skip step.

That step exists because a skipped integration suite and a passing one are
indistinguishable in a summary line. It has fallen behind the tree **three
times** — the W0-F identity-migration and W0-G audit suites, then the
tenant-registry and end-to-end identity suites, then the tenant-membership
suite — and on every occasion it kept passing while real controls sat outside
it.

A guard blind to the code it exists to cover is the same shape as the
portability guard that was not scanning `scripts/`, and the retired-role guard
whose needle could not see a short form.

The list in the workflow stays **explicit**. Deriving it by globbing would
silently include a file nobody meant to gate on, and a gate that assembles
itself is no longer a decision anybody made. What this control changes is that
forgetting to extend it fails the build instead of passing quietly.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "verify.yml"
API_TESTS = ROOT / "petcare_api" / "tests"

#: The step whose command must name every suite.
_STEP_NAME = "PostgreSQL controls must not be skipped"


def _postgres_suites() -> list[str]:
    """Test files that require a PostgreSQL server.

    Identified by name rather than by reading their contents: a suite that needs
    a database is named for it in this estate, and a content sniff would drift
    from the convention the moment somebody imported psycopg for a helper.
    """
    return sorted(
        p.name for p in API_TESTS.glob("test_*postgres*.py")
    )


def _step_command() -> str:
    text = WORKFLOW.read_text(encoding="utf-8")
    idx = text.index(_STEP_NAME)
    # From the step to the start of the next step at the same indent.
    rest = text[idx:]
    end = rest.find("\n      - name:")
    return rest if end == -1 else rest[:end]


def test_the_step_still_exists():
    """Without this the assertion below would pass vacuously if the step were
    renamed or removed."""
    text = WORKFLOW.read_text(encoding="utf-8")
    assert _STEP_NAME in text, "the PostgreSQL non-skip step is gone"


def test_the_suite_discovery_is_not_vacuous():
    suites = _postgres_suites()
    assert len(suites) >= 6, f"PostgreSQL suite discovery collapsed to {suites}"


def test_every_postgres_suite_is_named_in_the_ci_non_skip_step():
    command = _step_command()
    missing = [s for s in _postgres_suites() if s not in command]
    assert missing == [], (
        "these PostgreSQL suites are not named in the CI non-skip step, so the "
        f"step would pass while they were skipped: {missing}"
    )


def test_the_step_fails_the_build_when_anything_is_skipped():
    """The step's own logic, asserted — a list of suites that did not check for
    skips would be a list."""
    command = _step_command()
    assert "skipped" in command
    assert "exit 1" in command
    assert re.search(r"grep -qE '\[0-9\]\+ passed'", command) or "passed" in command
