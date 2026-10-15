# MVC-EPC-D-001 — Lane D ledger segment s17 (predecessor evidence/receipts/2026-10-15-epc-d-ledger-s16.md, sha256 1cd9df0daa2214b50a283cfce9ed42418b1c47c02e76a212d90919562b43e8c3, not modified)

| Unit | PR | Head | Merge SHA | CI attempts | D1–D6 | Journeys PASS | Screens PASS |
|---|---|---|---|---|---|---|---|
| D2n J-O9 internal tracking [J-O9-INTERNAL] (merge record — s16 left it "(this PR) / pending"); J-O9 UNCOUNTED, reason R21.1 | #98 | 44d049d9524afbc473da926496b962064e802571 | 496235c18a76fc20b722041d3e4fa38927af9c99 | verify: SUCCESS on head | see D2n receipt (E2E 4/4) | 9/53 | 11/107 |
| R20 custody (merge record) | #99 | 215a2289fc774ebd16acb0885f0605cc9b0b7195 | b13016879bebf413eb69e575cc38dbd7a08cc310 | verify: SUCCESS on head | rulings continuity 3/3 | 9/53 | 11/107 |
| R21 custody (merge record) | #100 | 173ba4d4fbb634ba6bb3ff1dea0b313bf0487239 | ef073caf80602163c04900ae47e280c0f7ff1c5e | 1 (verify: SUCCESS) | rulings continuity 3/3; R1–R21 each once | 9/53 | 11/107 |
| R21.3 .claude-flow hygiene (merge record) | #101 | 421941b038ece5a5223f0ee7b993374c26e00dae | 51fcccd517f072589f955400617231b4c4d1c4c2 | 2 (head 20e855e SUCCESS, merge refused: required check expected on a head current with main; main merged in -> head 421941b SUCCESS) | see receipt 2026-10-15-epc-d-r21-3-claude-flow-hygiene.md | 9/53 | 11/107 |
| R21.1 annotation (this segment) | (this PR) | see PR | pending | see PR | no code | 9/53 | 11/107 |

## R21.1 — J-O9 counting (annotation; no count changed by hand)

J-O9 is **UNCOUNTED**, reason **R21.1**: `[J-O9-INTERNAL]` does not count J-O9. Its carrier readings are blocked on the logistics
partner (R18.4), and its "pharmacy assigned" (ROUTED) step is proven only through the FR-15 maps contract double, which R18.4 bars
from counting a journey. J-O9 counts only when both are proven against real providers. The internal-tracking spec
(`petcare_web/e2e-full/jo9-tracking.spec.ts`) stays as uncounted partial evidence. `report.mjs` already does not count the tag
(`J-O9-INTERNAL` is not a journey id), so the matrix on main is unchanged: `petcare_web/e2e/JOURNEYS.md` J-O9 NO_TEST.

Ledger rows: none added or closed. HYG-CLAUDE-FLOW-IGNORE (D2m finding) closed by #101. Measured on main 51fcccd: CP1 11/19,
CP2 0/40 (X-33 OPEN), CP3 0/20; screens 11/107; journeys 9/53; BRD FR accepted 2/31 (FR-02, FR-09; tools/check_register.py).
