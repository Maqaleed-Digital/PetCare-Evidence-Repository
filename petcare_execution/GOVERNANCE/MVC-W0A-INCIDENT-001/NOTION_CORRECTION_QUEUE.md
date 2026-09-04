# Notion / register correction queue — PREPARED, NOT APPLIED

No Notion page was mutated. Each item names the target field, the current value, the
corrected value, and the primary evidence. Nothing is backdated.

## C-1 — `VULNERABLE_IMAGE_EXECUTED` must revert YES → UNKNOWN  *(new, highest priority)*

- **Current:** `NOTION_AUTHORITY_SYNC.md` CONTRADICTION 2 and the Sponsor's working
  model both carry `VULNERABLE_IMAGE_EXECUTED = YES (evidenced)`.
- **Corrected:** `UNKNOWN`.
- **Evidence:** `petcare_api/routers/auth.py` was **created** at `5202bb5f` on
  2026-05-23 (+164 lines, new file). The cited PH5.1 deployment is 2026-04-06 — seven
  weeks earlier. The deployed image cannot have contained code that did not exist.
- **Consequence:** CP-2 exclusion 2 is *further* from firing than previously recorded,
  not closer. It requires `EXECUTED=YES` **and** `PUBLICLY_REACHABLE=YES`; the first
  has now weakened from YES to UNKNOWN.

## C-2 — public source exposure is CURRENT, not merely historical  *(new)*

- **Current:** treated as "the secret was potentially derivable from public history".
- **Corrected:** the retired literal is present in `origin/main` of the **public**
  `Maqaleed-Digital/PetCare-Evidence-Repository` **right now**. `git show
  origin/main:petcare_api/routers/auth.py` → 1 occurrence. The W0-A fix exists only on
  the local canonical branch and has never been pushed.
- **Exposure:** opened 2026-05-23T22:22:51Z, **still open**, 103 days.

## C-3 — `petcare-web-prod` is decommissioned  *(new)*

- **Current:** PH5.1 records it PRODUCTION_ACTIVE.
- **Corrected:** the service no longer exists — returns the byte-identical 404 of three
  invented control hostnames (`6b43b396…`, 272 bytes).

## C-4 — product denominator 499, not 106

- 499 = programme requirement estate; 106 = Implementation-B local register. Carried
  forward from `NOTION_AUTHORITY_SYNC.md`; still `RELAYED`, not independently measured.

## C-5 — PF-33 `PUSH=NOT_CONFIGURED_ZERO_REMOTES` is stale

- Both repositories have configured origins; `gh` confirms both exist. Git wins on
  implementation reality. Which is the *authorised* custody destination remains a
  Sponsor designation.

## C-6 — W0-F is not agent work

- Standing instruction: prepare `MVC-W0F-ENGINEERING-HANDOFF-001`; do not implement
  the serving-layer replacement in an agent lane.

---

# Additions from the source-fix + product-advance run (2026-09-04)

## C-7 — the responsive baseline was 90/53/37, not 88/51/37  *(measured)*

- **Stale fact:** `PLAYWRIGHT_TOTAL=88 PASS=51 FAIL=37`, carried as relayed.
- **Current fact:** **90 / 53 / 37**, measured by running the suite.
- **Primary evidence:** `MVC-RESPONSIVE-CLOSURE/…/playwright_baseline_raw.txt`.
- **Correction type:** MEASUREMENT. The fail count was exact; total and pass were
  each understated by 2. Cases are loop-generated, so a static count of `test(`
  declarations gives 6 and only a run gives 90.
- **BACKDATE=NO**

## C-8 — responsive failures are closed  *(measured)*

- **Current fact:** **90/90 pass, 0 fail.** One CSS change,
  `ASSERTIONS_WEAKENED=0`, no e2e spec diff.
- **Root cause:** one shared non-wrapping nav needing 407px, clipped by a blanket
  `overflow-x: hidden` — the items were unreachable, not absent.
- **BACKDATE=NO**

## C-9 — `.env.local` was not gitignored in a PUBLIC repository  *(new defect, fixed)*

- **Stale fact:** env coverage assumed adequate.
- **Current fact:** only bare `.env` was ignored. `.env.local`, `.env.production`
  and every `.env.*.local` were **not** — including the exact filename Next.js
  instructs developers to put local secrets in.
