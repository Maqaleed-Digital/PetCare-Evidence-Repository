# Phase R2 fix (v1.3) · U25 perturbations retargeted; step-up session binding re-guarded, 2026-09-27

```
PROGRAMME=MVC-BUILD-RUNNER-001 v1.3   PHASE=R2 (one fix attempt, bounded unit under M1–M5)
BASE_MAIN=41bca574fcccffa801d2bb1368854ab37929d706 (U30 merged, PR #78)   BRANCH=build/r2-fix-u25-retarget
TRIGGER=R2 replay on 41bca57: evidence/replay/2026-09-26/perturb_u25.py stopped at its first anchor
        (P-BYPASS-STEP-UP, main.py count 0) — U28 replaced the U25 mechanism under SQ-3.
```

## Diagnosis
Anchor drift was the symptom. The substantive defect: U25's guard that a step-up is bound to ONE session lived in
`test_a_configured_sensitive_operation_requires_a_fresh_session_bound_step_up`, which U28 removed as superseded
(env-configured policy). After U28 no test exercised session binding — a mutation letting any session of the same
person use another session's step-up would have passed the whole suite.

## Fix
- `test_nfr08_sq3.py::test_a_step_up_belongs_to_the_session_that_performed_it` (served_app, mfa_enforced) — added and
  registered as NFR-08 evidence (NON_PROD, SQ3 authority). NFR-08 items 14 -> 15; NFR-08 remains EVIDENCED.
- `evidence/replay/2026-09-27/perturb_u25_retargeted.py`: each U25 rule re-expressed against current code. The
  2026-09-26 corpus script is left unchanged (historical).
```
P-BYPASS-STEP-UP              ARMED   (new anchor: SQ-3 middleware)
P-STEP-UP-NOT-SESSION-BOUND   ARMED   (new guard: session-binding test)
P-NO-FRESHNESS                ARMED   (guard: 15-minute boundary test)
P-REPLAY-ALLOWED              ARMED   (unchanged anchor; mechanism test)
P-PLAINTEXT-SECRET            ARMED   (unchanged anchor; mechanism test)
P-PG-REPLAY-RACE              ARMED   (unchanged anchor; PG test)
P-RUNNER-CHOSEN-WINDOW        SUPERSEDED — guarded "the runner must not choose a window"; Sponsor act SQ-3 ratified
                              the window (15 min). Successor guard: perturb_u28.py P-EXTEND-FRESHNESS (ARMED).
ARMED=6 VACUOUS=0 SUPERSEDED=1
```
FINDING R2-U25-SESSION-BINDING-UNGUARDED (fixed here).
