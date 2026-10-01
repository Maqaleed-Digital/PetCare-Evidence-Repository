# MVC-EPC-D-001 v1.5 — Lane D Sponsor rulings register, continuation 3 (custody, append-only by new file; R15.2)

```
CREATED=2026-10-01   BY=Lane D runner (D2g)   AUTHORITY=R15.2
PREDECESSOR=evidence/receipts/2026-10-01-epc-d-rulings-register.md sha256 7af65fe52492693be7ff83ec1168f36074a18a23c68d86476f0a93f789278b2f (not modified)
```

| IDENTIFIER | SOURCE | SHA256 | CUSTODY_STATUS |
|---|---|---|---|
| R17 (2026-10-01, Rulings on D2f — R17.1–R17.4) | the D2g execution command, block "--- R17 BEGIN ---" … "--- R17 END ---" copied word for word as `evidence/receipts/2026-10-01-epc-d-rulings/R17.txt` (markers included, one trailing newline) | 3cdb943ac51f5d2eed53b476e7e3ed45f514d2fe33389c2ab000f33c79dbfb70 | CUSTODIED VERBATIM |

Finding D2G-R17-REGISTER-APPEND-WOULD-MODIFY-COMMITTED: the command asked to append R17 to "the file that holds R14–R16".
No single file does (R14/R15: 2026-09-30-epc-d-rulings-register.md; R16: 2026-10-01-epc-d-rulings-register.md), and both are
committed receipts, so appending would modify committed bytes (stop S3). R17 is custodied by a new file instead, the register's
own append-only-by-new-file rule.
