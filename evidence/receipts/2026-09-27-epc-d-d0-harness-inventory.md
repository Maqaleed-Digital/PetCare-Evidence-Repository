# MVC-EPC-D-001 v1.5 · Lane D · Phase V + unit D0 (E2E harness, design system, inventory), 2026-09-27

```
PROGRAMME=MVC-EXTERNAL-PRODUCTION-CLOSURE-001   LANE=D   INSTRUMENT=MVC-EPC-D-001 v1.5 (issued on paste, [SPONSOR])
BASELINE=c20ca93e723b33ee044831c54e1ccad8055804f2   BRANCH=lane-d/d0-e2e-harness
AUTHORITY: BRD governance/brd/PetCare KSA - BRD1.docx sha256 5450f7832260532aafd080fa54999a66e7af914f1f3452ed3cb3c64950c640dc (matches);
           SQ-3 sha256 16efd2330f4b04e15aaf7cc04684897b7bd958feeb88c23a4133794e22f585cc; MVC-PHARM-001
ACCEPTANCE_COUNTS=UNCHANGED (2/16, 42/68, 3/13) — this lane registers no acceptance evidence
```

## Phase V
- V1 repo Maqaleed-Digital/PetCare-Evidence-Repository; common dir …/petcare-evidence-repository/.git; worktree petcare-wt-build.
- V2 origin/main == BASELINE (PASS). V3 tree clean; no Lane D ledger existed → fresh start; no open PRs.
- V4 (fresh detached checkout of BASELINE): backend 1142 passed / 0 skipped; web 203 passed; tsc clean; checker output ==
  requirements/status.json; corpus 24 scripts → 193 ARMED, 3 VACUOUS (historic first attempts), 1 SUPERSEDED, 1 historical
  script stopping on anchor drift (perturb_u25.py) — all listed in the new evidence/replay/EXCLUSIONS.md.
- V5 INVENTORY
  - Canonical web app: `petcare_web` (the CI web job runs there). FINDING D-V5-TWO-WEB-APPS: `petcare-web` (6 pages) also exists
    and is not tested by CI; not used by this lane.
  - Web pages (23): / · /signin · /register · /privacy · /unauthorized · /onboarding · /onboarding/pharmacy · /owner ·
    /owner/pets · /owner/orders · /owner/deliveries · /owner/reminders · /owner/recalls · /owner/emergency · /account ·
    /account/security · /account/consultations · /account/consultations/video · /account/messages · /vet ·
    /vet/prescriptions · /pharmacy · /pharmacy/inventory · /admin. Catalogue: 107 screens → 0 PASS today.
  - Served API routes: 101 (requirements/served_routes.json).
  - Provider integration code: none as an adapter layer (sfda.py, licences.py, deliveries.py, video.py hold internal
    logic only). FINDING D-V5-NO-ADAPTER-LAYER → D6.
  - Deployment files: petcare_api/Dockerfile, petcare_web/Dockerfile, GCP cloudbuild*.yaml; no AWS IaC. FINDING
    D-V5-API-IMAGE-INCOMPLETE: petcare_api/Dockerfile copies only main.py and routers/ — the image would fail to import
    (mfa.py, persistence.py, … absent) → D7.
  - E2E tooling: Playwright with network-mocked specs only (e2e/). No full-stack harness → built in D0.
  - Design: two token sets in globals.css; Latin-only fonts (DM Sans / DM Serif). FINDING D-V5-NO-ARABIC-FACE → D0 G1.
  - Local: port 8080 is held by an unrelated Docker container on this workstation; the harness uses 8090 (API) / 3100 (web).

