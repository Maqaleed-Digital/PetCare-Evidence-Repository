# MVC-ACCEPT-PACK-P1 v1.0 — DRAFT Phase-1 High acceptance pack, 2026-09-24

```
LANE=MVC-ACCEPT-PACK-P1
VERSION=1.0
FROZEN=YES (AM-5)
TRACK=T0A
AUTHORITY=MVC-ACCEPTANCE-AUTHORITY-001 (AA-1..AA-5, ratified 24 Sep 2026, LOCK) ·
          MVC-COMPLETION-AMENDMENTS-001 · MVC-PHARM-001 (ratified 24 Sep 2026)
BASE=origin/main 6b16e28d4a07442f5e60fed102cff79d2170bfb7   (precondition: ancestor check PASS)
BRANCH=accept/mvc-accept-pack-p1   (worktree ~/dev/petcare-wt-accept-pack)
LABEL=DRAFT_NOT_RATIFIED
REQUIREMENT_IDS_MOVED=none   status.json NOT touched   ACCEPTED=0
PRODUCT_CODE_CHANGED=NO   CLOUD_ACTIONS=NONE
```

**Nothing in this pack is ratified.** It is the one batched document for the Sponsor decision
at the top of `requirements/acceptance/phase1_high_pack.draft.md`.

## Denominator

```
BRD_SHA256=5450f7832260532aafd080fa54999a66e7af914f1f3452ed3cb3c64950c640dc   (bound; control-tested)
PHASE1_HIGH_IDS=[FR-01, FR-02, FR-04, FR-05, FR-06, FR-07, FR-09, FR-13, FR-14, FR-15, FR-16, FR-19, FR-20, FR-23, FR-27, FR-30]
FR_COVERED=16/16
W1_MEASURED_AT=6b16e28d4a07442f5e60fed102cff79d2170bfb7
```

## Pack

```
CRITERIA_TOTAL=68
PER_FR=[FR-01:4, FR-02:4, FR-04:5, FR-05:4, FR-06:5, FR-07:3, FR-09:3, FR-13:4, FR-14:7, FR-15:4, FR-16:4, FR-19:4, FR-20:4, FR-23:4, FR-27:4, FR-30:5]
FROM_CANDIDATE_MAPPING=8/16   [FR-01, FR-02, FR-04, FR-07, FR-13, FR-14, FR-19, FR-30] — AA-3's evidence-backed mappings in the Phase-1 High set
FROM_BRD_ONLY=8/16            [FR-05, FR-06, FR-09, FR-15, FR-16, FR-20, FR-23, FR-27]
DEPENDENCIES: NONE=42 · PRODUCTION=3 · EXTERNAL=17 · COUNSEL=6
  EXTERNAL: KYC_PROVIDER, LOGISTICS_PARTNER, MAPS_API, SFDA, SFDA_API, SMS_GATEWAY, VET_LICENSING_AUTHORITY
            (each external FR has an adapter/contract criterion AND a separate live-counterparty criterion, R6)
  COUNSEL:  EV-11, L-2, MVC-PHARM-001_§6c, REG-02_TELEMEDICINE
INTERPRETATIONS_FOR_SPONSOR=16  [AC-FR-01-04, AC-FR-02-04, AC-FR-04-01, AC-FR-04-04, AC-FR-05-01, AC-FR-06-05,
                                 AC-FR-07-02, AC-FR-13-01, AC-FR-14-06, AC-FR-15-01, AC-FR-16-03, AC-FR-20-02,
                                 AC-FR-23-01, AC-FR-27-01, AC-FR-30-01, AC-FR-30-03]
                                 + NFR interpretation notes: NFR-07, NFR-09, NFR-15
CUSTOMER_FACING=14 (all carry UI evidence)   CLIENT_ACCEPTANCE_APPLIES=15
TENANT_ISOLATION+AUDIT: present for every FR holding tenant data (15/16; FR-09 is a language property, holds none)
```

