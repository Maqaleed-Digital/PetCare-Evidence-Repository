"""PORT-10 — the cross-repository traceability denominator.

Two repositories describe one product and neither holds the whole picture.
`petcare-evidence-repository` is canonical and carries the evidence, the seals
and the runtime; `petcare-platform` is LEGACY_TO_PORT_FROM and carries the
requirement register and the authority precedence table. Any coverage claim is
a join across both, and a join is only as honest as its denominator.

This module computes that join. It is deliberately a script rather than a
document, because the numbers in a document go stale silently and these ones
have: the handoff chain has carried `499` as RELAYED since 31 August.

The one thing it will not do is invent the product denominator. See
`unmeasurable()`.
"""
from __future__ import annotations

import glob
import os
import re
import sys
from collections import Counter
from pathlib import Path

CANONICAL_ROOT = Path(__file__).resolve().parents[2]
PORT_SOURCE_ROOT = Path(
    os.environ.get("MVC_PORT_SOURCE_ROOT", os.path.expanduser("~/dev/petcare-platform"))
)
PORT_SOURCE_GOVERNANCE = PORT_SOURCE_ROOT / "scripts" / "governance"


class PortSourceUnavailable(RuntimeError):
    """The port source is not checked out, so the join cannot be computed.

    Raised rather than returning partial numbers. A traceability report that
    quietly omitted half its inputs would read as a smaller estate rather than
    an incomplete measurement.
    """


# ---------------------------------------------------------------------------
# Path resolution — the instrument, and why it needs validating
# ---------------------------------------------------------------------------
#
# `source_path` in the authority table uses three shorthands that a literal
# `Path.exists()` cannot resolve: brace lists `{a,b}`, globs `PH-R*`, and
# alternatives separated by a comma OR a semicolon. Resolving them literally
# reports four of eleven authorities as missing — a 36% false-negative rate on
# a table whose whole purpose is to say what exists. The naive reading gives
# 7/11; the correct one gives 11/11.

_SEPARATORS = re.compile(r"[;,]")


def expand_spec(spec: str) -> list[str]:
    """Expand one `source_path` into concrete candidate paths."""
    spec = spec.split("#")[0]

    def brace(s: str) -> list[str]:
        m = re.search(r"\{([^}]*)\}", s)
        if not m:
            return [s]
        return [
            out
            for alt in m.group(1).split(",")
            for out in brace(s[: m.start()] + alt.strip() + s[m.end() :])
        ]

    parts: list[str] = []
    for chunk in brace(spec):
        parts += [p.strip() for p in _SEPARATORS.split(chunk) if p.strip()]
    return [os.path.expanduser(p) for p in parts]


def resolves(path: str) -> bool:
    """True when a candidate path names something that exists.

    Relative paths are resolved against the port source, which is where the
    authority table lives and therefore what its relative paths mean.
    """
    candidate = path if os.path.isabs(path) else str(PORT_SOURCE_ROOT / path)
    if any(ch in candidate for ch in "*?"):
        return bool(glob.glob(candidate))
    return os.path.exists(candidate)


def validate_instrument() -> None:
    """Prove the resolver discriminates, in both directions, before it is used.

    A resolver that returned True for everything and one that worked correctly
    produce the same clean report on a healthy table.
    """
    assert expand_spec("a/{x,y}/z") == ["a/x/z", "a/y/z"], "brace expansion broken"
    assert expand_spec("a.py; b/*.sh") == ["a.py", "b/*.sh"], "separator handling broken"
    assert resolves(str(CANONICAL_ROOT / "petcare_execution")), "known-present path unresolved"
    assert not resolves("/no/such/path/anywhere"), "known-absent path resolved"
    assert resolves(str(CANONICAL_ROOT / "petcare_execution" / "EP0*")), "glob under-matching"
    assert not resolves(str(CANONICAL_ROOT / "zzz-no-such-*")), "glob over-matching"


# ---------------------------------------------------------------------------
# The join
# ---------------------------------------------------------------------------

def _load_port_source():
    if not PORT_SOURCE_GOVERNANCE.is_dir():
        raise PortSourceUnavailable(
            f"port source governance not found at {PORT_SOURCE_GOVERNANCE}; "
            "set MVC_PORT_SOURCE_ROOT. The join was NOT computed."
        )
    if str(PORT_SOURCE_GOVERNANCE) not in sys.path:
        sys.path.insert(0, str(PORT_SOURCE_GOVERNANCE))
    from mvc_authorities import AUTHORITIES  # noqa: E402
    from mvc_requirements import REQUIREMENTS  # noqa: E402
    return AUTHORITIES, REQUIREMENTS


