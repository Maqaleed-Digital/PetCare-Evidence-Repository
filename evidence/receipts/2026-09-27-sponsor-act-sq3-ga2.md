# GA-2 · Sponsor act SQ-3 recorded (MVC-BUILD-RUNNER-001 v1.3), 2026-09-27

```
PROGRAMME=MVC-BUILD-RUNNER-001 v1.3   PHASE=S   EXCEPTION=GA-2 (one-time; replaces M3 for this PR only)
BASE_MAIN=6a540fcb22491e345053ef53e8a3bf76e2c449a8
BRANCH=governance/v13-ga2-sq3
ACT_ID=MVC-SQ3-NFR08-STEP-UP-001   STATUS=RATIFIED   DATE=2026-09-27   LOCK=YES   SCOPE=NFR-08
ACT_FILE=governance/sponsor_acts/MVC-SQ3-NFR08-STEP-UP-001.md
ACT_SHA256=16efd2330f4b04e15aaf7cc04684897b7bd958feeb88c23a4133794e22f585cc   (sha256 of the whole file, as for SQ1/SQ2)
PATH_SET=exactly {ACT_FILE, this receipt}
COMMIT / PR / CI / MERGE_SHA: recorded in the v1.3 ledger after merge (a file cannot carry its own merge SHA)
GA-2=SPENT on merge
```

## Provenance of the act text
The act text is the SQ-3 block of the v1.3 instrument pasted by the Sponsor on 2026-09-27, with ONE Sponsor change
given in the Sponsor's follow-up message of the same session before recording:
`SQ-3 item 10 = "bulk export of any data."` (the instrument draft read "bulk export of personal data");
`SQ-3 item 11 remains "export of personal data."` Nothing else differs from the instrument text.

## Phase V (recorded here because no ledger segment exists yet for v1.3)
```
V1 CANONICAL_REPO=Maqaleed-Digital/PetCare-Evidence-Repository (git-common-dir …/petcare-evidence-repository/.git)
   WORKTREE=petcare-wt-build
V2 PASS  origin/main == BASE
V3 PASS  no open PRs
V4 PASS  tracked tree clean; detached at origin/main
V5 PASS  checker and served routes byte-stable; 2/16 ACCEPTED, 42/68 criteria, 2/13 NFR
V6 FINDING=V6-AUTHORITY-NOT-IN-REPO — no committed copy of M1–M5, CLARIFICATION-01 or the generic unit procedure;
   APPENDIX A (below) is the carried authority and is now in-repo through this receipt.
```

## APPENDIX A — carried v1.1 terms, verbatim (as embedded in the v1.3 instrument)
```
APPENDIX A — CARRIED v1.1 TERMS, VERBATIM
Source: Notion "Session Handoff — 24 Sep 2026" §7 (MVC-BUILD-RUNNER-001 v1.1), page 3e63ed7dc1048150b355e0da5dcb04ea.
The programme may merge a unit's PR without a separate Sponsor act only when ALL hold:
 M1 CI green on the unit's final head; at most one re-run, and only if the sole failure is the known UPHR flake
    (test_timeline_can_search) before U0 has merged;
 M2 every perturbation in the unit is ARMED (0 vacuous);
 M3 the diff touches none of: governance/**, requirements/register.yaml, requirements/authority/**,
    requirements/acceptance/phase1_high_pack.*, any existing evidence/receipts/* file;
 M4 the checker shows no FR's engineering status lower than before the unit, and ACCEPTED appears only as
    asserted by checker v1.3;
 M5 no HARD STOP fired. Merge method: merge commit.
This authorizes merges only. It authorizes no production, cloud, credential, counsel or scope act.
CLARIFICATION-01: If a unit cannot satisfy M1-M5 after the bounded correction permitted by the programme (one fix
attempt), leave its PR open and HALT the programme. Do not skip that unit and continue building later FR units from main.

NOT STOPS (record in SPONSOR_QUEUE / findings and continue within the unit or to the next unit): a criterion needing a
Sponsor product decision not covered by the ratified pack (leave that criterion's gap; complete the rest of the unit);
a criterion whose evidence needs an external counterparty, counsel or production (build the internal part only, never
fabricate DEPENDENCY evidence).

GENERIC UNIT PROCEDURE (every FR unit):
 1 git fetch origin && git checkout origin/main -b build/<unit-id>; tracked tree clean.
 2 Read the FR's ratified criteria (statement, fails_if, evidence, dependency, disposition, parameters, ratified_text)
   and its status.json criteria_gaps. Scope = every criterion gap closable without an external party, counsel,
   production or an uncovered Sponsor decision. Parameters are binding (e.g. REAL_TIME_BOUND p95 ≤ 5 s over ≥ 100 events).
 3 Build: server-side tenant and actor from the session only (Rule 21); persistence in PostgreSQL through the existing
   repository pattern; audit on every write; Arabic/RTL where the criterion names ARABIC_RTL; UI where it names UI.
   MVC-PHARM-001 applies to FR-13/FR-27/FR-14/FR-04/FR-19: supply classes, prescription gate only for
   POM/RESTRICTED/CONTROLLED, POM dispense veterinarian-only, no general-purpose pharmacy role, licence gate
   fail-closed (requirements PENDING COUNSEL). The earlier MVC-PHARM-002 design is advisory input only.
 4 Tests: every test driving main:app carries @pytest.mark.served_app. Each closed criterion gets a test whose
   failure mode is the criterion's fails_if. One perturbation per closed criterion, each ARMED.
 5 Bind: requirements/bindings.json (implements/routes/tests/fitness, each with basis file:line). Register evidence in
   requirements/acceptance/evidence.json only for types actually satisfied. Regenerate status.json with
   tools/check_register.py; served_routes.json with tools/list_served_routes.py main:app if routes changed.
 6 First real ACCEPTED: if this unit produces the first ACCEPTED FR, supersede
   test_ratified_pack.py::test_ratification_is_not_acceptance by replacing its body with an assertion that every
   ACCEPTED FR has acceptance_state ACCEPTED (record the supersession in the unit receipt). No other change to it.
 7 Receipt evidence/receipts/<date>-<unit-id>.md: criteria closed (AC ids), gaps remaining with reason, FR status
   before→after, perturbations, CI, M1–M5 check.
 8 Commit (explicit paths only), push, gh pr create, wait for CI. If M1–M5 hold: gh pr merge --merge and continue.
   If not: one fix attempt; if still unmet, leave the PR open and HALT (CLARIFICATION-01).
   Append one line per unit to evidence/receipts/<date>-mvc-build-runner-001.md (the programme ledger), committed with
   the next unit (a new file on the first unit; later lines appended by the lane that created it are permitted under M3).
```
