# U30 · Correction record — R2 unscripted perturbations, and direct verification of GA-1 / U24 / U25, 2026-09-27

```
PROGRAMME=MVC-BUILD-RUNNER-001 v1.3   UNIT=U30   BASE_MAIN=b4a185947f4e6f686f3a858c5db4fd868cfe2efa (U29 merged, PR #77)
NATURE=NEW correction receipt. No original unit receipt, the v1.2 Phase R receipt, or any historical evidence is edited.
```

## PART A — the 19 reconstructed perturbations

```
ORIGINAL_SCRIPT_AT_ORIGINAL_MERGE=NOT_PRESENT
HISTORICAL_EXECUTION_FROM_SCRIPT=NOT_PROVEN
REBUILT_DATE=2026-09-26
CURRENT_SUBSTANTIVE_PERTURBATION_PROOF=PASS
```

These 19 perturbations were recorded as ARMED in their unit receipts in prose only; no executable script existed in
the repository (or in the runner's scratch corpus) at the original merge. On 2026-09-26 each was RECONSTRUCTED from the
receipt's description into a byte-exact mutation against the then-current code and executed (v1.2 Phase R). That
replay proves the reconstructed mutation is caught NOW. It does NOT retroactively prove that an identical executable
perturbation ran at the original merge. The historical attestation gap is preserved here as a record-quality finding:
FINDING R2-UNSCRIPTED-PERTURBATIONS (record quality) — unit receipts U1–U8 attested ARMED without a committed
executable perturbation; U14/U21 redesigns likewise. Remedy in force since 2026-09-26: every perturbation is committed
as an executable script (`evidence/replay/2026-09-26/`, `evidence/replay/2026-09-27/`).

| # | Original unit (PR, merged) | Criterion | Reconstructed id | Current result (main b4a1859) |
|---|---|---|---|---|
| 1 | U1 (#46, 2026-09-24T18:27Z) | AC-FR-02-04 | U1-P-ACTOR-HEADER | ARMED |
| 2 | U2 (#47, 2026-09-24T18:49Z) | AC-FR-02-01 | U2-P-AC01 | ARMED |
| 3 | U2 (#47) | AC-FR-02-02 | U2-P-AC02 | ARMED |
| 4 | U2 (#47) | AC-FR-02-03 | U2-P-AC03 | ARMED |
| 5 | U3 (#48, 2026-09-24T19:09Z) | AC-FR-09-01 | U3-P-AC01 | ARMED |
| 6 | U3 (#48) | AC-FR-09-02 | U3-P-AC02 | ARMED |
| 7 | U4 (#49, 2026-09-24T19:24Z) | AC-FR-01-01 | U4-P-ACTOR-HEADER | ARMED |
| 8 | U5 (#50, 2026-09-24T19:44Z) | AC-FR-01-02 | U5-P-ROLE-ALONE | ARMED |
| 9 | U6 (#51, 2026-09-24T20:01Z) | AC-FR-27-01 | U6-P-AC01 | ARMED |
| 10 | U6 (#51) | AC-FR-27-03 | U6-P-AC03 | ARMED |
| 11 | U6 (#51) | AC-FR-27-04 | U6-P-AC04 | ARMED |
| 12 | U7 (#52, 2026-09-24T21:42Z) | AC-FR-07-01 | U7-P-AC01 | ARMED |
| 13 | U7 (#52) | AC-FR-07-02 | U7-P-AC02 | ARMED |
| 14 | U8 (#53, 2026-09-25T11:26Z) | AC-FR-13-01 | U8-P-AC01-ISO | ARMED |
| 15 | U8 (#53) | AC-FR-13-01 | U8-P-AC01-UI | ARMED |
| 16 | U8 (#53) | AC-FR-13-02 | U8-P-AC02-TRIGGER | ARMED |
| 17 | U8 (#53) | AC-FR-13-02 | U8-P-AC02-AUDIT | ARMED |
| 18 | U14 (#59, 2026-09-25T13:20Z) | AC-FR-20-03 (internal exact-total rule; criterion EXTERNAL-gated) | U14-P-AC03-NO-CONFIRMATION-CHECK-ANYWHERE | ARMED |
| 19 | U21 (#66, 2026-09-25T15:11Z) | AC-FR-27-02 (internal part; criterion COUNSEL:L-2) | U21-P-AC02-NONVET-SUPPLY-BOTH-LAYERS | ARMED |

The same script also re-runs two U22 UI cases (U22-P-VIDEO-UI-NO-GATE / -NO-SCREEN) that duplicate the scripted U22
set; they are not among the 19 (both ARMED).

Corpus: `evidence/replay/2026-09-26/perturb_u1_u8_u14_u21_u22_reconstructed.py`
sha256 9454a0d3f109d6a70f4f0177dc10bb8b6c9de4d65534cc8c2743114606df780e (unchanged);
its 2026-09-26 output `replay_reconstructed.out.txt` sha256 388963d69f7e92dfb1556ef286e61bb651030f44f4a51d4c3fac2ffb3e4255be;
current output on main b4a1859 `evidence/replay/2026-09-27/replay_reconstructed_on_b4a1859.out.txt` sha256 33a2251a738f1f64a25cf5a0098c88b32966ff04f436c9d4e758874f6114f75a
(ARMED=21 VACUOUS=0).

## PART B — GA-1, U24, U25 verified directly (git, GitHub PR metadata, Actions runs, v1.2 ledger)

| Field | GA-1 Sponsor acts | U24 NFR-15 | U25 NFR-08 mechanism |
|---|---|---|---|
| PR | #69 `acts/sq1-sq2` | #70 `build/u24-nfr15-rate-limit` | #71 `build/u25-nfr08-mfa` |
| Head SHA | c56e79120476f924d72ebb632e75597cff469eb7 | 27274e6b7d3d273e1bd46cc76f31293f3309ce0f | a9d810d0d388c9e0fc0c3624c10ee8d3d6437d7c |
| Merge SHA | 591539d0e9c9cdba380fabbe2ed9a37955eca66a | 6e7479ed1f1c15f78ba18297d4c8dbb6d8e676d9 | c6b04505b5c7accc6d0266f6cc6343dfe37e8df9 |
| Merged at | 2026-09-26T16:30:21Z | 2026-09-26T16:49:05Z | 2026-09-26T17:08:59Z |
| CI (check `verify`) | SUCCESS | SUCCESS | SUCCESS |
| CI runs / attempts | 1 run (36255291379), attempt 1 | 1 run (36256387126), attempt 1 | 1 run (36257547025), attempt 1 |
| CI totals (from run log) | estate 1105 passed/7 skipped; PG 199 passed | estate 1110/7; PG 200 passed | estate 1115/7; PG 201 passed |
| Touched paths | governance/sponsor_acts/MVC-SQ1-…-001.md (A), governance/sponsor_acts/MVC-SQ2-…-001.md (A), evidence/receipts/2026-09-26-sponsor-acts-sq1-sq2.md (A) | 15 paths; receipts only ADDED (…-v1.2.md, …-u24-…md); no governance/, register, authority or pack path | 16 paths; receipts only ADDED (…-v1.2-s2.md, …-u25-…md); no governance/, register, authority or pack path |
| Merge rule | GA-1 in place of M3: exactly two new act files + one new receipt — PASS | M1 PASS · M2 PASS (perturbations re-run ARMED in v1.2 Phase R) · M3 PASS · M4 PASS (no FR regression; 2/16→2/16) · M5 PASS | M1 PASS · M2 PASS (idem) · M3 PASS · M4 PASS (2/16→2/16) · M5 PASS |
| Ledger entry | v1.2 ledger row "GA-1 acts (merge record) \| #69 \| c56e791… \| 591539d… \| 1" | v1.2-s2 row "#70 \| 27274e6… \| 6e7479e… \| 1 (PG 200 passed 0 skipped)" | v1.2-s3 row "#71 \| a9d810d… \| c6b0450… \| 1 (PG 201 passed 0 skipped)" |
| Agreement | AGREE (the ledger gives no PG total for GA-1; 199 recorded here from the run log) | AGREE | AGREE |

No material contradiction between Git/GitHub and the v1.2 ledger was found; no reconciliation receipt is needed.

## PART C — migrations
```
MIGRATIONS=59 (0054 added by U28)   REQUEST_002=STALE — NOT reissued in v1.3
REQUEST_002_REISSUE_TIMING=CODE_FREEZE_IMMEDIATELY_BEFORE_AUTHORIZED_PRODUCTION_ACT
No production migration / apply is authorized or performed.
```
