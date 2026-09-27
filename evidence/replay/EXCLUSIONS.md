# Perturbation corpus — recorded non-ARMED items (MVC-EPC-D-001 Lane D, rule D3(c))

Every item below is NOT ARMED when the committed corpus is replayed, and each was already recorded as such by the receipt
cited. The replay tool (`tools/corpus_replay.py`) fails a PR if any non-ARMED item is missing from this list, or if any
committed perturbation changes classification between base and head. Items are never removed to make a replay pass.

| Key | Classification | Recorded by |
|---|---|---|
| evidence/replay/2026-09-26/perturb_u12.py::P-AC02-NO-TIMESTAMP | VACUOUS (first attempt; redesigned as P-AC02-DEFAULTED-TIMESTAMP, ARMED) | evidence/receipts/2026-09-25-u12-fr16-cold-chain.md |
| evidence/replay/2026-09-26/perturb_u14.py::P-AC03-PAID-UNCONFIRMED | VACUOUS (first attempt; redesigned as P-AC03-NO-CONFIRMATION-CHECK-ANYWHERE, ARMED) | evidence/receipts/2026-09-25-u14-fr20-cod-receipt.md |
| evidence/replay/2026-09-26/perturb_u21.py::P-AC02-NONVET-SUPPLY | VACUOUS (first attempt; redesigned as P-AC02-NONVET-SUPPLY-BOTH-LAYERS, ARMED) | evidence/receipts/2026-09-25-u21-fr27-class-scope.md |
| evidence/replay/2026-09-26/perturb_u25.py::* | SCRIPT_ERROR (anchor drift since U28 replaced the mechanism; superseded by evidence/replay/2026-09-27/perturb_u25_retargeted.py) | evidence/receipts/2026-09-27-r2-fix-u25-retarget.md |
| evidence/replay/2026-09-27/perturb_u25_retargeted.py::P-RUNNER-CHOSEN-WINDOW | SUPERSEDED (Sponsor act SQ-3 ratified the window; successor perturb_u28.py P-EXTEND-FRESHNESS) | evidence/receipts/2026-09-27-r2-fix-u25-retarget.md |
