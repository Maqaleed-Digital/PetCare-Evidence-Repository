# MVC-EPC-D-001 — TOTP read-only safety check before the D2g merge

DATE=2026-10-04
CHECK=TOTP_READ_ONLY_SAFETY_CHECK
PROCEDURE_SOURCE=HANDOFF_SECTION_5A (Notion "Session Handoff — 3 Oct 2026 — Sponsor gate: R19 + D2g–D2j merge queue", §5a, run verbatim)
AUTHORITY=[SPONSOR] disposition of 2026-10-04, step 3 (seal before adjudicate)
BASE=c0d34fa7185f46e0d8b52960be841c4f40eeeca3 (origin/main, D2f merge)
CANDIDATE=c75fe47045bb3a9dae978cbb8bd0acda23168fc2 (D2g)
MUTATION_PERFORMED=NO

## Sealed raw output

RAW_OUTPUT_PATH=evidence/receipts/2026-10-04-epc-d-totp-readonly-check.raw.txt
RAW_OUTPUT_SHA256=d922be2171827cd5ed0574332f34f3c5c2b061c1425db2dd45fc3fac90964210

The raw file holds the two §5a commands and their full output, written and hashed before the comparison below was made.
It also holds two supplementary attribution commands (per-file counts of changed lines, and the files owning unchanged
context lines); these are not part of §5a and are labelled as supplementary in the raw file.

## Observed

Changed paths matching `e2e|seed|totp|harness|fixture` (§5a command 1):

- petcare_api/tests/pg_harness.py
- petcare_web/e2e-full/jo7-prescriptions.spec.ts
- petcare_web/e2e-full/screen-routes.json
- petcare_web/e2e/JOURNEYS.md
- tools/e2e_stack.py

Diff lines matching `totp|otp_secret|step.?up` outside `evidence/` (§5a command 2): 14 lines.

| FILE | CHANGED (+/-) HITS | CONTEXT-ONLY HITS |
|---|---|---|
| petcare_web/e2e-full/jo7-prescriptions.spec.ts | 7 | 0 |
| tools/e2e_stack.py | 4 | 0 |
| petcare_web/app/pharmacy/page.tsx | 0 | 1 |
| petcare_web/app/vet/prescriptions/page.tsx | 0 | 1 |
| petcare_web/components/account/AccountCenter.tsx | 0 | 1 |

The three context-only hits are the unchanged line `import { useStepUp } from '@/components/StepUp'`, which D2g neither
adds nor removes; they appear because the §5a grep also matches diff context lines.

## Comparison against the Phase-0 report (2026-10-03)

| ITEM | PHASE-0 REPORT | OBSERVED 2026-10-04 | MATCH |
|---|---|---|---|
| petcare_web/e2e-full/jo7-prescriptions.spec.ts | 7 | 7 | YES |
| tools/e2e_stack.py | 4 | 4 | YES |
| application-source changed hits | 0 | 0 | YES |

RESULT=PASS
TOTP_READ_ONLY_CHECK=PASS_SEALED

Scope of this result: it is the §5a merge-gate check only (D2g introduces TOTP seeding solely in the e2e journey spec and
the e2e stack tool). It is not the standing test required by R19.4, which remains to be built in the next lane.
