# MVC-ACCEPT-AUTH-001 v1.1 — acceptance-authority candidate, 2026-09-24

```
LANE=MVC-ACCEPT-AUTH-001
VERSION=1.1
TRACK=T0A_ACCEPTANCE_AUTHORITY
FROZEN=YES
AUTHORITY=MVC-COMPLETION-AMENDMENTS-001 AM-1
BASE_MAIN=413554c753bea02cc3219d723e32cf29be934d74
W1_MERGE_SHA=413554c753bea02cc3219d723e32cf29be934d74
BRANCH=authority/mvc-accept-auth-001
```

**This lane establishes candidate acceptance-authority evidence. It does not
ratify the BRD, the crosswalk, or any acceptance criterion.**

```
BRD_RATIFIED=NO
CROSSWALK_RATIFIED=NO
ACCEPTANCE_CRITERIA_AUTHORED=NO
PRODUCT_CODE_CHANGED=NO
CLOUD_ACTIONS=NONE
```

## Instruments

```
V10_PATH=governance/brd/PetCare KSA - BRD1.docx
V10_SHA256=5450f7832260532aafd080fa54999a66e7af914f1f3452ed3cb3c64950c640dc   (re-verified: MATCH)

V30_PATH=governance/brd/MVC-BRD-001_V3_0_DRAFT_MyVetiCare_Master_BRD.docx
V30_SHA256=b6991f0888eba781fceb2ae13a9d4c7a85f3204bbecce5b1c68bf160ff79a190   (custody copy: MATCH)
V30_BYTES=119064   V30_MTIME=2026-08-28 15:08:06 (preserved by cp -p)
V30_CUSTODY_SOURCE=~/Downloads/MyVetiCare_RedTeam_20260828/MVC-BRD-001_V3_0_DRAFT_MyVetiCare_Master_BRD.docx
V30_DOCUMENT_STATUS="MVC-BRD-001 V3.0 — DRAFT · NON-AUTHORISING · NOT FOR RATIFICATION"
  also: "This is a draft requirements body. It authorises nothing, ratifies nothing, supersedes nothing"
  also: "Not for ratification until preconditions P1–P3 are di[scharged]"
V30_GENERATOR=NOT_GENERATOR_READABLE
  tools/gen_register.py exit=3 stderr="no FR rows found in source instrument"
  structure: FR-01..FR-31 appear once, in one 4-column disposition table
  (Legacy | Requirement | Disposition | Where it lands / why), 36 rows incl. 4 NEW unnumbered.
  Read by tools/extract_v30_requirements.py (new, read-only). gen_register.py NOT modified.
```

## V3.0 vs v1.0

```
ONLY_IN_V10=[]
ONLY_IN_V30=[]
CHANGED_IDS=[FR-01, FR-02, FR-03, FR-04, FR-05, FR-07, FR-09, FR-12, FR-15, FR-17, FR-20, FR-21, FR-22, FR-27, FR-29, FR-31]
TITLE_CHANGES=16      (abridgement/punctuation; e.g. FR-01 drops "(Owner, Vet, Pharmacist, Admin)")
PRIORITY_CHANGES=0    V3.0 DOES NOT CARRY per-FR priority  -> fields_not_carried_by_candidate
PHASE_CHANGES=0       V3.0 DOES NOT CARRY per-FR phase     -> fields_not_carried_by_candidate
V30_NEW_UNNUMBERED=4  Notifiable-disease reporting · ZATCA Phase 2 e-invoicing · Licence lifecycle and gating · Inspection evidence pack
```