- **Status:** FIXED this run. Nothing had been committed, so it was preventive.
- **CORRECTION_TYPE:** SECURITY_HYGIENE. **BACKDATE=NO**

## C-10 — W0-A source fix is published as PR, not merged

- **Current fact:** PR **#3** open against `main`, branch
  `security/w0a-require-session-signing-key`, one commit, 18/18 tests green on
  the branch. `main` still carries the insecure default until it is merged.
- **GATE:** Sponsor merge. **BACKDATE=NO**

## C-11 — port progress is 6 of 10, not 4

- **Current fact:** PORT-01, 02, 03, 04, 05, 06 complete. Remaining:
  PORT-07, 08, 09, 10.
- **BACKDATE=NO**

## C-12 — W0-F handoff exists

- **Current fact:** `MVC-W0F-ENGINEERING-HANDOFF-001` written.
  `W0_F_AGENT_IMPLEMENTATION=NO`, `W0_F_ENGINEERING_HANDOFF=READY`.
- **BACKDATE=NO**

## Residuals recorded, not closed

| ID | Note |
|---|---|
| `BLANKET_OVERFLOW_X_HIDDEN_RESIDUAL` | `globals.css:275` — now load-bearing on nothing; removal has its own regression surface |
| `PASSWORD_HASH_UNSALTED_SHA256` | `petcare_api` `_hash_password` is bare SHA-256, no KDF — routed to W0-F as a credential migration |
| `NEXT_LINT_NOT_CONFIGURED` | `next lint` drops into interactive ESLint setup; no lint result is claimed either way |
| `WEB_TREE_DUPLICATION_OPEN` | `petcare_web/` vs `petcare-web/` relationship still unestablished |

---

# Additions from the PORT-07..10 continuation run (2026-09-04, later)

## C-13 — C-10 is superseded: PR #3 is MERGED  *(measured)*

- **Stale fact:** C-10 above records PR **#3** as OPEN, awaiting Sponsor merge.
- **Current fact:** **MERGED** at `2026-09-04T11:00:51Z`, merge commit
  `204bd4cc23cc550f73e687a9f7340a688e26d0aa`, which is now `origin/main`.
  Read via `gh pr view 3 --json state,mergedAt,mergeCommit`.
- C-10 is preserved above rather than edited; it was true when written.
- **CORRECTION_TYPE:** MEASUREMENT. **BACKDATE=NO**

## C-14 — the live half of the public exposure is CLOSED; the history half is not

- **C-2 above** records the retired literal present in `origin/main` of the public
  repository. That is **no longer true of the tip**: `origin/main` now refuses to
  start on the retired literal rather than defaulting to it.
- Measured per-ref with a precise instrument (module-level
  `SECRET_KEY = os.getenv("SECRET_KEY", ...)`, not a substring search): `origin/main`
  and `origin/security/w0a-…` carry the fix; **four published branches still carry
  the active default at their tips** — `origin/gate-evidence-prep`,
  `origin/m8-brand-cleanup`, `origin/mvc-ux-wo-001`,
  `origin/mvc-ux-wo-002-trust-surfaces`.
- **The literal remains in published history** (`5202bb5f` onward). Git history is
  the exposure channel and it is unaffected by any branch tip.
- **GOTCHA, recorded because it produced a wrong reading first:** a substring grep
  for `os.getenv("SECRET_KEY", "` matches the **docstring** on the fixed file, which
  quotes the old expression. Every ref then reads as vulnerable. Five occurrences of
  the literal survive on the fixed tree and all five are a docstring, a rejection
  guard, or a test constant.
- **BACKDATE=NO**

## C-15 — GCP is not an infrastructure lane  *(supersedes the "GCP Read Pending" label)*

- **Old continuation label:** `GCP Read Pending`.
- **Corrected:** *Legacy-GCP reachability check (unauthenticated only); IAM read
  parked behind PATHFINDER-002.*
- Disposition record: `GCP_LANE_DISPOSITION.md`. `GCP_FORENSIC_READ_CARD.md` and
  `PRODUCTION_REMEDIATION_PLAN.md` are reclassified **PARKED**, not falsified.
