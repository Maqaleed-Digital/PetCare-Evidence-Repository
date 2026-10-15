# MVC-EPC-D-001 v1.5 — Lane D unit D2m: J-O8 cash-on-delivery path (full stack) — partial evidence, J-O8 UNCOUNTED (R20.1)

```
UNIT=D2m   AUTHORITY=R19.5(3), R20.1, R18.4   STACKED_ON=D2l (f2ffb72)
CODE_COMMIT=3715297ca4312ad7227bf88629d7e12884cb652b (WIP commit 70a6de0, rebased; git patch-id identical 0d304b0e…)
```

## What is built
- API (additive): `GET /api/catalog/prices` and every order line carry the registered product `name`
  (`InventoryRepository.name_of`, in-memory + PostgreSQL). POM/RESTRICTED/CONTROLLED stay unlisted and unorderable (FR-04/FR-20).
- `/owner/orders`: products by name; each order exposes `data-status`; order lines; machine values (product names, ids,
  collection reference, ISO date in the Arabic receipt) set `translate="no"`; owner home link `owner-open-orders`.
  Only cash on delivery is offered — online payment is BLOCKED on X-05 / HyperPay and is not simulated (R18.4).
- `tools/e2e_stack.py`: two synthetic registered products (GENERAL `e2e-shampoo`, POM `e2e-amoxicillin`); registration has
  no served route.
- `e2e-full/jo8-cod.spec.ts` **[J-O8-COD]**: owner opens the shop from home -> GENERAL offered, POM absent -> orders 2 with COD
  (only method) -> PLACED -> POM order via API refused 409 -> delivery from an UNLICENSED location refused 409
  ESTABLISHMENT_LICENCE_INVALID -> platform admin records the licence (R19.2 fields; `registry_verified=false`) -> delivery with
  exact cash collected -> owner sees DELIVERED + receipt in their language (lang/dir) -> receipt retrievable (3000 halalas).
  Arabic: no untranslated copy at three points.

## R20.1 — counting
Cash on delivery alone does not complete J-O8. The spec is tagged **[J-O8-COD]**, which report.mjs does not count; J-O8 stays
**PARTIAL, uncounted** until its online-payment path is proven against the real provider under X-05. The BRD journey definition is
unchanged. No screen is tagged: MS-06 requires HyperPay among other things; PH-02/PH-14/PH-16 (staff screens) are not built.

## Full-stack acceptance (R20 Phase 3: each project separately, one worker, no concurrent backend run)
| ORDER | PROJECT | RESULT | EVIDENCE |
|---|---|---|---|
| 1 | en-desktop | PASS (1 expected, 0 unexpected) | evidence/replay/2026-10-15-epc-d-d2m/jo8-cod-en-desktop.json |
| 2 | ar-desktop | run 1 FAIL (finding D2M-SIGNIN-REDIRECT-COLD-DEV, fixture sign-in redirect on cold `next dev`); run 2 PASS | failures/ar-desktop-run1/ ; jo8-cod-ar-desktop.json |
| 3 | en-mobile | PASS | jo8-cod-en-mobile.json |
| 4 | ar-mobile | PASS | jo8-cod-ar-mobile.json |

**D2M_E2E = 4/4 PASS.** Earlier attempts (before this series): one all-projects run failed 4/4 at the owner-home click (first-run
guide intercepted the click; fixed by `dismissFirstRun`, the J-O7 sequencing); one run was stopped by the host for low memory.

## Evidence
| Check | Result |
|---|---|
| backend, CI command (D2m head) | **1293 passed, 0 failed** |
| PostgreSQL control (product name) | 1 passed, 0 skipped |
| tsc · web vitest | clean · **45 files / 238 passed** (FR-20, FR-04, FR-15 pinned page tests unchanged and passing) |
| prohibited-literal / secret / evidence bundles | 0 / CLEAN / 32 bundles FAILED=0 |

## Incident D2M-TOOLING-LOG-IN-EVIDENCE (commit hygiene; Sponsor decision OPTION_1_AMEND_AND_UNTRACK, 2026-10-15)
| FIELD | VALUE |
|---|---|
| original path | `evidence/replay/2026-10-15-epc-d-d2m/.claude-flow/policy/state.json` (1590 bytes, 52 lines) |
| source | the claude-flow hook (`hooks_post-command`) wrote its policy/receipt state into the replay directory while the runner's shell working directory was that directory; staging the directory swept it in |
| original unpublished commit | `fb5422dd` (local only; never pushed — `git ls-remote` showed no lane-d/d2m ref) |
| secret scan | repository `scripts/governance/secret_scan.py` PATTERNS (6) applied to the file: **0 findings — CLEAN** (the scanner walks tracked files only, so its patterns were applied to the file directly; no values printed). Order: the untrack + amend (Sponsor answer "Amend, untrack only") ran before this scan; the scan was then run on the retained local copy |
| removal | that one path untracked (`--cached`), then `commit --amend --no-edit` on the unpublished commit; no recursive delete; no other file changed |
| amended commit | the commit carrying this receipt (D2m receipt commit); its diff against main holds 0 `.claude-flow` paths |
| evidence verification | `verify_evidence_bundles.py` BUNDLES=32 FAILED=0; no manifest referenced the file (git grep) |
| local copy | retained on disk, untracked |

Finding HYG-CLAUDE-FLOW-IGNORE (separate hygiene item, not fixed in D2m; `.gitignore` unchanged): the repository has no ignore rule
for `.claude-flow/`, and two such tooling logs are already TRACKED on main from earlier work
(`petcare_api/.claude-flow/policy/state.json`, `petcare_api/tests/.claude-flow/policy/state.json`).

## Intermittent finding D2M-SIGNIN-REDIRECT-COLD-DEV (classification: intermittent test/runtime)
ar-desktop attempt 1 FAILED: the owner's sign-in SUCCEEDED (signed-in header rendered) but the browser remained on `/signin` until
the fixture's 30 s URL wait expired. The trace was preserved (runner scratch, binary) and the page snapshot is committed
(`failures/ar-desktop-run1/`). The unchanged re-run PASSED. The original failure stays on record and is not reclassified; the four
passing per-project results stand under the existing acceptance criteria (every project passed).

## Counts
No ledger row closes. CP1 11/19 (as of the D2k merge), CP2 0/40; screens 11/107; journeys 9/53. J-O8 PARTIAL, uncounted (R20.1).
Finding D2M-RECEIPT-PRODUCT-ID: the frozen FR-20 receipt text names products by id, not name; recorded, not changed here.
