# Cross-repository traceability denominator

**PORT-10** · **Under:** `MVC-GOV-CANON-001` · **Measured:** 2026-09-04
**Re-derivable from:** `scripts/governance/cross_repository_traceability.py`
**Asserted by:** `tests/governance/test_cross_repository_traceability.py`

Two repositories describe one product and neither holds the whole picture.
`petcare-evidence-repository` is canonical and carries the evidence, the seals
and the runtime. `petcare-platform` is `LEGACY_TO_PORT_FROM` and carries the
requirement register and the authority precedence table. Every coverage claim is
a join across both, and a join is only as honest as its denominator.

## The finding

**`106` is measurable. `499` is not, and cannot be from these two repositories.**

That is not a bookkeeping distinction. Presenting `106` as the product
denominator understates scope roughly fourfold, and it is the exact confusion
the 1 September authority sync flagged as CONTRADICTION 1.

## What was measured this run

| Denominator | Value | Status |
|---|---|---|
| Authority precedence table | **11** | measured |
| — repository-resident | **8** | measured |
| — `REFERENCED_NOT_REPOSITORY_RESIDENT` | **3** (AUTH-01, 02, 03) | measured |
| Authority `source_path`s that resolve to nothing | **0 / 11** | measured |
| Local requirement register (Implementation-B) | **106** | measured |
| — `CLOSED_EVIDENCED` | **104** | measured |
| — `DEFERRED_INTEGRATION` | **2** | measured |
| Distinct evidence citations from the register | **14** | measured |
| — resolving in the canonical repository | **14 / 14** | measured |
| Evidence files under custody | **40** | measured |
| `petcare_execution` manifest | **315** | measured, 0 drift |
| Port plan | **10** | measured |

Test estate, every figure produced by **running** the suite:

| Suite | Cases |
|---|---|
| `tests/` (canonical, python) | **73** — of which **39** are governance |
| `petcare_runtime/tests` | **234** |
| `petcare_api/tests` | **46** |
| `petcare_web` vitest | **120** |
| `petcare_web` Playwright | **90** |

Playwright cases are loop-generated over viewports and routes: a static count of
`test(` declarations gives 6 where a run gives 90. Static source counts and
runtime case counts are different measures and must not be substituted for one
another.

## The hole, and its exact shape

`499` is the product requirement estate. Its provenance is the Notion handoff
chain — "Session Handoff — 31 Aug 2026" records `REQUIREMENTS_TOTAL = 499
(REQ-MVC-1 is prose)`, i.e. 500 authored rows less one prose row, and the 1
September handoff repeats it. It has carried `RELAYED_NOT_REMEASURED` ever since
and it still does.

It cannot be measured here because it derives from **AUTH-01 (PetCare BRD v1.1),
AUTH-02 (AI-Native Technical Architecture v1.0) and AUTH-03 (Agentic AI Feature
Layer BRD)** — precedence 1, 2 and 3, outranking everything that *is* in the
repositories, and all three marked `REFERENCED_NOT_REPOSITORY_RESIDENT`. No file
in either repository carries the 499 rows.

**The trap:** all three have a `source_path`, and it resolves. It resolves to
`PHASE1_SCOPE_GATES_ACCEPTANCE.md`, the Phase-1 pack that *cites* them by name.
A traceability check that only asked "does the source_path resolve?" would report
AUTH-01 healthy and hide the hole completely. `authorities_referenced_not_resident`
is asserted separately for that reason.

**What would close it:** ingest AUTH-01 into the canonical repository, or export
the Notion requirement rows to a versioned artefact and cite it. Until one of
those happens, `499` stays relayed, and it must keep saying so. A denominator
invented to make a ratio presentable is worse than an admitted gap.

## A note on the instrument

The first resolver written for this report said **7 of 11** authority source
paths resolved. The correct answer is **11 of 11**. The four "failures" were
brace lists (`{SERVICE_REGISTRY.json,API_CONTRACTS.json}`), globs (`PH-R*`), and
alternatives separated by a semicolon rather than a comma — a 36% false-negative
rate on a table whose only job is to say what exists, and every one of them
pointing at a healthy artefact.

The resolver is now validated in both directions before it is trusted: a
known-present path must resolve, a known-absent path must not, a glob must match
and must not over-match. A resolver that returned `True` for everything produces
exactly the same clean report on a healthy table as one that works.

## Standing rules this pins

1. `106` and `499` are different objects. Never collapse them; a test now fails
   if the ratio is treated as if the register covered the estate.
2. Any figure quoted from a handoff is `RELAYED` until a run reproduces it.
   Re-measure; do not re-quote.
3. A static source count is not a runtime case count.
4. An unmeasurable denominator is declared, with its provenance and with what
   would measure it — never estimated, never quietly dropped.
