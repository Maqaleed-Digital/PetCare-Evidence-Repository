# MVC-EPC-D-001 v1.5 — Lane D Sponsor rulings register, continuation 2 (custody, append-only by new file; R15.2)

```
CREATED=2026-10-01   BY=Lane D runner (D2f)   AUTHORITY=R15.2
PREDECESSOR=evidence/receipts/2026-09-30-epc-d-rulings-register.md sha256 8f1dee0cfe5733dadab575f1db49dad360e9438117e49af086a07005523c8b71 (not modified)
RULE: only ruling text available VERBATIM from this session is custodied; nothing is reconstructed from a summary.
```

| IDENTIFIER | SOURCE | SHA256 | CUSTODY_STATUS |
|---|---|---|---|
| R16 (2026-10-01, SPONSOR RULING + EXECUTION — R16.1–R16.13) | pasted into the Lane D session on 2026-10-01; copied byte-for-byte as `evidence/receipts/2026-10-01-epc-d-rulings/R16.txt` (682 lines) | fa247de9a8609d458c916821d0107415044cdce8d0c15753cdd23cd6787fa0b0 | CUSTODIED VERBATIM |

## R16_ALREADY_ISSUED determination
```
R16_ALREADY_ISSUED=NO
EVIDENCE: the predecessor register lists R14 and R15 only; origin/main 1df6f24 holds no "R16" ruling text.
```

## Interpretations recorded under R15.13 (safe, reversible, no change to product/business semantics)
- **D2F-R16.4-SCOPE.** R16.4 names "the frozen FR-01 tests identified during D2e". Implementing X-27 surfaced the SAME
  placeholder-pet precondition conflict in four more frozen files whose consultations are created by one helper:
  `test_consultation_messaging.py::_consultation` (`"p1"`), `test_fr06_consultation.py::_book` (`"pet-6"`),
  `test_fr06_video.py::_book` (`"p"`, also imported by `test_sq2_video_nonprod.py`, which is byte-unchanged). The
  conflict is not materially different (no assertion of any of them expects a foreign or non-existent pet to be
  accepted), so the R16.4 precondition-only method was applied to them as well, with every assertion byte-identical
  (AST proof in the D2f receipt). This is disclosed for the Sponsor at the merge gate; rejecting it means reverting
  those four helper lines and holding X-27.
