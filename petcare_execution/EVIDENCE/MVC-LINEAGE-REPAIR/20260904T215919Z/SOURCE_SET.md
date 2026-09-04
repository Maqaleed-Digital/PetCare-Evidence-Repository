# Declared source set — six documents, byte-verified into custody

**Authority for the set:** `MVC-CONTENT-COMPLETENESS-001 V1.0` §1 and §4
(six documents; three named directly by the defect list).

| Document | Version | Bytes | SHA-256 | Maqaleed blob | Ratified |
|---|---|---:|---|---|---|
| `MVC-BRD-001` | V3.1 CANDIDATE | 110,312 | `024501e639ba3b6d…` | `41999be430e8` | **NO** |
| `MVC-BRD-001` | V3.2 | 37,403 | `32f5366925128ca8…` | `5b2423c6a3f8` | **NO** |
| `MVC-CLOSE-001` | V1.1 | 21,325 | `27a07179d911e8ff…` | `b7d196078576` | **NO** |
| `MVC-SPEC-001` | V3.1 Annex K | 8,854 | `058356cc916f9a27…` | `bda8de25ff00` | **NO** |
| `MVC-SPEC-001` | V3.0 | 357,215 | `a3f2fb2c2a4eb709…` | `da48a7cb4d8a` | **NO** |
| `MVC-GAP-001` | V1.7 | 34,567 | `e8d221b4beb82708…` | `ba13a1fd8e14` | **NO** |

Every `repository_sha256` equals its `source_sha256`; the copies are byte-identical.
`ratified: false` on every entry — custody is not ingestion, and neither is ratification.

## Not in the set, and why it matters

`MVC-SPEC-001 V3.1` (full) does not exist — only its Annex K. V3.2 Appendix T
derives its identifier set from *"the SPEC V3.1 / GAP V1.7 namespaces"*, so a
named source of the universe is missing. `MVC-SPEC-001 V3.0` is included as the
only complete SPEC in custody, and the reconciliation reports the measurement
both with it (511) and without it (292).