def compute() -> dict:
    validate_instrument()
    authorities, requirements = _load_port_source()

    resident = [
        a for a in authorities if a["status"] != "REFERENCED_NOT_REPOSITORY_RESIDENT"
    ]
    non_resident = [
        a for a in authorities if a["status"] == "REFERENCED_NOT_REPOSITORY_RESIDENT"
    ]

    unresolved = []
    for a in authorities:
        for candidate in expand_spec(a.get("source_path", "")):
            if not resolves(candidate):
                unresolved.append((a["authority_id"], candidate))

    citations = {
        c.split("::")[0].strip()
        for r in requirements
        for c in (r.get("evidence_paths") or [])
        if c.strip()
    }
    citations_resolving = {c for c in citations if (CANONICAL_ROOT / c).exists()}

    return {
        "authorities_total": len(authorities),
        "authorities_repository_resident": len(resident),
        "authorities_referenced_not_resident": len(non_resident),
        "authorities_non_resident_ids": [a["authority_id"] for a in non_resident],
        "authority_source_paths_unresolved": unresolved,
        "local_register_total": len(requirements),
        "local_register_statuses": dict(Counter(r["status"] for r in requirements)),
        "evidence_citations_distinct": len(citations),
        "evidence_citations_resolving_in_canonical": len(citations_resolving),
    }


def unmeasurable() -> dict:
    """The denominator this repository cannot produce, and why.

    CORRECTED 2026-09-04. This function previously said `499` derives from
    AUTH-01/02/03. It does not. That attribution was inherited from the
    authority table's framing rather than measured: AUTH-01/02/03 are the
    *PetCare* lineage, while `499` is computed in `MVC-ACCEPTANCE-ANNEX-001 V1.0`
    over the *MyVetiCare* lineage — `MVC-BRD-001` V3.1 + V3.2 and
    `MVC-SPEC-001` V3.1 Annex K — none of which the authority table lists.

    The residency status of AUTH-01/02/03 is unchanged and still NO. Only the
    attribution was wrong, and it mattered: it made `499` look unreachable in
    principle, when in fact its source is on this machine and its blockers are
    three named, closable conditions.

    A second computed figure exists and disagrees: V3.2 Appendix T reports 495
    distinct traced identifiers. The two exclude different things over different
    corpora, and the gap does NOT reconcile against the annex's four-identifier
    residue set. See AUTHORITY_CANDIDATES.md.

    Recorded rather than guessed. A denominator invented to make a ratio
    presentable is worse than an admitted gap.
    """
    return {
        "value": 499,
        "meaning": "product requirement estate, full platform",
        "status": "RELAYED_NOT_REMEASURED",
        "computed_in": "MVC-ACCEPTANCE-ANNEX-001 V1.0 section 6",
        "computed_over": [
            "MVC-BRD-001 V3.1 CANDIDATE (carries the requirement bodies)",
            "MVC-BRD-001 V3.2 (invariants, scope, fences; does NOT supersede V3.1)",
            "MVC-SPEC-001 V3.1 Annex K",
        ],
        "provenance": [
            "MVC-ACCEPTANCE-ANNEX-001 V1.0: REQUIREMENTS_TOTAL = 499 "
            "(500 less REQ-MVC-1, proven prose)",
            "MVC-CP2-PACK-001 V1.0: SPECIFICATION_CONTENT_COMPLETE = YES at 499",
            "Notion session handoffs of 31 Aug and 1 Sep 2026 relay it",
        ],
        "derivation_as_stated": "500 authored identifiers less REQ-MVC-1, which is prose",
        "competing_figure": {
            "value": 495,
            "computed_in": "MVC-BRD-001 V3.2 Appendix T",
            "definition": "distinct requirement identifiers traced into a V3.2 section",
            "excludes": "the metavariable REQ-MVC-n; INCLUDES REQ-MVC-1",
            "reconciliation": (
                "NOT RECONCILED. The gap is not explained by the annex's "
                "four-identifier residue set: REQ-MVC-1 is already excluded from "
                "499, so removing the other three gives 496, and on a common "
                "basis the figures are 500 and 495."
            ),
        },
        "why_not_measurable_here": (
            "no MyVetiCare BRD artefact is repository-resident, and none can be "
            "ingested yet. Nothing in the family is ratified; V3.2 does not "
            "supersede V3.1 so neither is complete alone; and V3.2's bytes no "
            "longer produce the hash its own governing record binds (recorded "
            "d480cb71, actual 32f53669). Two of six REV-8 hashes reproduce "
            "exactly, which validates the method and makes the rest drift."
        ),
        "what_would_measure_it": (
            "a Sponsor act ratifying MVC-BRD-001 V3.1 + V3.2 + Annex K as the "
            "requirement authority, ingestion of that companion set together, "
            "and a hash register re-issued against current bytes"
        ),
    }


if __name__ == "__main__":  # pragma: no cover
    import json

    print(json.dumps({"join": compute(), "unmeasurable": unmeasurable()}, indent=2))
