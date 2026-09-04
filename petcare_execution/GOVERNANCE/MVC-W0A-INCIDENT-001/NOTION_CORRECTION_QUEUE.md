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