## Journey work list (V5 map: screen / API — exists, partial, missing)
| Journey | Screen | API | Journey | Screen | API |
|---|---|---|---|---|---|
| J-00 landing | partial (/) | n/a | J-P1 order queue, fulfil | partial | partial |
| J-O1 register, verify email, reset | partial (invite-only; no verify/reset) | partial | J-P2 COD reconciliation | missing | partial |
| J-O2 consent grant/revoke | partial (component) | missing | J-P3 inventory GENERAL/OTC | exists | exists |
| J-O3 profile + data export (#11) | partial | missing | J-P4 dashboard | exists | exists |
| J-O4 pets | partial | exists | J-P5 recalls + SFDA report file | partial | partial |
| J-O5 book / reschedule / cancel | missing | partial | J-P6 goods receipt, barcode | missing | partial |
| J-O6 attend (video, chat, files) | exists | exists | J-P7 expiry/low-stock, stock-take | missing | missing |
| J-O7 prescriptions, timeline, upload | missing | partial | J-C1 clinic profile, hours, licence | missing | missing |
| J-O8 order + HyperPay/COD | partial | partial (no payments) | J-C2 invite staff, roster | missing | missing |
| J-O9 delivery tracking | exists | exists (no logistics adapter) | J-C3 change roles (#5) | missing | missing |
| J-O10 reminders + notification centre | exists | exists (no SMS adapter) | J-C4 permissions, membership | missing | exists |
| J-O11 owner MFA | exists | exists | J-C5 assisted MFA reset | missing | exists |
| J-O12 pay consultation, invoice | missing | missing | J-C6 bulk export file (#10) | missing | partial |
| J-V1 onboarding, licence status | partial | partial (no licensing adapter) | J-C7 payout/bank (#12, #13) | missing | missing |
| J-V2 availability, queue | missing | missing | J-C8 services, price list | missing | partial |
| J-V3 workspace | partial | partial | J-A1 genesis | missing | partial |
| J-V4 sign notes (#3) | missing | exists | J-A2 tenant onboarding | missing | missing |
| J-V5 prescribe, dispense, POM supply | exists | exists | J-A3 users/roles, suspend | missing | missing |
| J-V6 verify uploaded Rx | partial | partial | J-A4 credentials, API keys (#14, #15) | missing | missing |
| J-V7 sign medical record (#4) | missing | missing | J-A5 audit viewer/export | partial | exists |
| J-V8 vet MFA | exists | exists | J-A6 configuration, switches | missing | missing |
| J-V9 in-clinic visit | missing | missing | J-A7 vet verification queue | missing | exists |
| J-M1…J-M6 marketplace | missing | missing (catalog prices only) | CHAINS clinic/pharmacy/market | missing | missing |

## D0 build
- `tools/e2e_stack.py`: fresh PostgreSQL database (CI service or throwaway local cluster), all 59 migrations from empty,
  labelled synthetic seed (tenant t-e2e-clinic; one user per role; a synthetic vet authority), serves main:app in
  `postgres` mode. Test-only literals; no provider, secret or deployed system reached.
- `petcare_web/playwright.full.config.ts` + `e2e-full/`: four projects (ar default / en × 1280 / 390 px); fixtures; the
  harness spec (sign-in through the real stack; server-held session read back; wrong password refused). The mocked
  suite in e2e/ is unchanged.
- `e2e-full/report.mjs` → `petcare_web/e2e/JOURNEYS.md` (53 frozen journeys) and `product/SCREENS.md` (catalogue
  `product/screens.catalogue.json`, 107 screens). PASS only when every tagged test passes in all four projects.
- CI: the `verify` job runs the full-stack suite against its PostgreSQL service and uploads the matrices.
- Design system (G1): `app/design-system.css` (tokens, logical properties → automatic RTL mirroring, 48 px targets,
  focus ring), `components/ui` (Page, Card, Button, Field, Notice, Loading/Empty/Error/Offline states, DataView,
  useOnline), Arabic face IBM Plex Sans Arabic via next/font.
- `evidence/replay/EXCLUSIONS.md` and `tools/corpus_replay.py` (D3: base/head classification diff + exclusion check).

## Perturbations — `evidence/replay/2026-09-27-epc-d/perturb_epc_d_d0.py`
P-HARNESS-SEED-CREDENTIAL-WRONG (full stack) · P-DATAVIEW-NO-EMPTY-STATE · P-FIELD-UNLABELLED · P-PAGE-LTR-IN-ARABIC →
ARMED=4 VACUOUS=0.

## Findings raised in D0
- D-FR05-TEST-LOCAL-DATE-VS-SERVER-UTC: `test_fr05_licence.py::test_a_veterinarian_cannot_register_without_licence_details`
  (frozen U10; registered evidence) builds "yesterday" from the LOCAL date while the server compares licence expiry with
  the UTC date (routers/auth.py:484). It fails only between 00:00 and 03:00 Asia/Riyadh; passes under TZ=UTC and in CI
  (UTC runner). Not modified by this lane (frozen unit); local Lane D suite runs use TZ=UTC.
- D-V5-AUTH-LOG-EMAIL: the auth log line `AUTH_EVENT auth.sign_in_failed {'email': …}` carries the email address (PII,
  not a secret/code/token). Recorded for the X6/G6 review in D5.

## Status at D0
Journeys 0/53 PASS · screens 0/107 PASS (matrices committed; regenerated by CI). Harness 8/8 (2 tests × 4 projects).