- No `AMEND_MVC-GCP-FORENSIC-READ-001` execution item exists or is scheduled. No
  current GCP key-rotation workstream exists.
- **BACKDATE=NO**

## C-16 — the authority seal contradicted its own closure record  *(new defect, fixed)*

- **Stale fact:** `CANONICAL_REPOSITORY_AUTHORITY_SEAL.json` listed
  `GATE_EVIDENCE_UNVERSIONED` as `GOVERNANCE_EXCEPTION_OPEN` while
  `GATE_EVIDENCE_UNVERSIONED_CLOSURE.md` sat in the same directory, written the
  day before.
- Same class in the port plan's own exception table: `WEB_TREE_DUPLICATION_OPEN`
  (closed by `WEB_TREE_AUTHORITY_RECONCILIATION.md`) and `CANONICAL_HEAD_LOCAL_ONLY`
  (now partially closed — W0-A reached `origin/main`).
- **Status:** FIXED. Rows preserved, statuses changed; the exception list is
  append-only and a PORT-07 test now fails if the contradiction recurs.
- **CORRECTION_TYPE:** REGISTER_INTEGRITY. **BACKDATE=NO**

## C-17 — `/vet` presented three fabricated case rows  *(new defect, fixed)*

- **Current fact:** the consultation queue rendered rows labelled "Waiting",
  "Draft" and "Pending" against an em-dash patient, each with an Open /
  Review & sign / Authorize action. There is no case source in the pilot.
- On a clinical surface this is not cosmetic: "Prescription — Pending —
  Authorize" reads as a prescription waiting on a veterinarian.
- **Status:** FIXED. Explicit empty state plus a WI-5 disclosure that the queue is
  scaffolded, not merely quiet. Capabilities are still described, as capabilities.
- **CORRECTION_TYPE:** HONEST_DISCLOSURE. **BACKDATE=NO**

## C-18 — C-4 refined: 106 is now measured, 499 remains relayed

- **106** is **measured** this run: `len(REQUIREMENTS) == 106`, statuses
  `104 CLOSED_EVIDENCED + 2 DEFERRED_INTEGRATION`.
- **499** stays `RELAYED_NOT_REMEASURED`, and **cannot** be measured from either
  repository: it derives from AUTH-01/02/03, all `REFERENCED_NOT_REPOSITORY_RESIDENT`.
  Their `source_path` *resolves* — to the Phase-1 pack that cites them by name — so a
  path check alone reports them healthy and hides the hole.
- Record: `CROSS_REPOSITORY_TRACEABILITY.md`. **BACKDATE=NO**

## C-19 — the responsive figure is re-confirmed, not re-quoted

- **90 / 90 pass, 0 fail**, reproduced by running Playwright three times in this run
  (baseline, after PORT-08, after PORT-09). C-8 stands, now on a second measurement.
- **BACKDATE=NO**

## Residuals added, recorded not closed

| ID | Note |
|---|---|
| `PUBLIC_HISTORY_RETIRED_LITERAL` | The literal is in published history from `5202bb5f`. Removing it is `HISTORY_PURGE_PLAN`, `GATE_CLASS=GATE-5_IRREVERSIBLE_ACTION`, `STATUS=NOT_AUTHORIZED_BY_THIS_RUN`. |
| `PUBLISHED_BRANCH_TIPS_CARRY_DEFAULT` | Four published branches still carry the active default at their tips. Rebasing or retiring them is a separate decision; it does not reduce the history exposure. |
| `ADMIN_ATTESTATION_UNCOMPUTED` | `/admin` renders `CONTROLLED_PRODUCTION_ACTIVE`, `Audit chain: Live` and `Fail-closed: Active` as static text. These are governance claims the client cannot compute — the W0-E family. Not changed here; routed to W0-F. |
| `ADMIN_INERT_CTAS_UNDISCLOSED` | `/admin` CTAs are `href="#"` with no WI-5 disclosure, unlike `/owner`. Same class as C-17, lower severity, not a clinical surface. |
| `SIGNOUT_SERVER_FAILURE_SILENT` | `Nav.handleSignOut` swallows a failed `POST /api/auth/sign-out` and clears local state anyway. The UI then says signed out while the server session may still be valid. Fixing it needs a UX decision (never block sign-out on a network error), so it is recorded, not changed. |