**Sourcing rules applied.** REQ sources are cited only for the 8 FRs whose mapping AA-3 ratified as
evidence-backed, and only REQs in that FR's candidates (R2). The 8 BRD-only FRs cite BRD v1.0 paragraphs
only. MVC-PHARM-001 is cited as `SPONSOR_ACT` for supply-class rules (R5): class from SFDA registration;
unverified veterinary medicine = POM; prescription gate for POM/RESTRICTED/CONTROLLED only; POM dispense
veterinarian-only until counsel; no general-purpose pharmacy role. V3.0 dispositions are not applied
(AA-2): FR-14, FR-15, FR-16 are drafted in full, with the proposed V3.0 change noted where relevant.

## NFR evidence definitions (AA-5)

```
NFR: PHASE1_RELEVANT=13/15   DEFINED=13   ENVIRONMENT_PRODUCTION=6 (NFR-05, 07, 09, 10, 11, 12)
NOT_PHASE1_RELEVANT=[NFR-13 (Milestone 2.3 P471), NFR-14 (Milestone 2.3 P473)]
Thresholds are the BRD targets verbatim.
NFR-07 interpretation: BRD §7.2 P360 "AWS/GCP in Bahrain region" conflicts with NFR-07 "All data stored in KSA-based servers".
```

## Controls

```
TESTS=26/26   register 5 · W1 6 · accept-auth 7 · accept-pack 8 (tests/governance/test_acceptance_pack.py, verbatim as issued)
PERTURBATIONS=6 applied, 6 ARMED, 0 vacuous
  P1 label -> RATIFIED                                -> test_pack_is_draft                                 ARMED
  P2 remove FR-23                                     -> test_pack_covers_exactly_phase1_high               ARMED
  P3 add REQ-MVC-8.25 to FR-14 (outside candidates)   -> test_req_sources_are_ratified_candidate_mappings   ARMED
  P4 FR-14 dependency -> MAYBE                        -> test_every_criterion_is_well_formed                ARMED
  P5 FR-09 UI evidence removed from all criteria      -> test_customer_facing_requirements_carry_ui_evidence ARMED
  P6 one byte of rendered .md changed                 -> test_review_document_is_current                    ARMED
REGRESSION (local, CI command)=958 passed / 0 skipped   (= 950 + 8)
SCANNERS: ACTIVE_LITERAL_DEFAULT=0 · SECRET_SCAN=CLEAN
CI_CONFIG_CHANGED=NO (directory collection)
```

## Artefacts

| Path | sha256 |
|---|---|
| `requirements/acceptance/phase1_high_pack.draft.json` | `72705323bae1ed0e77181e3948fd46abdced1d1eaac3dbf58c0506bdc9069302` |
| `requirements/acceptance/phase1_high_pack.draft.md` | `4267149bba4cc2b43c18b1a843c73fdc5535c2d8699f8989b38a2fcdaa94b9cc` |
| `tools/render_acceptance_pack.py` | `15935e24f62fbf763e114ed2f52d9c90199f9218938c33552e5b09b0c3d44d41` |
| `tests/governance/test_acceptance_pack.py` | `71b47d379e4467457ecbf9dfb3b245ab2c5bc3cf7feee412cdac4eda091c8a54` |

## Findings

1. **F-1 R2_CONTROL_WIDER_THAN_AA3.** `test_req_sources_are_ratified_candidate_mappings` (issued verbatim)
   permits any REQ in an FR's crosswalk candidates. AA-3 ratified only the 9 evidence-backed mappings; FR-05,
   FR-06, FR-09 and FR-20 carry candidates that are NOT among them. The pack cites no REQ for those FRs, but
   the control would not catch it. Tightening requires amending the issued test text.
2. **F-2 CRITERIA_THAT_FAIL_TODAY.** AC-FR-02-04 (audit actor from session) would fail on current code: W1
   measured `POST /api/pets` writing a client-supplied actor.
3. **F-3 UNMEASURABLE_BRD_TARGETS.** NFR-09 and NFR-15 thresholds are not measurable as written; "real-time"
   (FR-13, FR-27) and "optimal" (FR-15) need Sponsor-set values. Each is an interpretation note.
