# Authority precedence table

**Date:** 2026-09-04 · **Under:** `MVC-GOV-CANON-001`
**Discovery:** `AUTHORITY_CANDIDATES.md` · **Contract:** `AUTHORITY_INGESTION_SPEC.md`

Precedence is decided from what the documents and their governing records say,
never from version number or filename. "V3.2 > V3.1" is the assumption this
table exists to refuse: V3.2 explicitly does **not** supersede V3.1.

| AUTHORITY_ID | DOCUMENT_ID | VERSION | DATE | STATUS | SUPERSEDES | SUPERSEDED_BY | GOVERNANCE_REFERENCE | CANONICAL_REFERENCE | DECISION |
|---|---|---|---|---|---|---|---|---|---|
| AUTH-01 | PetCare BRD | v1.1 | 2026-01-16 | `REFERENCED_NOT_REPOSITORY_RESIDENT` | PetCare brochure BRD | — | `mvc_authorities.py` precedence 1 | cited in `PHASE1_SCOPE_GATES_ACCEPTANCE.md` §1 | `UNRESOLVED_PRECEDENCE` |
| AUTH-02 | PetCare AI-Native Technical Architecture | v1.0 | — | `REFERENCED_NOT_REPOSITORY_RESIDENT` | — | — | `mvc_authorities.py` precedence 2 | cited in `PHASE1_SCOPE_GATES_ACCEPTANCE.md` §1 | `UNRESOLVED_PRECEDENCE` |
| AUTH-03 | PetCare Agentic AI Feature Layer BRD | — | 2026-03-15 | `REFERENCED_NOT_REPOSITORY_RESIDENT` | — | — | `mvc_authorities.py` precedence 3 | cited in `PHASE1_SCOPE_GATES_ACCEPTANCE.md` §1 | `UNRESOLVED_PRECEDENCE` |
| — | MVC-BRD-001 | V3.1 CANDIDATE | 2026-08-31 | `CANDIDATE` | V3.0 DRAFT | **not superseded by V3.2** | `MVC-RESUMPTION_RECORD.md` REV 8 | tower `10_Operational-Runtime-Towers/MyVetCare/` | `COMPANION` |
| — | MVC-BRD-001 | V3.2 | 2026-08-31 | `DRAFT — non-authorising` | — (incorporates V3.1 by reference) | — | `MVC-RESUMPTION_RECORD.md` REV 8 | same | `UNRESOLVED_PRECEDENCE` |
| — | MVC-SPEC-001 | V3.1 Annex K | 2026-08-31 | `CANDIDATE` | V3.0 for the split-taxpayer set | — | cited by the 499 denominator | same | `COMPANION` |
| — | MVC-SPEC-001 | V3.0 | 2026-08-31 | superseded for Annex K scope | V2.0 | V3.1 Annex K | — | same | `SUPERSEDED` |
| — | MVC-ACCEPTANCE-ANNEX-001 | V1.0 | 2026-08-31 | `DRAFT` | — | — | computes `REQUIREMENTS_TOTAL = 499` | same | `HISTORICAL` (derivation record, not a requirement source) |

## Why every live row is `UNRESOLVED_PRECEDENCE`

**Three independent reasons, any one of which is sufficient.**

**1. Nothing in the MyVetiCare family is ratified.**
`MVC-RESUMPTION_RECORD.md` line 149: *"All outputs are DRAFT pending Sponsor
verdict. Nothing is ratified."* V3.2 says the same of itself, and
`MVC-CP2-PACK-001` records `CP2_STATE = NOT_TAKEN`. There is no ratified BRD to
be current authority.

**2. V3.2 does not supersede V3.1, and neither is complete alone.**
V3.2 carries invariants, scope and fences; V3.1 carries the requirement bodies
and is a *normative annex*. The document says an engineer needs both. A
precedence model that picks one is wrong regardless of which it picks.

**3. V3.2's bytes do not match the hash its own governing record binds.**
Recorded `d480cb71…`, actual `32f53669…`. Two of the six REV-8 hashes reproduce
exactly, which validates the method and makes this drift rather than a
methodology difference. Ingesting bytes whose link to the recorded governance act
is broken would create custody, not record it.

**AUTH-01/02/03 are unresolved for a different reason:** they are not present at
all. They exist in this repository only as three bullet lines naming them, and no
artefact was located that can be *proven* to be the cited version — the PetCare
lineage files found (`PetCare_KSA_BRD_v1.1_Board_Ready.docx`,
`PetCare_Agentic_AI_BRD.docx`) match by title and version but carry no governance
record binding them to AUTH-01/AUTH-03. Title similarity is not identity.

## Consequences

```
AUTHORITY_PRECEDENCE                  = UNRESOLVED_PRECEDENCE
AUTHORITY_INGESTION_PERFORMED         = NO
AUTH01_REPOSITORY_RESIDENT            = NO
AUTH02_REPOSITORY_RESIDENT            = NO
AUTH03_REPOSITORY_RESIDENT            = NO
DENOMINATOR_499_STATUS                = RELAYED_NOT_REMEASURED
DENOMINATOR_499_REPOSITORY_MEASURABLE = NO
```

What **did** change is that the gap is now specific. Before this run, `499` was
believed to derive from AUTH-01/02/03 and was therefore unreachable in principle.
It does not: it derives from `MVC-ACCEPTANCE-ANNEX-001 V1.0` over the MyVetiCare
BRD family, which is **located on this machine**. The blocker moved from "the
source is unknown" to three named, closable conditions.

## What would close each row

| Condition | Closes |
|---|---|
| A Sponsor act ratifying `MVC-BRD-001` V3.1 + V3.2 + Annex K as the requirement authority | reason 1 |
| Ingesting the pair together, since neither is complete alone — the schema supports a companion set | reason 2 |
| Re-issuing REV 8's hash register against current bytes, or restoring the bytes that produce `d480cb71…` | reason 3 |
| A governance record binding `PetCare_KSA_BRD_v1.1_Board_Ready.docx` to AUTH-01 by hash | AUTH-01 |

Until then no ingestion is performed and `499` stays relayed. A denominator
adopted from an unratified draft whose bytes have drifted from their own record
would be worse than an admitted gap, because it would look measured.
