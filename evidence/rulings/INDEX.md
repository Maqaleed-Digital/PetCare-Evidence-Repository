# MVC-EPC-D-001 — Lane D rulings-register INDEX (authoritative; Sponsor ruling R18.5)

Every rulings-register file, in chronological order. Each ruling R1..R<highest> is listed in exactly one indexed file's
register table (IDENTIFIER column, first cell). Register files are append-only by new file and are never edited; this index
is the one maintained file — a new ruling adds a new register file and a new row here. Executable check:
`tests/governance/test_rulings_register_continuity.py` (discoverable, exactly once, no gap, no duplicate, hashes match).

| # | FILE | RULING RANGE | SHA256 | NOTE |
|---|---|---|---|---|
| 1 | `evidence/receipts/2026-09-30-epc-d-rulings-register.md` | R1–R15 | 8f1dee0cfe5733dadab575f1db49dad360e9438117e49af086a07005523c8b71 | R1–R9, R10–R12 custody exceptions; R13 partial; R14, R15 verbatim |
| 2 | `evidence/receipts/2026-10-01-epc-d-rulings-register.md` | R16 | 7af65fe52492693be7ff83ec1168f36074a18a23c68d86476f0a93f789278b2f | R16 verbatim |
| 3 | `evidence/receipts/2026-10-01-epc-d-rulings-register-c3.md` | R17 | dfca8a2c5958b848029badbd31bd9ff3372e0e9375aa5de70bddf60b222abefe | R17 verbatim |
| 4 | `evidence/receipts/2026-10-02-epc-d-rulings-register-c4.md` | R18 | 0871d988c048b61e4f84ffd8c3303cd2707bffb1798a2cabc7af284638b6e792 | R18 verbatim |
| 5 | `evidence/receipts/2026-10-15-epc-d-rulings-register-c5.md` | R19 | fbb32db688e7584ccc1f9b956e67a9d0f3b513521779ea3a055778367fe2b1ec | R19 verbatim (as relayed by the Sponsor 2026-10-15; issued 2026-10-04); punctuation correction annotated in row 6 (R20.3) |
| 6 | `evidence/receipts/2026-10-15-epc-d-rulings-register-c6.md` | R20 | 33047ad39e623862822e0fb3dc70a7f294f60db820e77a7dbba0b3e8aeb6e9f3 | R20 verbatim; R19 correction annotation (R20.3) |
