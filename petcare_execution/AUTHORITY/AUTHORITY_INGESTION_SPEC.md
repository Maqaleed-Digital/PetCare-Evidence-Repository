# Authority ingestion specification

**Under:** `MVC-GOV-CANON-001` · **Opened:** 2026-09-04
**Schema:** `AUTHORITY_INGESTION_SCHEMA.json`
**Asserted by:** `tests/governance/test_authority_residency.py`

## The gap this exists to close

`499` is the product requirement denominator. It has carried
`RELAYED_NOT_REMEASURED` since 31 August and it still does, because it cannot be
measured from either repository. It derives from three authorities:

| ID | Document | Precedence | Status |
|---|---|---|---|
| AUTH-01 | PetCare BRD v1.1 | 1 | `REFERENCED_NOT_REPOSITORY_RESIDENT` |
| AUTH-02 | PetCare AI-Native Technical Architecture v1.0 | 2 | `REFERENCED_NOT_REPOSITORY_RESIDENT` |
| AUTH-03 | PetCare Agentic AI Feature Layer BRD | 3 | `REFERENCED_NOT_REPOSITORY_RESIDENT` |

They outrank every authority that *is* resident. Searched exhaustively, all
three appear in this repository in exactly one place: three bullet lines under
"1. Authoritative references used" in
`petcare_execution/PHASE_1_EXECUTION_PACK/PHASE1_SCOPE_GATES_ACCEPTANCE.md`
(lines 7–9). That is a list of names. It carries no rows, no version hash and no
content.

```
AUTH_01_REPOSITORY_RESIDENT           = NO
AUTH_02_REPOSITORY_RESIDENT           = NO
AUTH_03_REPOSITORY_RESIDENT           = NO
DENOMINATOR_499                       = RELAYED_NOT_REMEASURED
DENOMINATOR_499_REPOSITORY_MEASURABLE = NO
```

## The trap, stated plainly

**Their `source_path` resolves.** It points at `PHASE1_SCOPE_GATES_ACCEPTANCE.md`,
which exists. A traceability check that asked only "does the cited path resolve?"
returns a clean bill of health for all three and reports the hole as closed.

The check must ask a different question: *is the authority itself here?* A
document that cites an authority is evidence that the authority exists
somewhere. It is not the authority. The residency rule in the schema lists four
things that look like residency and are not, and AUTH-01 satisfies every one of
them.

**Counting references is not ingestion, and no amount of it will produce 499.**

## Neighbouring figures that must not be mistaken for the estate

| Figure | What it actually is |
|---|---|
| **106** | `petcare-platform` Implementation-B register. Measured. ~21% of the product estate. |
| **27** | Story rows in `PHASE1_BACKLOG.csv`. A Phase-1 slice, smaller again. |
| **315** | Files in the `petcare_execution` evidence manifest. Not requirements at all. |
| **499** | The product estate. Not resident, not measurable here. |

Each has been used as "the denominator" at some point. Only the last one is it.

## What ingestion requires

An authority becomes `REPOSITORY_RESIDENT` when
`petcare_execution/AUTHORITY/<authority_id>/` exists containing a conforming
`MANIFEST.json` and the export file it names, and the export file's SHA-256
equals the manifest's `content_sha256`. Field definitions are in the schema; the
load-bearing ones:

- **`source_identity`** must be enough to re-fetch the same object. Provenance
  that cannot be re-fetched is a claim, not a source.
- **`source_last_edited_utc`** is the *source's* timestamp, kept separate from
  `exported_utc`. The gap between them is exactly how stale the copy is, and
  collapsing them into one field destroys that.
- **`original_ids_preserved`** must be `true` and **`semantic_normalisation_applied`**
  must be `false`. Ingestion copies. Renumbering, merging, splitting or
  reconciling produces a derivation, and a derivation presented as an authority
  is how a denominator quietly changes meaning.
- **`excluded_rows`** must carry the exclusion by id. The stated derivation of
  499 is "500 authored less REQ-MVC-1, which is prose". Unless `REQ-MVC-1`
  appears in `excluded_rows` with that reason, the arithmetic is unauditable and
  `499` remains a number someone remembers.

## Procedure

1. Export the authoritative rows from their source. For AUTH-01 the source is
   the Notion requirement estate; the handoff chain (31 Aug, 1 Sep) is where
   `499` is stated, not where it is defined.
2. Write the export byte-for-byte to
   `petcare_execution/AUTHORITY/AUTH-01/<export_filename>`. No reformatting.
3. Write `MANIFEST.json` per the schema, including `excluded_rows`.
4. Run `pytest tests/governance/test_authority_residency.py`. It fails closed:
   a missing directory, a hash mismatch, a normalised export or an unexplained
   exclusion each keep the authority non-resident.
5. Only then may `mvc_authorities.py` move AUTH-01 off
   `REFERENCED_NOT_REPOSITORY_RESIDENT`, and only then may `499` move off
   `RELAYED_NOT_REMEASURED` — to whatever the export actually counts, which may
   not be 499.

## What this run did not do

No authority was ingested. No rows were invented. `499` was not converted to
measured, and `mvc_authorities.py` was not edited — it lives in the port source
and its statuses are currently accurate.

The export itself needs the authoritative source, which is outside this
repository. That is a data-availability boundary, not a Sponsor gate: no
credential, no production system and no external configuration is involved in
producing it.
