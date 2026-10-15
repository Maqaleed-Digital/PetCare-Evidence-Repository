# MVC-EPC-D-001 v1.5 — Lane D Sponsor rulings register, continuation 4 (custody, append-only by new file; R15.2)

```
CREATED=2026-10-02   BY=Lane D runner (D2g, R18)   AUTHORITY=R15.2, R18.5
PREDECESSOR=evidence/receipts/2026-10-01-epc-d-rulings-register-c3.md sha256 dfca8a2c5958b848029badbd31bd9ff3372e0e9375aa5de70bddf60b222abefe (not modified)
INDEX=evidence/rulings/INDEX.md (every register file, chronological; continuity test tests/governance/test_rulings_register_continuity.py)
```

| IDENTIFIER | SOURCE | SHA256 | CUSTODY_STATUS |
|---|---|---|---|
| R18 (2026-10-01, Rulings on D2g progress — R18.1–R18.5) | Sponsor ruling pasted into the Lane D session; copied byte-for-byte as `evidence/receipts/2026-10-01-epc-d-rulings/R18.txt` (72 lines) | fd7fa3ae0d3397860a5479951ab7a8c7dc78ccd26d35b18278b72923498de526 | CUSTODIED VERBATIM |

Finding D2G-R18-CUSTODY-NEW-FILE: the continuation instruction asked to custody R18 "in the current R17+ rulings file"
(continuation 3). That file is already committed (b9ef482), so appending would modify committed bytes (stop S3). R18 is
custodied by this new file; the index makes every register file discoverable as one chain.
