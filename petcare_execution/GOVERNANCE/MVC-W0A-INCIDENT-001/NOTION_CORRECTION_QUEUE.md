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
