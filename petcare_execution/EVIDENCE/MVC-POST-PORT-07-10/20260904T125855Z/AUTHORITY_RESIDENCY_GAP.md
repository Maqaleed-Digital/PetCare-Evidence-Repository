# Authority residency gap — a citation is not the artefact

**Date:** 2026-09-04 · **Under:** `MVC-GOV-CANON-001`
**Contract:** `petcare_execution/AUTHORITY/AUTHORITY_INGESTION_SPEC.md`
**Asserted by:** `tests/governance/test_authority_residency.py` (13 cases)

## Measured state

```
AUTH_01_REPOSITORY_RESIDENT           = NO
AUTH_02_REPOSITORY_RESIDENT           = NO
AUTH_03_REPOSITORY_RESIDENT           = NO
DENOMINATOR_499                       = RELAYED_NOT_REMEASURED
DENOMINATOR_499_REPOSITORY_MEASURABLE = NO
AUTHORITY_INGESTION_PERFORMED         = NO
```

Searched exhaustively for `AUTH-01`, `AUTH-02`, `AUTH-03`, `REQ-MVC-1`, `499`,
`500 authored`, `PetCare BRD v1.1`, `AI-Native Technical Architecture` and
`Agentic AI Feature Layer` across the canonical repository. All three
authorities appear in exactly one place:

```
petcare_execution/PHASE_1_EXECUTION_PACK/PHASE1_SCOPE_GATES_ACCEPTANCE.md:5
    ## 1. Authoritative references used
    - PetCare BRD v1.1
    - PetCare AI-Native Technical Architecture v1.0
    - PetCare Vendor and SI Enablement Pack v1.0
```

Three bullet lines naming them. No rows, no version hash, no content.

## The trap

**Their `source_path` resolves.** It points at that same Phase-1 pack, which
exists and is healthy. A traceability check asking only "does the cited path
resolve?" returns a clean bill of health for all three — and these are
precedence **1, 2 and 3**, outranking every authority that *is* resident. The
hole is at the top of the table and a path check cannot see it.

The residency rule therefore names four things that look like residency and are
not, and AUTH-01 satisfies every one:

1. a document that names the authority in prose;
2. a `source_path` that resolves to a document citing it;
3. an entry in a reference list;
4. a row count quoted in a handoff or register.

**Counting references is not ingestion, and no amount of it produces 499.**

## Denominators that have each been called "the denominator"

| Figure | What it actually is | Status |
|---|---|---|
| **27** | story rows in `PHASE1_BACKLOG.csv` | a Phase-1 slice |
| **106** | `petcare-platform` Implementation-B register | **measured**; ~21% of the estate |
| **315** | files in the `petcare_execution` evidence manifest | not requirements at all |
| **499** | the product requirement estate | **relayed, and not measurable here** |

Only the last is the product denominator. Presenting `106` as it understates
scope roughly fourfold.

## What was built

`petcare_execution/AUTHORITY/AUTHORITY_INGESTION_SCHEMA.json` defines residency
structurally: a conforming `MANIFEST.json` plus the export it names, whose bytes
still produce `content_sha256`. Load-bearing fields:

- **`source_identity`** — enough to re-fetch the same object. Provenance that
  cannot be re-fetched is a claim, not a source.
- **`source_last_edited_utc`** kept separate from **`exported_utc`** — the gap
  between them is exactly how stale the copy is, and one field destroys that.
- **`original_ids_preserved: true`** and **`semantic_normalisation_applied: false`**
  — ingestion copies. A derivation presented as an authority is how a
  denominator quietly changes meaning.
- **`excluded_rows`** itemised by id. The stated derivation of 499 is "500
  authored less REQ-MVC-1, which is prose". Unless `REQ-MVC-1` appears there
  with that reason, the subtraction is unauditable.

The residency check is proven armed against a conforming fixture built in a
temporary directory, then broken five ways — drifted bytes, admitted
normalisation, renumbered ids, a dropped provenance field, a missing export —
each of which must read as non-resident.

## What was NOT done

No rows were invented. No authority directory was created with placeholder
content. `mvc_authorities.py` was not edited — it lives in the port source and
its statuses are currently accurate. `499` was not converted to measured.

Producing the export needs the authoritative source, which is outside this
repository. That is a **data-availability boundary, not a Sponsor gate**: no
credential, no production system and no external configuration is involved.
When the rows are exported, step 4 of the spec verifies them and step 5 permits
the status change — to whatever the export actually counts, which may not be 499.