V3.0 disposition of the legacy FRs: MODIFY 13 · REJECT 6 (FR-08, FR-14 "as
specified, MODIFY in substance", FR-15, FR-16, FR-29, FR-31) · DEFER 5 · RETAIN 5
(FR-09, FR-19, FR-21, FR-23, FR-25) · FENCE 2 (FR-06, FR-11). Recorded in
`requirements/authority/v1_0_vs_v3_0.json` → `candidate_disposition`.

## REQ estate

```
SOURCE_COUNT=43        40 text (git grep -I) + 3 .docx (paragraph extraction); all sha256-pinned in tools/req_inventory.py
GRAMMAR=petcare_execution/tools/mvc_inventory.py (REUSED: IDENTIFIER + build())
RAW_DISTINCT_TOKENS=530
EXCLUDED=2             REQ-MVC-n (metavariable), REQ-UX-4-conformant (prose suffix)
DISTINCT_REQ=528
REQ_WITH_FAILS_IF=199
FAILS_IF_LINES=268     attributed 209 · unattributed 59 (withheld, not guessed)
```

**511 vs 513 vs 528, reconciled from evidence.**

| Figure | What it is | Reproduced here |
|---|---|---|
| 511 | Governed SET-A union (6 authority sources), `DENOMINATOR_RECONCILIATION.md` | **YES — set_a_union = 511 exactly** |
| 528 | Same grammar over all 43 REQ-bearing tracked files | measured |
| 528 − 511 = 17 | tokens occurring ONLY outside SET-A: `REQ-A`, `REQ-C`, `REQ-D`, `REQ-E`, `REQ-F`, `REQ-FIN`, `REQ-MVC`, `REQ-UX`, `REQ-UX-NTI`, `REQ-ABS`, `REQ-INT`, `REQ-PRD12`, `REQ-REG`, `REQ-SAF`, `REQ-SRC`, `REQ-VET` (parser-defect / namespace discussion in governance evidence and `mvc_inventory.py`) and `REQ-3` (synthetic test fixture) | none is an authority requirement |
| 513 | W1-session ad-hoc count, undeclared grammar and source set | **NOT reproducible**; governed raw distinct = 530 (529 without `REQ-MVC-n`) |

`in_set_a_not_in_estate=[]`. Nothing was tuned toward any historical figure.

**Fails-if rule.** A line opening "Acceptance — fails if", "Build fails if",
"CI fails if" or "Fails if" is recorded verbatim against the nearest preceding
single-id REQ header (id followed by a provenance tag, separator or line end;
or a Markdown heading naming one id) within 40 lines. Range headers
(`REQ-MVC-8.32–8.45`), compound headers (`REQ-MVC-7.19 (amended) · 7.41, 7.42`),
prose lines that merely open with an id, and non-REQ headings withhold
attribution. The rule was tightened twice during the run after inspection
found misattribution (prose-leading and compound headers); every change moved
clauses to UNATTRIBUTED or to their correct header, spot-checked 11/11.

## Candidate FR → REQ crosswalk

`requirements/authority/fr_req_crosswalk_candidate.json`, label
`CANDIDATE_NOT_RATIFIED`. Anchors: V3.1 Annex A `REQ-MVC-A.3` (the only
source-authored legacy-theme → REQ table, keyed to the v1.0 BRD sha
`5450f783…`) and the V3.0 disposition row for each FR.

```
HAS_CANDIDATE_CRITERIA=9/31   [FR-01, FR-02, FR-03, FR-04, FR-07, FR-13, FR-14, FR-19, FR-30]
NO_CANDIDATE=22/31
  mapped REQ, but no source-authored fails-if (9): [FR-05, FR-06, FR-08, FR-09, FR-10, FR-11, FR-20, FR-21, FR-29]
  no candidate REQ at all (13):                    [FR-12, FR-15, FR-16, FR-17, FR-18, FR-22, FR-23, FR-24, FR-25, FR-26, FR-27, FR-28, FR-31]
NO_CANDIDATE_IDS=[FR-05, FR-06, FR-08, FR-09, FR-10, FR-11, FR-12, FR-15, FR-16, FR-17, FR-18, FR-20, FR-21, FR-22, FR-23, FR-24, FR-25, FR-26, FR-27, FR-28, FR-29, FR-31]
HIGH_LINKS=10  MEDIUM_LINKS=24  LOW_LINKS=4   (38 links)
UNMAPPED_REQ=492
UNMAPPED_BY_NAMESPACE={MVC:433, UX:12, VET:10, FIN:5, A:4, E:4, SAF:4, D:3, SRC:3, ABS:2, C:2, F:2, INT:2, PRD12:2, REG:2, 0:1, 3:1}
```

| FR | coverage | candidates (REQ / confidence / fails-if lines) |
|---|---|---|
| FR-01 | HAS | 8.32/M/1 · 8.37/M/0 · 8.34/M/1 · 7.7/M/0 · 8.16/L/0 |
| FR-02 | HAS | 7.3/M/0 · 6.10/M/1 |
| FR-03 | HAS | 7.4/H/1 |
| FR-04 | HAS | 4.25/M/0 · 6.19/M/1 |
| FR-05 | NO | 4.11/H/0 · 4.12/H/0 · 7.7/M/0 · 4.10/M/0 |
| FR-06 | NO | 4.69/M/0 |
| FR-07 | HAS | 8.67/L/1 (LOW — delivery evidence only; V3.0 DEFERs chat) |
| FR-08 | NO | 5.4/L/0 (V3.0 REJECTs FR-08) |
| FR-09 | NO | 4.55/H/0 · 8.25/H/0 · 4.57/M/0 |
| FR-10 | NO | 4.71/M/0 |
| FR-11 | NO | 4.70/M/0 |
| FR-13 | HAS | 7.30/M/1 · 4.68/M/0 |
| FR-14 | HAS | REQ-DISP-AUTH-FAILCLOSED/H/1 · 7.11/H/0 · 8.38/M/1 · 4.24/M/0 |
| FR-19 | HAS | 7.12/H/0 · 6.22/H/1 · 7.32/M/1 |
| FR-20 | NO | 8.7/M/0 |
| FR-21 | NO | 7.3/H/0 · 4.6/M/0 |
| FR-29 | NO | REQ-FIN-G2/M/0 · REQ-FIN-G1/L/0 |
| FR-30 | HAS | 4.28/M/0 · 6.20/M/1 |

(`n.nn` = `REQ-MVC-n.nn`.) All other FRs: no candidate.

```
PHASE1_HIGH_16:
HAS_CANDIDATE_CRITERIA=8   [FR-01, FR-02, FR-04, FR-07, FR-13, FR-14, FR-19, FR-30]
NO_CANDIDATE=8             [FR-05, FR-06, FR-09, FR-15, FR-16, FR-20, FR-23, FR-27]

OPTION_A_BRIDGE_CONSISTENT=YES
  FR-14: bridge REQ-DISP-AUTH-FAILCLOSED (evidence/traceability/OPTION_A_FR14_FR27_BRIDGE.md:42) is a HIGH candidate.
  FR-27: the bridge names no REQ-* identifier (its aliases are rulings/custody ids); nothing to carry.
```

## Controls

```
TESTS=17/17
  REGISTER 5/5 · W1 6/6 · ACCEPT-AUTH 6/6 (tests/governance/test_acceptance_authority.py)
    test_req_inventory_is_current
    test_register_comparison_is_current
    test_crosswalk_is_labelled_candidate
    test_crosswalk_covers_every_fr_and_cites_basis
    test_coverage_matches_inventory
    test_no_ratification_or_authored_criteria   (also proves every fails-if is a verbatim source line)
```

| # | Perturbation | Control | Perturbed | Restored | Verdict |
|---|---|---|---|---|---|
| P1 | `req_inventory.json` distinct_req +1 | `test_req_inventory_is_current` | failed | passed | ARMED |
| P2 | comparison title_changes +1 | `test_register_comparison_is_current` | failed | passed | ARMED |
| P3 | crosswalk label → RATIFIED | `test_crosswalk_is_labelled_candidate` | failed | passed | ARMED |
| P4 | `REQ-NONEXISTENT-000` into FR-12 | `test_crosswalk_covers_every_fr_and_cites_basis` | failed | passed | ARMED |
| P5 | FR-14 coverage → NO_CANDIDATE | `test_coverage_matches_inventory` | failed | passed | ARMED |
| P6 | "ACCEPTED by Sponsor" into FR-14 basis | `test_no_ratification_or_authored_criteria` | failed | passed | ARMED |

```
PERTURBATIONS=6 ARMED=6 VACUOUS=0   (exact bytes restored; both BRDs never perturbed; sha256 re-verified)
REGRESSION (local, CI command)=949 passed / 0 skipped   (= 943 at W1 + 6)
SCANNERS: ACTIVE_LITERAL_DEFAULT=0 · SECRET_SCAN=CLEAN · BUNDLES=32 FAILED=0
```

## Artefacts

| Path | sha256 |
|---|---|
| `governance/brd/MVC-BRD-001_V3_0_DRAFT_MyVetiCare_Master_BRD.docx` | `b6991f0888eba781fceb2ae13a9d4c7a85f3204bbecce5b1c68bf160ff79a190` |
| `tools/extract_v30_requirements.py` | `46d9f9997ed9d79b7598959effec1bea1042538ff54020173d3d3f8c83a69706` |
| `tools/compare_registers.py` | `679846a9dc6388ac410f78439a7aa16dab5348f1c3f134b4cd8f0abd4a020400` |
| `tools/req_inventory.py` | `39b65072a5c76edd11ca4206d8d15bffd2738f5efb712c501cb9f7569d7a5e38` |
| `requirements/authority/v1_0_vs_v3_0.json` | `f58dbdc6e6946031cdf0f8a40f1ec62d2d021d46ddfb961a98f229f24774b272` |
| `requirements/authority/req_inventory.json` | `b4f0d3eb4ac00ffd5c93684247dcaab0e68800f24108155aef9d377e624f00c0` |
| `requirements/authority/fr_req_crosswalk_candidate.json` | `f6eeee4807993447877352438dbc8c6e39a74e0b3d3091dea48e1f4d07160144` |
| `tests/governance/test_acceptance_authority.py` | `0045ea386eddadd800ab0086d2096cadab2f60ed13fdc866507ee52b50bf97d7` |

`requirements/authority/register_v3_0.yaml` NOT created (generator could not read V3.0).

## Findings

1. **F-1 V30_SOURCE_PATH_DEVIATION.** The `.docx` was absent at the pinned
   `~/Downloads/` path; a byte-identical file (sha256 = pin) was at
   `~/Downloads/MyVetiCare_RedTeam_20260828/`. Custody is by hash; taken from there.
2. **F-2 V30_NOT_GENERATOR_READABLE** — disposition table, not a register; no
   per-FR priority or phase exists to compare.
3. **F-3 V30_REJECTS_SIX_LEGACY_FRS** incl. FR-14 "as specified" and FR-29
   (High in v1.0). Candidate links for rejected/fenced FRs point to the successor
   substance V3.0 names; they are not endorsements of the legacy wording.
4. **F-4 INVENTORY_PINS_PRODUCT_AND_TEST_FILES.** Mechanical discovery put
   `petcare_api/main.py`, `petcare_web/app/pharmacy/page.tsx`, migration `0029`,
   four governance tests and `requirements/bindings.json` in the manifest. Any
   edit to them fails `test_req_inventory_is_current` until the manifest is
   deliberately re-pinned. Forward risk for completion lanes.
5. **F-5 NON-AUTHORITY TOKENS.** 17 of 528 ids occur only in governance
   evidence, tooling and one test fixture.
6. **F-6 513_NOT_REPRODUCIBLE** (undeclared method).
7. **F-7 FAILS_IF_UNATTRIBUTED=59** under range/compound headers, §-headings
   without an id, or flattened tables > 40 lines from a header. Some of these are
   real criteria not keyable to one REQ without judgement.
8. **F-8 ONLY_THEME_LEVEL_LEGACY_MAPPING.** V3.1 Annex A maps legacy *themes*,
   not FR ids; no source maps FR-nn to REQ-*.
9. **F-9 CRITERIA_AUTHORING_NEEDED=22 FRs** (13 without any candidate REQ, 9
   whose candidates carry no authored fails-if).
10. **F-10 STDLIB_XML** advisory on the new extractor (hash-pinned input, same
    stance as `gen_register.py`).
