# Authority residency results

**Date:** 2026-09-04 · `tests/governance/test_authority_residency.py` — 14 passed.

```
AUTH01_REPOSITORY_RESIDENT = NO
AUTH02_REPOSITORY_RESIDENT = NO
AUTH03_REPOSITORY_RESIDENT = NO
AUTHORITY_INGESTION_PERFORMED = NO
AUTHORITY_PRECEDENCE = UNRESOLVED_PRECEDENCE
```

## The guard, proven in both directions

The rule under test is **a reference to AUTH-01 is not AUTH-01**. A check that
returned `False` for everything would report the same clean result, so residency
is driven against a conforming fixture built in a temporary directory and then
broken five ways.

| Condition | Residency |
|---|---|
| conforming manifest + export whose bytes match `content_sha256` | **YES** |
| export bytes drifted from the recorded hash | NO |
| `semantic_normalisation_applied: true` | NO |
| `original_ids_preserved: false` | NO |
| a required provenance field dropped (`source_identity`) | NO |
| the named export absent | NO |
| a document that merely **cites** the authority | NO |
| a directory name alone | NO |

`CITATION_ONLY` — `PHASE1_SCOPE_GATES_ACCEPTANCE.md` — exists, names all three
authorities, and is exactly what their `source_path` resolves to. Residency is
still NO for all three. That is the assertion the whole file exists for.

## Why no ingestion was performed

Not because the sources were not found. They were:
`MVC-BRD-001` V3.1 + V3.2 and `MVC-SPEC-001` V3.1 Annex K, in the Maqaleed tower.

Three blocking conditions, each independently sufficient — see
`AUTHORITY_PRECEDENCE_TABLE.md`:

1. nothing in the family is ratified (`CP2_STATE = NOT_TAKEN`);
2. V3.2 does not supersede V3.1, so neither is complete alone;
3. V3.2's bytes no longer produce the hash its own governing record binds
   (`d480cb71…` recorded, `32f53669…` actual), and 2 of 6 REV-8 hashes reproduce
   exactly — which validates the method and makes the rest drift.

## Correction carried by this run

The claim that 499 derives from AUTH-01/02/03 is **falsified**. It is computed in
`MVC-ACCEPTANCE-ANNEX-001 V1.0` over the MyVetiCare lineage; AUTH-01/02/03 are
the PetCare lineage. Residency status is unchanged; the attribution was wrong.
Two tests now guard the correction so it cannot drift back, and a third records
that the competing figure 495 is **not reconciled** with 499.
