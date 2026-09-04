# Denominator reconciliation — 495 → 500 → 499, and what reconstruction found

**Date:** 2026-09-05 · **Under:** `MVC-GOV-CANON-001` · **Ruling 1: repair, not ratification**
**Tool:** `petcare_execution/tools/mvc_inventory.py` · **Output:** `inventory.json`
**Controls:** `tests/governance/test_mvc_inventory.py` (20 cases)

## The governed chain, which does reconcile

`MVC-CONTENT-COMPLETENESS-001 V1.0` §1 is titled *"The corrected denominator — it
was NOT 495"*. It withdraws 495 and names three defects that produced it:

| Defect | Effect |
|---|---|
| two-segment identifier regex truncates three-segment ids | `REQ-UX-NTI-1/-2/-3` collapsed into one phantom `REQ-UX-NTI` |
| `MVC-CLOSE-001 V1.1` absent from the source set | `REQ-SAF-F2`, `REQ-SAF-F3` never counted |
| `MVC-BRD-001 V3.2` absent from the source set | `REQ-DISP-AUTH-FAILCLOSED` never counted |

```
PRIOR_REPORTED_UNIVERSE = 495   (defective)
CORRECTED_UNIVERSE      = 500
EXCLUDED  REQ-MVC-n            metavariable, not an identifier
EXCLUDED  REQ-UX-4-conformant  prose suffix, not an identifier
RETAINED  REQ-UX-4             appears standalone 15x — a real requirement
```

`MVC-ACCEPTANCE-ANNEX-001 V1.0` §6 then takes 500 less `REQ-MVC-1`, "proven
prose", to reach **499**.

**So 495, 500 and 499 were never in conflict.** 495 is a withdrawn defective
figure; 500 is its correction; 499 is 500 with one documented exclusion. The
earlier claim in this repository that "495 vs 499 is NOT RECONCILED" was wrong —
see C-20.

## What reconstruction measured

| Source set | Documents | Union |
|---|---|---:|
| **SET-A** (declared) | V3.1, V3.2, CLOSE V1.1, SPEC V3.1 Annex K, SPEC V3.0, GAP V1.7 | **511** |
| SET-B | as above, without SPEC V3.0 | 292 |
| historic | six `.txt` documents, never committed | 500 |

```
RAW_DISTINCT_TOKENS  = 516
PHANTOMS_REMOVED     = 3    REQ-FIN, REQ-MVC, REQ-UX  (namespace mentions)
EXCLUDED             = 2    REQ-MVC-n, REQ-UX-4-conformant
MEASURED_UNIVERSE    = 511
MEASURED_vs_500      = +11
MEASURED_vs_499      = +12  (REQ-MVC-1 retained — see below)
ELISIONS_DETECTED    = 33
```

**Nothing was tuned.** The parser was corrected twice during this run, both
times because inspection found a defect, never because the number was wrong:
`REQ-A.5`/`REQ-D.22`/`REQ-E.1`/`REQ-F.12`/`REQ-C.35` were truncating to
`REQ-A`…`REQ-F` (the historic D-A defect in a new place), and `REQ-FIN-*` style
namespace mentions were counting as requirements. Both fixes moved the number
*away* from 500 as often as toward it.

## Why 500 is not reproducible, precisely

**`MVC-SPEC-001 V3.1` does not exist as a document.** Only its Annex K does —
verified across the filesystem and the full git history of the portfolio repo.
V3.2 Appendix T states its set was *"derived mechanically from the BRD V3.1
S0–S10 part structure and the SPEC V3.1 / GAP V1.7 namespaces"*. One of the two
named namespace sources is missing, and SET-B shows what its absence costs: 292
against 511 when SPEC V3.0 stands in for the SPEC mass.

Two further inputs of the historic run are also absent:

- the **inventory JSON** that `mvc_content_completeness.py` consumes
  (`json.load(open(a.inventory))['union']`) — never committed, and no tool in
  custody builds it;
- the **six `.txt` conversions** the run scanned — never committed; the
  invocation was never recorded.

```
DENOMINATOR_STATUS = NOT_REPRODUCIBLE_MISSING_SOURCE
```

This is a stronger result than "not reproducible". The cause is named, it is a
single missing artefact, and recovering `MVC-SPEC-001 V3.1` would let the
reconstruction be re-run and compared against 500 directly.

## REQ-MVC-1 is left in, deliberately

The 500 → 499 step needs `REQ-MVC-1` to be prose. The evidence is real but not
unanimous:

- **For:** `MVC-ACCEPTANCE-ANNEX-001` §A.3 finds it occurs only as *"the
  REQ-MVC-1 precedent"*, a naming-convention reference; V3.1's text confirms
  that phrasing verbatim.
- **Against:** `MVC-BRD-001 V3.2` Appendix T lists `REQ-MVC-1` among §1's traced
  identifiers.

Two governed documents disagree. Excluding it here would bake one side of an
unresolved question into a measurement — and would move the figure toward the
historic one, which is the tuning this lane forbids. It stays in the union;
the subtraction is reported separately and remains a Sponsor question.

```
MEASURED_UNIVERSE                     = 511
MEASURED_LESS_REQ_MVC_1               = 510   (arithmetic only, not adopted)
DENOMINATOR_499_REPOSITORY_MEASURABLE = NO
```
