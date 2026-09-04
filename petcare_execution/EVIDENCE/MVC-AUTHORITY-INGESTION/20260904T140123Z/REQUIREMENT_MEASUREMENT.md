# Requirement measurement — attempted, and why it cannot complete

**Date:** 2026-09-04 · read-only observation of non-resident documents.
Nothing below is a repository measurement, and none of it changes the 499 status.

## Attempt

Parsed requirement identifiers directly from the corpus the 499 denominator
names — `MVC-BRD-001 V3.1 CANDIDATE` (.docx, unzipped `word/document.xml`,
tags stripped), `MVC-BRD-001 V3.2` (.md) and `MVC-SPEC-001 V3.1 Annex K` (.md).

Grammar discovered from the sources, not assumed:
`REQ-<NAMESPACE>[-<SUBNS>][.<n>[a-z]]` — namespaces observed are `REQ-MVC`,
`REQ-FIN`, `REQ-VET`, `REQ-UX`, `REQ-UX-NTI`, `REQ-SAF`, `REQ-SRC`, `REQ-INT`,
`REQ-REG`, `REQ-ABS`, `REQ-A`, `REQ-D`, `REQ-E`, `REQ-PRD12`.

```
V3.1 .docx    180,054 chars    253 distinct identifiers
V3.2 .md       37,007 chars    100 distinct identifiers
Annex K .md     8,744 chars     13 distinct identifiers
GAP V1.7 .md                    11 distinct identifiers

UNION_DISTINCT_LITERAL_IDENTIFIERS = 291
```

`REQ-MVC-1` is present. The metavariable `REQ-MVC-n` is present.

## 291 is NOT a third denominator

It is a **lower bound on literal string occurrences**, and it cannot be anything
else. Two reasons, both in the documents:

**1. The trace table elides its own members.** V3.2 Appendix T is the computation
that produces 495, and it does not enumerate the identifiers. Rows read:

```
| §5  | Surfaces  | REQ-MVC-4.1, REQ-MVC-4.10, … (+114) | 120 |
| §6  | Tenancy   | REQ-MVC-8.1, REQ-MVC-8.10, … (+124) | 130 |
```

Six names, then a count. **33 rows carry a `(+n)` elision.** The identifiers
behind them appear nowhere in the file.

**2. The set was generated, not written.** Appendix T states it is *"derived
mechanically from the BRD V3.1 S0–S10 part structure and the SPEC V3.1 / GAP
V1.7 namespaces. Not hand-assigned."* A generated range such as
`REQ-MVC-4.49 … 4.54` has no individual defining block — the acceptance annex
says exactly that of `REQ-MVC-4.49`. Members of a range are identifiers without
being strings in the text.

So a scan of the prose measures how many identifiers were *mentioned*, never how
many *exist*. Reporting 291 against 495 or 499 would be the "counting
references" error in a new costume.

## What this establishes

**Neither 495 nor 499 is reproducible from the artefacts located on this
machine.** The generator — the register or part-structure enumeration that
mechanically produced the identifier set — is not among them. Locating
`MVC-BRD-001` was necessary and is not sufficient.

```
MEASURED_AUTHORED_TOTAL               = NOT_MEASURABLE
MEASURED_REQUIREMENTS                 = NOT_MEASURABLE
LITERAL_IDENTIFIERS_OBSERVED          = 291   (lower bound, not a denominator)
ELIDED_TRACE_ROWS                     = 33
PREVIOUS_RELAYED_499                  = 499
MEASURED_vs_499                       = NOT_COMPARABLE
DENOMINATOR_499_STATUS                = RELAYED_NOT_REMEASURED
DENOMINATOR_499_REPOSITORY_MEASURABLE = NO
```

## REQ-MVC-1, investigated

The exclusion behind `500 → 499` is documented in `MVC-ACCEPTANCE-ANNEX-001`
V1.0 §A.3: `REQ-MVC-1` *"occurs only as the prose phrase 'REQ-MVC-1 precedent' —
a naming-convention reference. The family's real members are REQ-MVC-1.1…1.3."*
Disposition: **NOT A REQUIREMENT — excluded.**

The literal scan is consistent with that: `REQ-MVC-1` appears, and so do
`REQ-MVC-1.1`, `1.2`, `1.3`. It neither confirms nor refutes the "prose only"
finding, because a scan cannot distinguish a heading from a reference. **The
exclusion is not adopted here** — it is recorded as the annex's finding, which is
where it belongs until the annex is ratified.

Note also that V3.2's 495 **includes** `REQ-MVC-1` and excludes `REQ-MVC-n`
instead. The two documents disagree about which identifier is notation.

## Not attempted

No requirement rows were exported from Notion. Reading page text is not
exporting an authoritative row set, and the ingestion spec's `row_count`,
`content_sha256` and `excluded_rows` fields cannot be honestly populated from a
search result.
