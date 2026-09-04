# Authority candidate discovery

**Date:** 2026-09-04 · **Under:** `MVC-GOV-CANON-001` · **Read-only survey**
Searched `~/dev`, `~/Documents`, `~/Downloads`, `~/Desktop` and the Maqaleed tower
by filename and by Spotlight content match. No credential store, cloud-auth
folder or system directory was touched.

## The finding that reframes the question

**`AUTH-01/02/03` and `MVC-BRD-001` are different document families.** The
`petcare-platform` authority table names AUTH-01 *"PetCare BRD v1.1"*, AUTH-02
*"PetCare AI-Native Technical Architecture v1.0"*, AUTH-03 *"PetCare Agentic AI
Feature Layer BRD"* — the **PetCare** lineage. The `499` denominator does **not**
come from any of them.

It comes from **`MVC-ACCEPTANCE-ANNEX-001 V1.0`**, computed over
**`MVC-BRD-001 V3.1` + `V3.2` + `MVC-SPEC-001 V3.1 Annex K`** — the **MyVetiCare**
lineage, which the authority table does not list at all.

> This falsifies a claim made in this repository's own PORT-10 record on
> 2026-09-04: *"499 derives from AUTH-01/02/03, all
> REFERENCED_NOT_REPOSITORY_RESIDENT."* The residency status of AUTH-01/02/03 is
> still `NO` and still correct. The **attribution** was wrong: it was inherited
> from the authority table's framing rather than measured, and 499's real
> derivation was never in that table.

## Candidates

Hashes are SHA-256 prefixes over the bytes on disk on 2026-09-04.

| SHA-256 | Bytes | mtime (UTC) | File | Family | Version | Status on its face |
|---|---:|---|---|---|---|---|
| `32f53669…` | 37,403 | 2026-08-31T20:37Z | `MVC-BRD-001_V3_2_EXECUTION_BASELINE_CANDIDATE.md` | MyVetiCare | V3.2 | **DRAFT — non-authorising**, "Nothing in this document is ratified" |
| `024501e6…` | 110,312 | 2026-08-31T16:20Z | `MVC-BRD-001_V3_1_CANDIDATE_MyVetiCare_Master_BRD.docx` | MyVetiCare | V3.1 | **CANDIDATE**; normative annex to V3.2, carries the requirement bodies |
| `058356cc…` | 8,854 | 2026-08-31T16:20Z | `MVC-SPEC-001_V3_1_Annex_K_Split_Taxpayer_Requirements.md` | MyVetiCare | V3.1 Annex K | companion, cited in the 499 denominator |
| `a3f2fb2c…` | 357,215 | 2026-08-31T16:20Z | `MVC-SPEC-001_V3_0_…Tranches_1_to_3.docx` | MyVetiCare | V3.0 | superseded by V3.1 Annex K for the split-taxpayer set |
| `f9510e71…` | 10,814 | 2026-08-31T21:16Z | `MVC-ACCEPTANCE-ANNEX-001_V1_0.md` | MyVetiCare | V1.0 | **where 499 is computed** |
| `8c11c8b9…` | 14,931 | 2026-08-31T21:18Z | `MVC-CP2-PACK-001_V1_0_…Authorization.md` | MyVetiCare | V1.0 | asserts `SPECIFICATION_CONTENT_COMPLETE=YES` at 499; `CP2_STATE = NOT_TAKEN` |
| `c4880c79…` | 38,363 | 2026-01-16T12:40Z | `PetCare_KSA_BRD_v1.1_Board_Ready.docx` | **PetCare** | v1.1 | the likely AUTH-01 artefact, by title and version |
| `4255e199…` | 37,624 | 2026-03-15T01:10Z | `PetCare_Agentic_AI_BRD.docx` | **PetCare** | — | the likely AUTH-03 artefact, by title |

Duplicates of several of these exist under `~/Downloads` and
`~/Downloads/MyVetiCare_RedTeam_20260828/`. The tower copy is treated as the
locus of record because it is the path the governance documents cite.

## Two computed denominators, not one

| Figure | Where computed | Denominator definition | Excludes |
|---:|---|---|---|
| **499** | `MVC-ACCEPTANCE-ANNEX-001 V1.0` §6 | 500 authored identifiers less one | `REQ-MVC-1`, "proven prose" — it occurs only in the phrase *"the REQ-MVC-1 precedent"* |
| **495** | `MVC-BRD-001 V3.2` Appendix T §40 | distinct identifiers traced into a V3.2 section | the **metavariable** `REQ-MVC-n`, which is notation |

They exclude **different things** and are computed over **different corpora**
(the annex enumerates authored identifiers; V3.2 traces identifiers derived from
the V3.1 S0–S10 part structure plus the SPEC V3.1 / GAP V1.7 namespaces). V3.2's
495 **includes** `REQ-MVC-1`, which 499 excludes.

The gap is 4, and there is a tempting arithmetic coincidence: the annex's
residue set is exactly four identifiers — `REQ-MVC-1`, `REQ-MVC-4.49`,
`REQ-REG-2`, `REQ-SRC-3`. **It does not reconcile.** `REQ-MVC-1` is already
excluded from 499, so subtracting the remaining three gives 496, not 495; and on
a common basis (both including `REQ-MVC-1`) the figures are 500 and 495, a gap
of five. The difference is therefore **not explained** by the residue set, and no
explanation is asserted here.

## Nothing in this family is ratified

```
MVC-RESUMPTION_RECORD.md:149
    "All outputs are DRAFT pending Sponsor verdict. Nothing is ratified."

MVC-BRD-001 V3.2  — "DRAFT — non-authorising", "Nothing in this document is ratified",
                    "PHASE_A_EXECUTION_READY is CP-2, a Sponsor act, and is not taken here"
MVC-CP2-PACK-001  — "CP2_STATE = NOT_TAKEN"
```

V3.2 also **does not supersede** V3.1: it incorporates V3.1's requirement text by
reference and governs only on conflict. V3.1 is a normative annex, not a
discarded predecessor. Neither alone is the authority; neither is ratified.

## The custody defect that settles ingestion

`MVC-RESUMPTION_RECORD.md` REV 8 records SHA-256 hashes for its six artefacts.
Checked against the bytes on disk:

```
MATCH     MVC-IMPLEMENTATION-BASELINE-001 V1.0
MATCH     MVC-EXEC-001 V1.0
MISMATCH  MVC-BRD-001 V3.2        recorded d480cb71…  actual 32f53669…
MISMATCH  MVC-BUILD-GAP-001 V1.0  recorded e05d19a9…  actual 1cd7ccf7…
MISMATCH  MVC-EXEC-BACKLOG-001    recorded df3cb3d7…  actual c537f615…
MISMATCH  MVC-RT-003 V1.0         recorded 1546d5f7…  actual adeb6425…

MATCH=2  MISMATCH=4
```

**The two matches validate the instrument.** Plain SHA-256 over the file bytes is
the right method and it reproduces two of the six recorded values exactly, so the
other four are drift, not a methodology difference.

`MVC-BRD-001 V3.2` is among the four. Its bytes no longer produce the hash its
own governing record binds it to, so ingesting it would bind a fresh hash to
bytes whose relationship to the recorded governance act is unestablished — the
opposite of custody. **This, rather than its draft status, is the decisive
reason no ingestion was performed.**

## Not searched

`~/Documents` returned no MyVetiCare BRD or SPEC artefacts. Notion was not
queried for rows in this pass: the export is the Sponsor-side act the ingestion
spec describes, and reading page text is not the same as exporting the
authoritative row set.
