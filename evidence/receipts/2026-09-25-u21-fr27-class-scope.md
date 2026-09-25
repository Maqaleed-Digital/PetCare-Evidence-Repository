# U21 · FR-27 AC-FR-27-02 — dashboard actions limited by supply class (internal part), 2026-09-25

```
PROGRAMME=MVC-BUILD-RUNNER-001 v1.1   UNIT=U21   BASE_MAIN=d782596a595866810f5c8a51cb966b565b148466 (U20 merged, PR #65)
BRANCH=build/u21-fr27-ac02
SELECTION (pass 2): FR-27 (1 dependency criterion, REACHABLE_TESTED) — its L-2 criterion carried non-dependency gaps.
CRITERIA_CLOSED=[] (AC-FR-27-02's internal part evidenced; gap now [DEPENDENCY] only — COUNSEL:L-2)
GAPS_REMAINING={AC-FR-27-02: [DEPENDENCY] — COUNSEL:L-2}
FR-27: REACHABLE_TESTED / EVIDENCE_INCOMPLETE (3/4; the remaining criterion is exclusively COUNSEL-gated)
```

## What is proven (no product change was needed)
Through the served app, with the dashboard's non-veterinarian user (partner clinic admin):
- a POM dispense from the dashboard queue is refused — directly (`/dispense`) and via a supply citing the prescription;
- RESTRICTED/CONTROLLED are outside EVERY actor's scope (AC-FR-04-02 gate) — refused for the dashboard user and the vet;
- GENERAL/OTC actions stay with dashboard staff (receipt and supply succeed) — scope is limited, not removed;
- every refusal is audited under the actor who attempted it.
The class-scoped pharmacy actor the criterion anticipates is defined by counsel (L-2); DEPENDENCY is not evidenced.

## Perturbations
```
P-AC02-NONVET-DISPENSE              dispense role check removed              -> FAILS  ARMED
P-AC02-NONVET-SUPPLY                supply role check removed                -> VACUOUS (first attempt): the practitioner
                                    authority check also refuses — defence in depth. REDESIGNED as:
P-AC02-NONVET-SUPPLY-BOTH-LAYERS    role check AND authority check removed   -> FAILS  ARMED
P-AC02-OUT-OF-SCOPE-CLASS           restricted-substance gate opened         -> FAILS  ARMED
P-AC02-OVER-RESTRICTED-GENERAL      prescription gate on GENERAL too         -> FAILS  ARMED
P-AC02-REFUSAL-UNAUDITED            dispense refusal not audited             -> FAILS  ARMED
FINAL SET: PERTURBATIONS=5 ARMED=5 VACUOUS=0
```
