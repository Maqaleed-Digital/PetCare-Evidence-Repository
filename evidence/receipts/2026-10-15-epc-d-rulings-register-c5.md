# MVC-EPC-D-001 v1.5 — Lane D Sponsor rulings register, continuation 5 (custody, append-only by new file; R15.2)

```
CREATED=2026-10-15   BY=Lane D runner (R19 custody, after the D2g–D2j merges)   AUTHORITY=R15.2, R18.5
PREDECESSOR=evidence/receipts/2026-10-02-epc-d-rulings-register-c4.md sha256 0871d988c048b61e4f84ffd8c3303cd2707bffb1798a2cabc7af284638b6e792 (not modified)
INDEX=evidence/rulings/INDEX.md (every register file, chronological; continuity test tests/governance/test_rulings_register_continuity.py)
```

| IDENTIFIER | SOURCE | SHA256 | CUSTODY_STATUS |
|---|---|---|---|
| R19 (2026-10-04, Rulings at the D2g–D2j merge gate — R19.1–R19.5) | [SPONSOR] ruling issued 2026-10-04, relayed verbatim in the Sponsor's Lane D execution instruction of 2026-10-15 ("R19 ISSUED TEXT"); copied byte-for-byte as `evidence/receipts/2026-10-04-epc-d-rulings/R19.txt` (37 lines) | ea14365121039b4d0c6b168affd33592dc33e03b03b60a7b6c251d6f5b304a78 | CUSTODIED VERBATIM (as relayed) |

Finding R19-CUSTODY-SOURCE: the original 2026-10-04 Sponsor message is not reachable from the runner session; the custodied
bytes are the issued text as the Sponsor relayed it on 2026-10-15. If the original instrument differs, the Sponsor custodies it
by a new register file (this file is never edited).

Comparison with the prepared draft (Notion "Session Handoff — 3 Oct 2026 — Sponsor gate: R19 + D2g–D2j merge queue", §4, marked
"Prepared, NOT YET ISSUED"; draft text `evidence/receipts/2026-10-04-epc-d-rulings/R19-draft-notion.txt`, sha256
ac58b9ddcb2e48f3b374ae6daead062160138960535dade0df045145bf7d82e7). Whitespace-normalised word diff, draft -> issued:

| # | DRAFT | ISSUED | CLASS |
|---|---|---|---|
| 1 | `(issued by the Sponsor, 2026-10-02)` | `Issued by the Sponsor, 2026-10-04` (own line) | ISSUE DATE: 2026-10-02 -> 2026-10-04 |
| 2 | `R19.2 — Licence record completeness: the record` | `R19.2 — Licence record completeness. The record` | punctuation only |
| 3 | `R19.4 — Test-only step-up seeding: the per-run` | `R19.4 — Test-only step-up seeding. The per-run` | punctuation only |

Every other word is identical (line wrapping differs). No substantive change to R19.1–R19.5. The issue date of record is
2026-10-04.
