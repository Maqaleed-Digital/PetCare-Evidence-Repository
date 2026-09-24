# MVC-ACCEPT-CHECK-001 v1.0 — ACCEPTED only from complete ratified-criterion evidence, 2026-09-24

```
MVC_ACCEPT_CHECK_001=COMPLETE
VERSION=1.0
FROZEN=YES

BASE_MAIN=2e2dd96cbd9cd527bfd38df598f4ec7463ded2ac   (PR #43 merge; 5f3509d is an ancestor)
AUTHORITY=MVC-ACCEPT-PACK-P1 · MVC-COMPLETION-AMENDMENTS-001 AM-2 (refined)
SPONSOR_ACT_SHA256=2d272abe5defcd666dc76ad7ddfafc714f2f07d82e34110d48e8ae6813b4d7e3   (re-verified)
BRANCH=check/mvc-accept-check-001   (worktree ~/dev/petcare-wt-accept-check)

SERVED_APP_MARKER=conftest.py:72   (pytest_configure in the repository-root conftest; no root pytest.ini exists)
EVIDENCE_REGISTRY_COMMITTED_EMPTY=YES   requirements/acceptance/evidence.json == {}
CHECKER=tools/check_register.py  MVC-REQREG-003 v1.3

FR:
ACCEPTED=0
EVIDENCE_INCOMPLETE=16/16            (every ratified Phase-1 High FR)
CRITERIA_NOT_RATIFIED=15/15

ENGINEERING_STATUS_UNCHANGED_VS_W1=YES   (31/31 identical; 0 movements)
ENGINEERING_STATUS_COUNTS={ABSENT:22, BUILT_UNWIRED:5, REACHABLE_TESTED:3, REACHABLE_UNTESTED:1, BINDING_BROKEN:0, ACCEPTED:0}

NFR:
EVIDENCED=0
EVIDENCE_INCOMPLETE=13
NOT_PHASE1_RELEVANT=2   (NFR-13, NFR-14)
```

## What the checker now does

Engineering status is derived exactly as in W1 (register, bindings, served routes, symbol resolution, test
collection). On top of it, for every ratified FR, each criterion gets
`need = evidence types (+ DEPENDENCY when dependency != NONE)`, `have = registry types that mechanically hold`,
`criteria_gaps = sorted(need - have)`. TEST items hold when pytest collects them; SERVED_APP_E2E TEST items must
also collect under `-m served_app`; ARTEFACT items hold when the file exists and its sha256 matches. An FR is
ACCEPTED iff it is ratified, REACHABLE_TESTED, and every criterion has zero gaps. CLIENT_ACCEPTED is never
emitted. A malformed registry (unknown key, empty list, unknown type/kind, ARTEFACT without sha256) exits 2.
Output carries `authority`, `known_limits` (incl. "collection is not execution; CI executes" and
"served_app marker is a declaration"), per-FR `engineering_status`, `acceptance_state`, `criteria_gaps`, and `nfr`.

## Reachability proof (never committed)

```
REACHABILITY_PROOF=YES
TRANSITIONS=[
 FR-01 REACHABLE_TESTED/EVIDENCE_INCOMPLETE
 -> ACCEPTED/ACCEPTED                              (every FR-01 criterion's required types registered and holding)
 -> REACHABLE_TESTED/EVIDENCE_INCOMPLETE           (AC-FR-01-04 DEPENDENCY item removed; gap ['DEPENDENCY'])
]
proof inputs: TEST refs to existing collected tests; SERVED_APP_E2E -> petcare_api/tests/test_served_app_reachability.py
(drives main.app) temporarily module-marked served_app; UI and DEPENDENCY -> a temporary local artefact with its sha256.
No production, legal, regulatory, customer or external evidence was represented.
restored: evidence.json == {}; served_app marker removed (file diff empty); artefact deleted;
regenerated status.json byte-identical to the committed one (ACCEPTED=0).
```

## Controls

```
W1 SUPERSESSION: tests/governance/test_register_status.py::test_no_requirement_claims_acceptance replaced (only that function)
NEW: tests/governance/test_acceptance_status.py (directory collection; no CI config change)
  T1 test_evidence_registry_is_well_formed
  T2 test_accepted_only_for_ratified_frs
  T3 test_accepted_requires_complete_evidence       (recomputes need vs registered types independently of the checker)
  T4 test_nfr_states_follow_relevance
  T5 test_empty_evidence_registry_yields_no_acceptance
  T6 test_no_client_acceptance_is_emitted
TESTS=40/40 acceptance+governance suites (register 5 · W1 6 · accept-auth 7 · accept-pack 9 · ratified 7 · acceptance-status 6)
PERTURBATIONS=4_APPLIED/4_ARMED/0_VACUOUS
  P1 evidence key AC-FR-99-01                          -> T1 FAILS   ARMED
  P2 ARTEFACT item with incorrect sha256               -> T1 FAILS   ARMED
  P3 FR-01 status=ACCEPTED in status.json, evidence {} -> T3 FAILS   ARMED
  P4 NFR-13 state=EVIDENCED                            -> T4 FAILS   ARMED

REGRESSION_LOCAL=972 passed / 0 skipped   (= 966 + 6; PostgreSQL suites included via local ephemeral cluster)
WEB_UNIT=CI_ONLY  RESPONSIVE=CI_ONLY      (worktree has no node_modules; no web change)
SCANNERS: ACTIVE_LITERAL_DEFAULT=0 · SECRET_SCAN=CLEAN · BUNDLES=32 FAILED=0
DIFF_CHECK=CLEAN

RATIFIED_PACK_UNCHANGED=YES   SPONSOR_ACT_UNCHANGED=YES   BINDINGS_UNCHANGED=YES   (git diff vs origin/main empty)
```

## Artefacts

| Path | sha256 |
|---|---|
| `tools/check_register.py` | `1ca3fb65fec1720161b952542ae5b3cd69a1e5e2e75b883b28c058852d192711` |
| `requirements/status.json` | `b6cd4730618ec554480e561753b53d34a287b4edd07f6854ddf4dee4f7103072` |
| `tests/governance/test_acceptance_status.py` | `95bc10a18899868471c0404727745c06ee1bd2aec512c575b7c0bc00dd17df4a` |
| `conftest.py` | `2f29e0d952234ef4ead1993fa93c9f9de4e8b4094854c1aa7283c0d6c3177043` |
| `requirements/acceptance/evidence.json` | `{}` |

## Findings

1. **F-1 W1_SUPERSESSION_ADAPTED.** The issued replacement body assumed `_status()`, `EMITTABLE` and a dict-shaped
   `requirements`; this repository has `EMITTABLE_STATES` and a list. Adapted mechanically; assertions unchanged.
2. **F-2 LATENT_CONFLICT test_ratified_pack.py::test_ratification_is_not_acceptance.** It forbids ANY
   ACCEPTED/CLIENT_ACCEPTED in status.json. It passes now (ACCEPTED=0) but will fail the first time an FR
   legitimately reaches ACCEPTED. It needs the same supersession as the W1 control, in the lane that first
   produces an ACCEPTED FR (outside this lane's authorised files).
3. **F-3 NO_ROOT_PYTEST_CONFIG.** Marker registered via root `conftest.py` `pytest_configure`; the only ini
   (`petcare_execution/pytest.ini`) is not read by root-level runs.
4. **F-4 KNOWN_LIMITS.** Collection is not execution (CI executes); `served_app` is a declaration.

```
T0_STATE=CLOSED_PENDING_PR_MERGE
NEXT=MVC-BUILD-FR02-AC04
```
