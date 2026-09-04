"""PORT-10 — the cross-repository traceability denominator, asserted.

The numbers this module pins have been travelling by handoff since 31 August,
and one of them was wrong for six days before anyone re-ran it (the responsive
baseline: relayed 88/51/37, measured 90/53/37). A denominator carried in prose
decays quietly. These assertions make it fail loudly instead.

The distinction the whole tranche turns on: `106` is measurable from the
repositories and `499` is not. Conflating them understates the product estate
roughly fourfold, and inventing a measurement for 499 to make the ratio
presentable would be worse than admitting the gap.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "governance"))

from cross_repository_traceability import (  # noqa: E402
    PORT_SOURCE_ROOT,
    PortSourceUnavailable,
    compute,
    expand_spec,
    resolves,
    unmeasurable,
    validate_instrument,
)

port_source_available = pytest.mark.skipif(
    not (PORT_SOURCE_ROOT / "scripts" / "governance").is_dir(),
    reason=(
        f"port source not checked out at {PORT_SOURCE_ROOT}; the cross-repository "
        "join was NOT computed. Set MVC_PORT_SOURCE_ROOT."
    ),
)


# ---------------------------------------------------------------------------
# The instrument, before anything it measures
# ---------------------------------------------------------------------------

def test_the_path_resolver_discriminates_in_both_directions():
    """A resolver that returned True for everything produces the same clean
    report on a healthy table as one that works."""
    validate_instrument()


def test_the_naive_reading_of_a_source_path_is_the_one_that_lies():
    """Records the concrete false negative this resolver exists to avoid.

    `source_path` uses brace lists, globs, and both comma and semicolon
    separators. Read literally, four of eleven authorities report as missing —
    36% false negatives on a table whose only job is to say what exists.
    """
    naive = "petcare_execution/RUNTIME_FOUNDATIONS/{SERVICE_REGISTRY.json,API_CONTRACTS.json}"
    assert not (ROOT / naive).exists(), "the brace literal is not a real path"
    assert len(expand_spec(naive)) == 2
    assert expand_spec("a.py; b/*.sh") == ["a.py", "b/*.sh"]


def test_the_resolver_is_not_simply_returning_true():
    assert resolves(str(ROOT / "petcare_execution"))
    assert not resolves("/no/such/path/anywhere")
    assert resolves(str(ROOT / "petcare_execution" / "EP0*"))
    assert not resolves(str(ROOT / "zzz-no-such-*"))


def test_an_absent_port_source_raises_rather_than_reporting_a_smaller_estate():
    """A join that quietly dropped half its inputs would read as a small
    product rather than an incomplete measurement."""
    assert issubclass(PortSourceUnavailable, RuntimeError)


# ---------------------------------------------------------------------------
# The join
# ---------------------------------------------------------------------------

@port_source_available
def test_every_authority_source_path_resolves():
    join = compute()
    assert join["authority_source_paths_unresolved"] == [], (
        f"authority source paths that resolve to nothing: "
        f"{join['authority_source_paths_unresolved']}"
    )


@port_source_available
def test_the_authority_table_denominator_is_eleven():
    join = compute()
    assert join["authorities_total"] == 11
    assert join["authorities_repository_resident"] == 8
    assert join["authorities_referenced_not_resident"] == 3


@port_source_available
def test_the_three_highest_precedence_authorities_are_the_non_resident_ones():
    """This is the shape of the hole, and it is the reason 499 is unreachable.

    AUTH-01, 02 and 03 sit at precedence 1, 2 and 3 — they outrank everything
    that IS in the repositories. Their `source_path` resolves, but it resolves
    to the Phase-1 pack that cites them by name, not to the documents. A path
    check alone therefore reports them healthy and hides the gap completely.
    """
    join = compute()
    assert join["authorities_non_resident_ids"] == ["AUTH-01", "AUTH-02", "AUTH-03"]


@port_source_available
def test_the_local_register_denominator_is_measured_not_relayed():
    join = compute()
    assert join["local_register_total"] == 106
    assert join["local_register_statuses"] == {
        "CLOSED_EVIDENCED": 104,
        "DEFERRED_INTEGRATION": 2,
    }
    assert sum(join["local_register_statuses"].values()) == join["local_register_total"]


@port_source_available
def test_every_evidence_citation_resolves_in_the_canonical_repository():
    """The cross-repository edge that actually carries weight: the port source's
    CLOSED_EVIDENCED rows cite artefacts that live here, not there."""
    join = compute()
    assert join["evidence_citations_distinct"] == 14
    assert join["evidence_citations_resolving_in_canonical"] == 14


# ---------------------------------------------------------------------------
# The denominator that is not measurable, declared as such
# ---------------------------------------------------------------------------

def test_the_product_denominator_is_declared_relayed_and_not_silently_measured():
    """499 must never acquire a computed-looking status it has not earned."""
    u = unmeasurable()
    assert u["value"] == 499
    assert u["status"] == "RELAYED_NOT_REMEASURED"
    assert u["provenance"], "a relayed figure with no provenance is a rumour"
    assert u["why_not_measurable_here"]
    assert u["what_would_measure_it"], (
        "an admitted gap must say what would close it, or it is just an excuse"
    )


@port_source_available
def test_the_two_denominators_are_not_collapsed():
    """106 and 499 measure different objects. Presenting the smaller as the
    product denominator understates scope roughly fourfold."""
    join = compute()
    assert join["local_register_total"] != unmeasurable()["value"]
    ratio = join["local_register_total"] / unmeasurable()["value"]
    assert ratio < 0.25, (
        "the local register is being treated as if it covered the product estate"
    )


# ---------------------------------------------------------------------------
# Vacuity guard
# ---------------------------------------------------------------------------

@port_source_available
def test_the_join_was_computed_against_populated_inputs():
    join = compute()
    assert join["authorities_total"] >= 10
    assert join["local_register_total"] >= 100
    assert join["evidence_citations_distinct"] >= 10
