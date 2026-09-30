# MVC-EPC-D-001 v1.5 — Lane D Sponsor rulings register (custody, append-only by new file; created under R15.2)

```
CREATED=2026-09-30   BY=Lane D runner (D2e)   AUTHORITY=R15.2
RULE: only ruling text available VERBATIM from this session or repository evidence is custodied. Nothing below is
      reconstructed from a summary. Where the original text is not available, a CUSTODY_EXCEPTION is recorded instead.
```

| IDENTIFIER | SOURCE | SHA256 | CUSTODY_STATUS |
|---|---|---|---|
| MVC-EPC-D-001 v1.5 (instrument) | Notion "Lane D — Engineering Completion Package (MVC-EPC-D-001…)" §8, page 3e83ed7d-c104-81fe-aee4-f23cb1902455 (last edited 2026-09-28T13:18:53Z) | — (not copied: the repository holds no byte copy, and a Notion render is not the pasted bytes) | REFERENCED — governing text read from Notion §8 in this session |
| R1–R9 (2026-09-27 resume rulings) | Notion §11 holds the text marked "DRAFT until the Sponsor pastes them"; the text as pasted is not in repository or session custody | — | **CUSTODY_EXCEPTION=R1-R9 REASON=VERBATIM_SOURCE_NOT_AVAILABLE** (only the pre-issue draft is available) |
| R10–R12 (2026-09-28 D2d continuation block) | Notion §13: the block "lives in the Sponsor's chat record of 28 Sep 2026"; §12 holds a superseded draft | — | **CUSTODY_EXCEPTION=R10-R12 REASON=VERBATIM_SOURCE_NOT_AVAILABLE** |
| R13 (2026-09-29, FR-23 consent interpretation) | evidence/receipts/2026-09-29-epc-d-d2d-r13-fr23-consent-interpretation.md (quotes R13.1 and R13.2 only) | f78f2818fb08fc74a143aaf1ea6403fc33ce82fd0f04416cf7b53698640f9ad3 (the receipt file) | PARTIAL — **CUSTODY_EXCEPTION=R13 (R13.3–R13.7 full text) REASON=VERBATIM_SOURCE_NOT_AVAILABLE** |
| R14 (2026-09-30, post-D2d record closure) | this runner session, Sponsor command "MYVETICARE CONTINUOUS PROJECT CLOSURE" §2 (issued because R14_ALREADY_ISSUED=NO) | 7e76c9632b2e265bb17b189703e9858a0351016c44bea7da7d89d7f1b4258b06 | CUSTODIED — evidence/receipts/2026-09-30-epc-d-rulings/R14.txt (verbatim) |
| R15 (2026-09-30, execution mechanics) | this runner session, same command §3 | 4b4c2c03b27a350bd106c99be612257de8d89cb636bba2067b95fb3a115815c5 | CUSTODIED — evidence/receipts/2026-09-30-epc-d-rulings/R15.txt (verbatim) |

## R14_ALREADY_ISSUED determination
```
R14_ALREADY_ISSUED=NO
EVIDENCE: `grep -rn -E '(^|[^F])R14' evidence/ governance/ requirements/` at origin/main 2f9a3c6 = 0 hits (every raw "R14"
  hit was an "FR14" substring); Notion Lane D page §11–§13 contain R1–R13 only. R14 is therefore issued by the 2026-09-30
  command itself and custodied once, above.
```

## R13 subsection citations in the merged D2d receipt (R14.0)
The merged D2d receipt cites R13.1, R13.2, R13.3, R13.5 and R13.7. Only R13.1 and R13.2 are available verbatim (above), so
the R13.3/R13.5/R13.7 citations can be neither confirmed nor shown wrong:
```
R13_CITATION_CHECK=NOT_VERIFIABLE (R13.3, R13.5, R13.7 — verbatim text not in custody)
R13_CITATION_CORRECTION=NONE (no incorrect citation is proven; the historical receipt is not edited)
```
