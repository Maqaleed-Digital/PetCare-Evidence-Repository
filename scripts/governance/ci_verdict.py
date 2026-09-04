"""Fail-closed CI verdict semantics.

Written after PR #3 merged with `statusCheckRollup = []` and the run that
merged it recorded "CI green". Nothing was green. Nothing had run. An empty
check set satisfies "no check failed" perfectly, which is why that predicate is
the wrong one: it cannot distinguish *passed* from *never attempted*.

The correct predicate has two clauses, and the first one is the one that was
missing:

    at least one REQUIRED check is present
    AND every required check succeeded

This is the same class of defect as a pytest run that exits 0 having collected
nothing, or a guard that passes because the register it reads is empty. The
absence of a failure is not evidence of a success.

The repository cannot make GitHub *enforce* a required check — that is branch
protection, which is external configuration. What it can do is refuse to
interpret an empty rollup as success anywhere it reads one.
"""
from __future__ import annotations

from enum import Enum
from typing import Iterable, Mapping

#: Check names that must be present and successful for a verdict of PASS.
#: Matches the job id in .github/workflows/verify.yml.
REQUIRED_CHECKS: frozenset[str] = frozenset({"verify"})

#: The only GitHub conclusion that counts as success. `skipped`, `neutral`,
#: `cancelled` and `stale` are each a way for a check to finish without having
#: evaluated the thing it exists to evaluate.
_SUCCESS = "success"


class Verdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_PROVEN = "NOT_PROVEN"


def ci_verdict(
    check_runs: Iterable[Mapping[str, object]],
    required: Iterable[str] = REQUIRED_CHECKS,
) -> Verdict:
    """Classify a GitHub check rollup.

    `check_runs` is the `statusCheckRollup` shape: mappings carrying at least
    `name` and `conclusion`.

    Returns NOT_PROVEN — never PASS — when a required check is absent, which
    covers the empty rollup, a workflow that never triggers on pull requests,
    and a workflow file sitting somewhere GitHub does not read.
    """
    required = set(required)
    if not required:
        raise ValueError(
            "no required checks configured; a verdict over an empty requirement "
            "set would be vacuous in exactly the way this module exists to prevent"
        )

    seen = {
        str(run.get("name")): str(run.get("conclusion") or "").lower()
        for run in check_runs
    }

    missing = required - set(seen)
    if missing:
        return Verdict.NOT_PROVEN

    if any(seen[name] != _SUCCESS for name in required):
        return Verdict.FAIL

    return Verdict.PASS


def describe(verdict: Verdict) -> str:
    return {
        Verdict.PASS: "required checks present and successful",
        Verdict.FAIL: "a required check did not succeed",
        Verdict.NOT_PROVEN: (
            "a required check is absent — nothing ran, so nothing is proven. "
            "This is NOT a pass."
        ),
    }[verdict]