4. **F-4 NFR_DEFINITIONS_FOR_NON_RELEVANT.** AA-5 requires definitions for all 15; NFR-13/14 are marked not
   Phase-1 relevant and carry none yet.
5. **F-5 CRITERION_DRAFTED_WITHOUT_SOURCE_FAILS_IF.** AC-FR-30-03 cites REQ-MVC-4.28, which has no
   source-authored fails-if; the criterion text is drafted in this pack (flagged).
6. **F-7 RENDERER_TRAILING_BLANK_LINE.** The verbatim renderer ends the `.md` with a blank line, which
   `git diff --check` reports ("new blank line at EOF"). Not altered: the renderer and its byte-identity
   control are issued text. Cosmetic only.
7. **F-6 UPHR_LANE_NOT_RUN_HERE.** The MVC-HYG-UPHR-001 block was not in this session's input; its worktree
   `~/dev/petcare-wt-uphr` exists at origin/main, untouched.

---

## v1.1 — AA-3 enforced in the standing controls

```
VERSION=1.1   FROZEN=YES (AM-5)   START_HEAD=2fcf24c22b4766d6f9b13c5269b9e6e3551c111d
REASON=v1.0 F-1 — the REQ-source control admitted REQs from mappings AA-3 did not ratify
       (FR-05, FR-06, FR-09, FR-20 have candidates but no evidence-backed criteria); candidate_source was unvalidated.
V1_0_TEXT_PRESERVED=YES (sections above unedited)
```

**Changes (exactly three).**
1. `test_req_sources_are_ratified_candidate_mappings` now admits a REQ only when that FR's crosswalk
   coverage is `HAS_CANDIDATE_CRITERIA` (AA-3's evidence-backed set), via `_aa3_ratified()`, read from the
   crosswalk and not from a hard-coded list.
2. New `test_candidate_source_matches_aa3`: `candidate_source` must be `RATIFIED_CANDIDATE_MAPPING` exactly for
   AA-3-ratified FRs, `NONE` otherwise.
3. Perturbations P7 and P8 added.

No criteria text, pack data, renderer or rendered document changed. An earlier shorter v1.1 variant (renderer
edit) was begun and discarded before commit on Sponsor instruction; it is not part of this version.

```
AA3_RATIFIED_FRS_IN_PACK=[FR-01, FR-02, FR-04, FR-07, FR-13, FR-14, FR-19, FR-30]
REQ_CITATIONS=18   REQ_CITATIONS_OUTSIDE_AA3=0
CANDIDATE_SOURCE_CORRECTIONS=0   (existing pack data already matched AA-3)
TESTS=27/27   register 5 · W1 6 · accept-auth 7 · accept-pack 9
PERTURBATIONS=8 applied, 8 ARMED, 0 vacuous
  P1–P6 re-run from v1.0                                                  ARMED
  P7 FR-05 crosswalk candidate REQ-MVC-4.11 cited in AC-FR-05-01
     -> test_req_sources_are_ratified_candidate_mappings FAILS             ARMED
     discrimination: the same perturbation PASSES the v1.0 control (vacuous there) — F-1 was real and is closed
  P8 FR-05 candidate_source -> RATIFIED_CANDIDATE_MAPPING
     -> test_candidate_source_matches_aa3 FAILS                            ARMED
  git diff after reverts: only the intended test-file change
REGRESSION (local, CI command)=959 passed / 0 skipped   (= 958 + 1)
test_acceptance_pack.py sha256=d8deabf064b2dc4e8f82c27717e3d66d8cb1527a8a66c7a60e6f2960cf338b91
```

### v1.1 findings
- **F-1 CLOSED.**
- **F-7 OPEN (unchanged).** The renderer's trailing blank line remains; this version's scope excludes the renderer.
- **AC-FR-02-04 failing today is FR-02 build work** (client-supplied audit actor on `POST /api/pets`), not a pack defect.

---

## v1.2 — Sponsor ratification frozen

```
MVC_ACCEPT_PACK_P1=COMPLETE
VERSION=1.2
FROZEN=YES

BASE_HEAD=2c7f48ee00d9f56fa11fa602f44430714187543d
SPONSOR_DECISION=MVC-ACCEPT-PACK-P1   (RESULT=RATIFY_ALL_WITH_INTERPRETATIONS, LOCK=YES, EXCEPTIONS=[])
SPONSOR_ACT_PATH=governance/sponsor_acts/MVC-ACCEPT-PACK-P1.md   (decision text verbatim, marker lines excluded)
SPONSOR_ACT_SHA256=2d272abe5defcd666dc76ad7ddfafc714f2f07d82e34110d48e8ae6813b4d7e3
RATIFIED_DATE=2026-09-24   HASH_BINDING_DATE=2026-09-24

CRITERIA_RATIFIED=68
FR_COVERED=16/16
PHASE1_RELEVANT_NFR=13/15

DISPOSITIONS={ACCEPT:59, ACCEPT_WITH_CLARIFICATION:4, ACCEPT_WITH_LIMIT:1, ACCEPT_WITH_SCOPE:1, ACCEPT_WITH_THRESHOLD:3}
NFR_DISPOSITIONS={ACCEPT:11, ACCEPT_WITH_THRESHOLD:2}   (NFR-13, NFR-14 phase1_relevant=false, no disposition)

PARAMETERISED=[AC-FR-13-01, AC-FR-15-01, AC-FR-23-01, AC-FR-27-01, NFR-09, NFR-15]

KNOWN_FAILING=[AC-FR-02-04]   (DISPOSITION=BUILD_REMEDIATION_NOT_REQUIREMENT_REOPEN)
ACCEPTED=0
CLIENT_ACCEPTED=0

DRAFT_JSON_UNCHANGED=YES   sha256 72705323bae1ed0e77181e3948fd46abdced1d1eaac3dbf58c0506bdc9069302
DRAFT_MD_UNCHANGED=YES     sha256 4267149bba4cc2b43c18b1a843c73fdc5535c2d8699f8989b38a2fcdaa94b9cc
STATUS_JSON_UNCHANGED=YES  sha256 5f74fd4aecaa9c17f2be5f914441135907dd7325081e240e79bc6bdff17bfa42 (git diff vs BASE_HEAD empty)
```

**Derivation.** `requirements/acceptance/phase1_high_pack.ratified.json` was produced mechanically from the draft
JSON and the committed Sponsor-act bytes: each `I-nn AC-…=DISPOSITION` / `NFR-nn=DISPOSITION` header gives the
disposition; its body lines, verbatim, are `ratified_text`; `KEY=VALUE` lines are `parameters`; an indented block
under `KEY:` (OPTIMAL_ROUTING_RULE) is one parameter. Criteria without an I-entry: `ACCEPT`, `""`, `{}`. Every
decision entry was consumed; none unmatched. The six frozen fields of every criterion are byte-equal to the draft.

### Non-ACCEPT dispositions and parameters (for Sponsor verification)

| Item | Disposition | Parameters |
|---|---|---|
| AC-FR-04-01 | ACCEPT_WITH_CLARIFICATION | — |
| AC-FR-05-01 | ACCEPT_WITH_CLARIFICATION | — |
| AC-FR-07-02 | ACCEPT_WITH_LIMIT | — |
| AC-FR-13-01 | ACCEPT_WITH_THRESHOLD | REAL_TIME_BOUND=5_SECONDS |
| AC-FR-15-01 | ACCEPT_WITH_CLARIFICATION | OPTIMAL_ROUTING_RULE=1 eligible/licensed for supply class · 2 fulfils complete basket · 3 lowest route ETA · 4 tie-break route distance · 5 tie-break stable pharmacy identifier |
| AC-FR-20-02 | ACCEPT_WITH_CLARIFICATION | — |
| AC-FR-23-01 | ACCEPT_WITH_THRESHOLD | REMINDER_DEFAULT=7_DAYS_BEFORE_DUE · SECOND_REMINDER=24_HOURS_BEFORE_DUE_IF_OUTSTANDING |
| AC-FR-27-01 | ACCEPT_WITH_THRESHOLD | REAL_TIME_BOUND=5_SECONDS |
| AC-FR-30-01 | ACCEPT_WITH_SCOPE | — |
| NFR-09 | ACCEPT_WITH_THRESHOLD | STANDARD=Saudi_PDPL + Implementing_Regulations + applicable_SDAIA_instruments · PASS=100_PERCENT_APPLICABLE_CONTROLS_EVIDENCED · UNRESOLVED_CRITICAL_FINDINGS=0 · UNRESOLVED_HIGH_FINDINGS=0 · EVIDENCE_BASIS=PDPL compliance matrix, to be produced and Sponsor-approved · DEPENDENCY=COUNSEL:PDPL_COMPLIANCE_MATRIX |
| NFR-15 | ACCEPT_WITH_THRESHOLD | AUTHENTICATED_DEFAULT=100_REQUESTS_PER_MINUTE_PER_PRINCIPAL · ANONYMOUS_DEFAULT=30_REQUESTS_PER_MINUTE_PER_CLIENT_IP · EXCESS_RESPONSE=HTTP_429 · ENDPOINT_SPECIFIC_STRICTER_LIMITS=PERMITTED |

I-entries with disposition ACCEPT that carry ratified text: AC-FR-01-04, AC-FR-02-04, AC-FR-04-04, AC-FR-06-05,
AC-FR-14-06, AC-FR-16-03, AC-FR-30-03, NFR-07.

### Controls

```
TESTS=34/34   register 5 · W1 6 · accept-auth 7 · accept-pack 9 · ratified-pack 7 (tests/governance/test_ratified_pack.py)
  test_ratified_pack_is_bound_to_sponsor_act
  test_ratification_did_not_alter_criteria_text
  test_every_criterion_has_a_disposition
  test_all_68_criteria_present_and_known_failing_recorded
  test_relevant_nfrs_have_a_disposition
  test_sponsor_parameters_are_preserved
  test_ratification_is_not_acceptance
PERTURBATIONS=7_APPLIED/7_ARMED/0_VACUOUS   (Sponsor act never perturbed; sha re-verified after run)
  P1 sponsor_act_sha256 changed                         -> ..._bound_to_sponsor_act              ARMED
  P2 AC-FR-14-01 statement edited                       -> ..._did_not_alter_criteria_text       ARMED
  P3 AC-FR-09-01 disposition removed                    -> ..._every_criterion_has_a_disposition ARMED
  P4 AC-FR-04-01 ratified_text emptied                  -> ..._every_criterion_has_a_disposition ARMED
  P5 AC-FR-13-01 REAL_TIME_BOUND -> 10_SECONDS          -> ..._sponsor_parameters_are_preserved  ARMED
  P6 NFR-09 COUNSEL:PDPL_COMPLIANCE_MATRIX removed      -> ..._sponsor_parameters_are_preserved  ARMED
  P7 known_failing -> []                                -> ..._known_failing_recorded             ARMED

REGRESSION_LOCAL=966 passed / 0 skipped   (= 959 + 7; includes PostgreSQL suites against a local ephemeral cluster)
WEB_UNIT / RESPONSIVE: measured in CI (worktree carries no node_modules; web code unchanged)
SCANNERS: ACTIVE_LITERAL_DEFAULT=0 · SECRET_SCAN=CLEAN
DIFF_CHECK=CLEAN   (F-7 residual lives only in the unchanged draft .md; not reported against this diff)
CI_CONFIG_CHANGED=NO (directory collection)
```

### v1.2 findings
- **F-7 COSMETIC RESIDUAL.** The frozen draft `.md` still ends with a blank line; not modified, per instruction.
- **NFR-15 line `LIMITS_MUST_BE_CONFIGURABLE_AND_AUDITABLE`** carries no `=` and is therefore recorded in
  `ratified_text`, not as a parameter.
- **Ratification is authority only.** `ACCEPTED` stays unreachable until the checker lane binds criterion evidence.

```
PHASE1_REQUIREMENTS_DEFINITION=CLOSED_PENDING_MERGE
NEXT_ACCEPTANCE_BOUNDARY=SPONSOR_MERGE_PR43
```
