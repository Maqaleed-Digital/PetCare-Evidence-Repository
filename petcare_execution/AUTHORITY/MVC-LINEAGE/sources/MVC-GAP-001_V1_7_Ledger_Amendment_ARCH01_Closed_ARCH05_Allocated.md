# MVC-GAP-001 V1.7 — Ledger Amendment · ARCH-01 CLOSED · ARCH-05 ALLOCATED · Enumeration Defect Raised

| Field | Value |
|---|---|
| **Instrument ID** | MVC-GAP-001 |
| **Version** | **V1.7** — Ledger Amendment |
| **Date** | 31 August 2026 · Jeddah, KSA |
| **Amends** | V1.0 … V1.6. **V1.6 preserved unmutated.** |
| **Executed under** | `MVC-CLOSE-001 V1.1` (SHA-256 `27a07179d911e8ff885a5020dee4832ba9c939b1a9758cb0ad5207d4401c85bc`) — **recovered 31 Aug, now GOVERNING**. Writes **W2·W3·W4·W5·W6**. V1.2 is WITHDRAWN (superseded by the recovered V1.1). |
| **Status** | **DRAFT — pending Sponsor verdict.** Not ratified. |
| **Closes** | ARCH-01. Authorises no build. |

> **Custody note.** This amendment is issued under a **successor** procedure, not the procedure
> that governed the previous act. `MVC-CLOSE-001 V1.1` — cited by hash in the live ARCH-05
> register row — is **LOST** (custody defect `MVC-CUST-005`). See `MVC-CLOSE-001 V1.2` §1.

---

## 1 · Movement

| | |
|---|---|
| OPENING (frozen, V1.6) | **87** |
| CLOSED | **1** — ARCH-01 |
| NEW accepted | **1** — ARCH-05 |
| Released without gap effect | 0 — EV-26 (postdates the freeze; §5) |
| Partial-limb void, no row effect | 0 — ENG-12 limb 8 (§4) |
| **CLOSING** | **87** |

Arithmetic matches `MVC-CLOSE-001 V1.2` §6 exactly. **No S-1 stop condition fired.**

> ⚠️ **The closing figure 87 is a movement result, not an enumeration.** See §6 — the ledger's
> own occupancy table cannot currently enumerate 87 rows. The movement is sound; the enumeration
> is defective. These are different claims and are not conflated here.

---

## 2 · ARCH-01 — CLOSED. Both conditions evidenced

ARCH-01 required two conditions. V1.6 recorded Condition A as unmet. **It is now met.**

**Condition A — estate entry ratified and locked. MET.**
Read from the **Portfolio Decision Log (Immutable) register itself**, not from any document
citing it, per `MVC-CLOSE-001` P3.c:

| Field | Live value |
|---|---|
| Decision ID | `PGD-ARCH-01-OFFLINE-SEGMENT` |
| Status | **Ratified** |
| Immutable Lock | **YES** |
| Date Ratified | **2026-08-28** |
| URL | `https://app.notion.com/p/3cc3ed7dc1048139996ae9c2f09a6bbd` |

This satisfies P3.c *exactly as specified, date included*. The register's own note states, verbatim:

> "Gap ARCH-01 (canonical ledger MVC-GAP-001 V1.6, frozen at 87 open) now has BOTH closure
> conditions met: (a) this lock, and (b) the DS-1..DS-8 downstream record authored and traced at
> MVC-SPEC-001 V3.0 Annex H. The ledger amendment to MVC-GAP-001 V1.7 (87 → 86) is a separate
> outstanding act and is not effected by this row."

**Condition B — DS-1…DS-8 authored and traced. MET.**
`MVC-SPEC-001 V3.0` Annex H, with the clause → requirement → acceptance-criterion table intact.
`MVC-RUN-001 V1.0`: `DS_1_TO_DS_8 = 8/8 AUTHORED AND TRACED`. V1.6 §7 concurs.

**Ratified ruling closed against:** `PGD-ARCH-01-OFFLINE-SEGMENT` — *"Offline device-local sealed
audit segments are a permitted component of the one universal Governed Audit Chain under C-3 — no
waiver required; implementation mechanism delegated to the architecture specification."*

### 2.1 A superseded record, named
`MVC-RUN-001 V1.0` (30 Aug, 14:44) records `ARCH_01_CLOSURE_TRACE = CONDITION A … NOT MET` and
calls the lock the `NEXT_GENUINE_ACCEPTANCE_BOUNDARY`. **The lock was applied later the same day.**
That line of MVC-RUN-001 is **superseded by the register** and must not be re-cited as current.
The register outranks a document citing it. MVC-RUN-001 is otherwise unaffected and is preserved
unmutated.

### 2.2 One correction to the register's own note
The register note projects the amendment as **"87 → 86"**. That is correct for ARCH-01 in
isolation and does not account for ARCH-05 being allocated in the same amendment (§3).
**Net movement is 87 → 87.** The note is not wrong about ARCH-01; it is arithmetic taken before
ARCH-05 was allocated. Recorded so the two figures are not later read as a contradiction.

---

## 3 · ARCH-05 — ALLOCATED. New gap row

**Occupancy proven before allocation** (P2.a/P2.b), from V1.6 §6 *and* independently from V1.5 §6:
`ARCH- occupied 01–04 · next free 05`. **ARCH-05 unoccupied. No collision.**

```
ARCH-05   SEPARATION OF COMMERCIAL AND FISCAL RESPONSIBILITY
DISPOSITION = D-2R  SPLIT TAXPAYER RESPONSIBILITY
CLASS       = EXECUTION_BLOCKING

1 Veterinary transaction     Clinic is seller / taxpayer
2 Platform service           Maqaleed Digital is seller / taxpayer
3 Clinic ZATCA               Clinic responsibility; never discharged by MVC
4 Maqaleed ZATCA             Maqaleed Odoo KSA, under the BILL-001 carve-out
5 Clinic fiscal credentials  Not held by Maqaleed by default
6 Clinic ERP / e-invoicing   Replaceable external integration seam
7 Embedded payments          Future governed capability; routing must not
                             silently change seller / taxpayer identity
8 Managed ZATCA-as-a-service Future optional product; separate regulatory and
                             commercial authorisation; NOT core launch.
                             Entry cost pre-priced at MVC-BENCH-001 V1.1 B-1..B-4

CLOSES ON   REQ-FIN-G1..G3 + REQ-FIN-S1..S3 + REQ-UX-NTI-1..3 + REQ-PRD12-NS
            authored and traced in MVC-SPEC-001 V3.1,
            AND the Decision Log row locked (CP-1)
```

**Register row status.** `MVC-ARCH-05-TAXPAYER-BOUNDARY` **already exists** in the Portfolio
Decision Log at `Status = Proposed`, `Immutable Lock = NO`, created 2026-08-31
(`https://app.notion.com/p/3cd3ed7dc10481788f2bfadd49e39874`). **That write is already executed
and was NOT re-executed by this amendment.** The lock (CP-1) is a human act and is not taken by
drafting.

**Binds:** `ARCH-04` (marketplace — the seller-identity invariant must survive its release) and
`PRD-13` (movement ledger).

---

## 4 · ENG-12 limb 8 — VOIDED_BY_RE_SCOPE. No row effect

**Superseding authority:** Sponsor decision **D-2R**, recorded at
`MVC-ARCH-05-TAXPAYER-BOUNDARY` and benchmarked at `MVC-BENCH-001 V1.1`.

Limb 8 was the **client-platform capability decision** for ZATCA stamping on clinic transactions.
Under D-2R, MyVetiCare's role in the veterinary transaction is, verbatim from
`MVC-BENCH-001 V1.1`: *"NONE. Not taxpayer, not agent, not custodian, not intermediary."*
A capability decision about executing clinic ZATCA has no subject.

**Ledger effect: ZERO.** ENG-12 is an umbrella gap; limb 8 is a partial limb, not a whole row.
Per V1.3 §, ENG-12 *"closes only when EVERY limb below is discharged"*. Seven limbs were
discharged; limb 8 is now void rather than open. **ENG-12 itself is therefore now discharged on
all limbs — but is NOT closed by this amendment**, because closure requires a positive
re-verification of the seven discharged limbs against the re-scoped boundary, which is authoring
work not performed here. ENG-12 remains **OPEN**, pending that pass.

*Device-identity lifecycle is unaffected:* `ENG-13` remains OPEN and independent — device
authority is distinct from human authority, and Governed Audit Chain cryptography is untouched by
the ZATCA re-scope.

---

## 5 · EV-26 — released, corrected scope, zero gap effect

**Gap-count effect ZERO, proven not assumed.** `MVC-RUN-001 V1.0` allocated `EV-25..EV-44`
(next free `EV-45`) **after** the V1.6 freeze — V1.6 §6 records next-free as `EV-25`. An
identifier that postdates the freeze cannot be one of the 87 frozen rows. This is the decisive
proof, not EV-26's absence from V1.6 Annex B, which proves only sequence.

**Scope correction.** EV-26 was allocated as the ZATCA cryptographic stamp profile *"gating
ENG-12 limb 8 on BOTH platforms"*, on the assumption MyVetiCare might execute clinic ZATCA.
`MVC-BENCH-001 V1.1` withdrew that assumption on new evidence before custody. **EV-26 is
discharged according to its actual evidence-register state under the split-taxpayer disposition
and is NOT resurrected as a client-platform stamping question.** Any residual relevance is
confined to Maqaleed's own fee invoicing under the `BILL-001` carve-out — finance lane, not the
MyVetiCare product.

*`EV-27` (non-production environment) and `EV-28` (EGS-unit decommissioning) are unaffected by
this release and remain as allocated.*

---

## 6 · 🛑 NEW FINDING — the ledger cannot enumerate its own count (blocks classification)

**Raised under `MVC-CLOSE-001 V1.2` S-3.** This amendment **HALTS write W8** (four-class
classification of every remaining gap) and reports.

### 6.1 The defect
The §6 prefix-occupancy table — the ledger's own enumeration instrument — **under-sums the
frozen count by exactly 1, in two consecutive amendments**:

| Amendment | Table sum | Ledger frozen at | Delta |
|---|---|---|---|
| V1.5 | GOV 20 + PRD 15 + ENG 12 + REG 15 + OPS 8 + MKT 9 + SPEC 2 + ARCH 4 = **85** | **86** | **−1** |
| V1.6 | GOV 20 + PRD 15 + ENG 13 + REG 15 + OPS 8 + MKT 9 + SPEC 2 + ARCH 4 = **86** | **87** | **−1** |

Reproducible across both. Not a transcription slip.

### 6.2 The cause — an entire lane fell out of the enumeration instrument

**PROVEN, by ID-level trace through the register lineage.** The `ORG-` lane is a live gap
namespace that the V1.5 and V1.6 occupancy tables omit entirely.

**V1.0 — ORG is one of the register's own lanes.** The base register declares its lanes and
counts, and the total reconciles exactly on independent extraction:

| Lane | GOV | REG | PRD | MKT | ENG | OPS | **ORG** | Total |
|---|---|---|---|---|---|---|---|---|
| V1.0 declared | 9 | 12 | 8 | 9 | 11 | 7 | **5** | **61** |
| Independently extracted | 9 | 12 | 8 | 9 | 11 | 7 | **5** | **61** ✔ |

`ORG-01 … ORG-05`, under **§7 Lane ORG · Organisation and capability**.
*(V1.0's prose says "Six lanes" while its own table lists seven — a separate, minor internal
inconsistency in the base register, recorded here and not acted on.)*

**V1.1 — ORG explicitly confirmed still open**, verbatim:
> "All other gaps in MVC-GAP-001 V1.0 stand as written across lanes GOV, REG, PRD, MKT, ENG, OPS
> **and ORG**. Total open: 63 (61 − 1 closed + 3 new)."

V1.1 also allocated **`ORG-06`**.

**V1.2 — corrects the total to 64 and closes exactly one ORG row**, verbatim:
> "1.2 Adjudication — Reading B. The correct V1.1 total was 64, not 63." … "**ORG-06 is closed.**"

Leaving **`ORG-01 … ORG-05` open — five rows.**

**V1.3 → V1.6 — ORG disappears from the instrument.** Mentions of any `ORG-nn` identifier:

| Amendment | V1.1 | V1.2 | V1.3 | V1.4 | V1.5 | V1.6 |
|---|---|---|---|---|---|---|
| `ORG-` mentions | 2 | 2 | **0** | **0** | **0** | **0** |

Every one of V1.3–V1.6 records `CLOSED = 0`. **No ORG row was ever recorded as closed after
`ORG-06`.** Yet the prefix-occupancy table — introduced at V1.5 — has never contained the lane.

**The arithmetic does not close, in either direction:**
- Declared prefixes only: **86** ≠ 87 (short by 1).
- Declared prefixes + five open ORG rows: **91** ≠ 87 (over by 4).

**This directly violates the register's own count rule**, stated at V1.2 §1.2 and binding since:
> "Every revision carries an explicit ledger — opening balance, closures by ID, new gaps by ID,
> and closing balance — and **the arithmetic must be reconstructible from the IDs alone.**"

It is not currently reconstructible from the IDs alone. A `VET-` prefix (`VET-5`, `-6`, `-8`,
`-11`) also appears in the base register and is likewise undeclared in any occupancy table;
whether those are gap rows or requirement references is not determined here.

### 6.2b The reconciliation, run to the defect site — 61 → 87 does NOT close

Executed 31 Aug 2026 by ID, per the V1.2 §1.3 count rule. **The chain breaks at one identifiable
point.**

| Step | Opening | Closed | New | Closing | Source |
|---|---|---|---|---|---|
| V1.0 | — | — | — | **61** | V1.0 lane table (7 lanes incl. ORG 5) — extraction-verified |
| V1.1 | 61 | −1 (`GOV-10`) | +4 | **64** | V1.1 §2.4 as corrected by V1.2 §1.2 (Reading B) |
| V1.2 | 64 | −1 (**`ORG-06`**) | +5 (`GOV-12`·`GOV-14`·`REG-13`·`OPS-10`·`PRD-11`) | **68** | V1.2 §1.4 ledger, verbatim |
| **???** | **68** | **—** | **+5** | **73** | 🛑 **NO RECORDED AMENDMENT** |
| V1.3 | 73 | 0 | +9 | **82** | V1.3 §1 |
| V1.4 | 82 | 0 | +2 | **84** | V1.4 §1 |
| V1.5 | 84 | 0 | +2 | **86** | V1.5 §1 |
| V1.6 | 86 | 0 | +1 (`ENG-13`) | **87** | V1.6 §1 |

**🛑 DEFECT SITE: V1.2 closes at 68; V1.3 opens at 73.** Five gaps enter the ledger with no
closure record, no allocation record, and no amendment. Every subsequent figure — 82, 84, 86, 87 —
inherits it.

**This is the exact failure the count rule was adopted to prevent, and it recurred in the very
next revision.** V1.2 §1.3, verbatim:

> "**MVC-GAP-001 count rule.** Every revision carries an explicit ledger — opening balance,
> closures by ID, new gaps by ID, closing balance — and **the arithmetic must be reconstructible
> from the IDs alone.**"

**Second, independent inconsistency.** `ORG-06` is the *only* ORG row ever closed (V1.2).
`ORG-01…ORG-05` have no recorded closure in any revision, and every amendment from V1.3 onward
records `CLOSED = 0`. So five ORG rows are open by the ledger's own arithmetic — yet the
occupancy table omits the lane entirely. Declared-only **86 ≠ 87**; declared + 5 open ORG
**91 ≠ 87**. **The two errors do not cancel and are not the same error.**

### 6.3 Why this halts W8 and nothing else
- **W8 requires enumerating every remaining gap** to assign exactly one class. An instrument that
  cannot list its rows cannot classify them. Classifying 86 rows and reporting 87 would be a count
  reconciled by assumption — *"worse than a halted run"*.
- **W3 (ARCH-05) is unaffected and proceeded.** `ARCH- 01–04 / next free 05` is stated identically
  and independently in V1.5 and V1.6; ARCH-05 occupancy does not depend on the total.
- **W4, W5, W6 are unaffected and proceeded.** All are movement deltas on named rows.
- **The 87 movement figure stands.** Opening 87 is V1.6's own frozen assertion; the deltas are
  proven. The defect is in enumeration, not in movement.

### 6.4 Required before W8 can run
1. Determine the disposition of `ORG-01…ORG-05` — still open, silently folded into another lane,
   or closed without a ledger entry. **`ORG-06` is closed (V1.2); the other five have no recorded
   closure.** Establish `VET-*` status likewise.
2. **Reconcile the +5 at the V1.2→V1.3 boundary (68 → 73).** §6.2b has already run the chain to
   this point; the five identifiers that entered without a record must be named, or the opening
   balance of V1.3 corrected and every downstream figure restated.
3. Reissue the occupancy table with every live namespace declared, and prove `sum(table) = count`.
4. Only then classify.

*This is the same defect class the programme has already caught twice — phantom `OPS-08`/`OPS-09`
occupancy, and the `EV-25` double-proposal. It was found by the same method: sum the table, do not
trust it.*

---

## 7 · Carried unchanged

- **Classification (V1.5 §4/§5)** stands: CE-1 → SPEC-01 · CE-2/CE-3/CE-4 → SPEC-02 · audit
  partition → ARCH-04 · OPERATOR_ENTITY collision → PRD-15 · sole-practitioner bootstrap → PRD-14
  · INT-MVC-8 deferral granularity → SPEC-02 · marketplace intermediary → Annex B.
- **SPEC-02** retains all three named closure limbs: the DST impossible-test correction, the
  OUT-MVC-3 provisional trace, the OUT-MVC-5 provisional trace.
- **OPS-08 / OPS-09** remain unexplained. **No OPS identifier may be reused until established.**
- **RULE-C2 unchanged.** 246 requirements authored across three tranches. Authoring is not closure.

---

## 8 · Prefix occupancy after this amendment

**Issued with an explicit completeness caveat** — see §6. This table reproduces V1.6's declared
namespaces plus this amendment's change. It is **NOT** asserted to be a complete enumeration.

| Prefix | Occupied | Next free |
|---|---|---|
| GOV- | 01–20 | 21 — released (GOV-21 resolved without becoming a gap) |
| PRD- | 01–15 | 16 |
| ENG- | 01–13 | 14 |
| REG- | 01–15 | 16 |
| OPS- | 01–07, 10 | 08 — **blocked pending OPS-08/09 provenance** |
| MKT- | 01–09 | 10 |
| SPEC- | 01–02 | 03 |
| **ARCH-** | **01–05** | **06** |
| EV- | 01–44 | 45 |
| **ORG-** | **UNDETERMINED** | **BLOCKED — §6.2** |
| **VET-** | **UNDETERMINED** | **BLOCKED — §6.2** |

`sum(declared numeric namespaces) = 87` only if `ORG-` and `VET-` contribute zero live rows.
**That has not been proven and must not be assumed.**

---

## 9 · What this amendment does not do

It authorises no implementation, deployment, schema mutation, procurement or delivery tranche.
It does not classify the remaining gaps (**W8 halted, §6**). It does not close ENG-12, ENG-13,
SPEC-01, SPEC-02, or any PRD row. It takes no lock — CP-1 remains outstanding for ARCH-05.

MyVetiCare remains **SPECIFIED — NOT AUTHORIZED**. Runtime **DEPLOYED-BUT-NOT-SERVING**.
Gate 4 unreached.

*MVC-GAP-001 V1.7 · CLOSING 87 open · 31 August 2026 · Jeddah, KSA · DRAFT pending Sponsor verdict · This amendment closes ARCH-01 and authorises no build.*

---

# ANNEX A — ORG-LANE RECONCILIATION · V1.6 ENUMERATION REPAIR · HEADER-COUNT DISPOSITION

*Appended 31 Aug 2026 under `MVC-CLOSE-001 V1.1`. Traced by SUBJECT MATTER, not identifier search.*

## A.1 · Halt-code correction (recorded, not silently rewritten)

```
PRIOR_HALT_CODE             = S-3
CORRECTED_PRIMARY_HALT_CODE = S-1  (arithmetic non-reconciliation)
SECONDARY                   = S-3  (namespace enumeration defect)
SUBSTANTIVE_HALT_JUDGEMENT  = UNCHANGED
```

Confirmed by the governing instrument itself. `MVC-CLOSE-001 V1.1` §3.1 lists among S-1 triggers:
*"arithmetic irreconcilable from actual row movements"*; §10 defines S-3 as *"identifier collision
or unexplained occupied namespace."* Both fire; S-1 is primary.

## A.2 · ORG lane — fate of every row

| Row | Subject | Fate | Evidence |
|---|---|---|---|
| **ORG-01** | Single-founder bandwidth is the binding constraint | **C_DROPPED_WHILE_OPEN** | No subject-matter occurrence in V1.3–V1.6, RUN V1.0, SPEC V3.0 or BRD V3.1. Last proven open: **V1.2**. |
| **ORG-02** | No named Veterinary Clinical Lead exists | **C_DROPPED_WHILE_OPEN** | The **role** is now load-bearing — owner in SPEC V3.0 §S5.2, owner of a BRD V3.1 acceptance criterion, author of the INT-MVC-9 rule pack (RUN V1.0). **But the gap was the absence of a *named appointed person*, and no appointment is evidenced anywhere.** The role being specified as an owner makes the gap **more acute, not closed**. Last proven open: **V1.2**. |
| **ORG-03** | No reference-data licensing owner and no licence | **A_REKEYED_OR_ABSORBED → `EV-16`** | Near-verbatim on both distinguishing criteria. ORG-03: *"licensed formulary with verbatim-display rights and historical-version retention."* RUN V1.0 EV-16: *"A written drug-reference embedding licence — verbatim-display rights, territory, historical-version retention for the full retention period."* **COUNT_EFFECT: −1 gap row** (moves to the Annex B evidence register). |
| **ORG-04** | No Arabic-language clinical authoring capability | **C_DROPPED_WHILE_OPEN** | No subject-matter occurrence anywhere downstream. Last proven open: **V1.2**. |
| **ORG-05** | No Riyadh presence (largest share of private establishments) | **C_DROPPED_WHILE_OPEN** | ⚠️ **All 20 "Riyadh" hits downstream are `Asia/Riyadh` — the TIMEZONE**, in DST and deadline-arithmetic contexts. **Zero** concern market presence. A keyword search would have falsely closed this row. Last proven open: **V1.2**. |
| **ORG-06** | Amendment C-03 / eight Extensibility Constraints | **B_CLOSED_WITH_COUNTER_RECORD** | Closed explicitly at V1.2 §2.1 with evidence, and the constraints are now incorporated individually at BRD V3.1 §S2.7 / `REQ-MVC-2.12 [SOURCED — Extensibility Position v1.0 §6]`. Genuine closure. |

**`COUNT_CORRECTION_REQUIRED = YES` — four rows (`ORG-01`, `ORG-02`, `ORG-04`, `ORG-05`) are open
by the ledger's own record and appear in no occupancy table from V1.5 onward.**

## A.3 · The header count — THREE mutually inconsistent totals

Evidence wins; 87 is not preserved merely because downstream documents cite it, and not changed
merely because ORG identifiers vanished.

| Basis | Total | Derivation |
|---|---|---|
| **Recorded movements** | **82** | `61 −1 +4 −1 +5 +9 +2 +2 +1` across V1.0→V1.6 |
| **Declared occupancy table** | **86** | GOV 20 + PRD 15 + ENG 13 + REG 15 + OPS 8 + MKT 9 + SPEC 2 + ARCH 4 |
| **Header assertion (V1.6)** | **87** | "FROZEN at 87 open" |

Three defects, independent, non-cancelling:

1. **The +5 at the V1.2→V1.3 boundary.** V1.2 §1.4 closes at **68**; V1.3 §1 opens at **73**.
   Five identifiers entered with no closure record, no allocation record and no amendment.
   82/84/86/87 all inherit it.
2. **The occupancy table conflates two different quantities.** It reports *occupied identifiers*,
   not *open gaps*. `GOV-10` is **closed** (V1.1) yet its identifier occupies `GOV-01–20`.
   So 86 occupied ≠ 86 open.
3. **The ORG lane is absent from the instrument** while four of its rows remain open (§A.2).

**`TRUE_V1_6_FROZEN_ROW_COUNT` = NOT DERIVABLE FROM EVIDENCE.** Reconstructing the five
identifiers at defect 1 would be inventing history. The best-evidenced *lower bound* on open rows is:

```
declared occupied            86
− GOV-10 (closed, occupying)  −1   = 85
+ ORG-01, ORG-02, ORG-04, ORG-05 +4 = 89
(ORG-03 absorbed → EV-16; ORG-06 closed: neither adds)
```

**≥ 89**, against a header of **87** — and still unreconciled to the recorded-movement figure of 82.

## A.4 · Consequence — W8 stays halted, and why that is the correct outcome

`MVC-CLOSE-001 V1.1` **P1.a** requires *"Enumerate all 87 frozen rows."* **87 corresponds to no
enumerable set.** W8 requires classifying *every* remaining open row *exactly once*; a row set
contested by at least four rows cannot support that, and `PHASE_A_EXECUTION_READY` condition 1
("every internally resolvable EXECUTION_BLOCKING item is CLOSED") cannot be evaluated against an
unenumerated population.

Classifying 86 and reporting 87 would be a count reconciled by assumption. **The run halts at S-1.**

## A.5 · ⚠️ SECOND, INDEPENDENT BLOCKER — ARCH-02 may not be deferred

`MVC-CLOSE-001 V1.1` §11 required this run to prove or disprove the §7.2 platform-fee hypothesis.
**Tested. NOT disproved.**

- `MVC-SPEC-001 V3.0` Part E specifies **subscription and seat management inside MyVetiCare**
  (`REQ-MVC-8.83 [DESIGN-AUTHORITY]` — "the tenant lifecycle … the states after signup").
- `MVC-SPEC-001 V3.0` specifies an **invoice-type catalogue carrying the participant discriminator**.
- `MVC-BENCH-001 V1.1` routes the fee itself to Maqaleed KSA Odoo under the `BILL-001` carve-out.

V1.1 §7.2 permits deferral **only** if the fee-billing path is *proven wholly inside `BILL-001`*,
and states **"Do not defer by assumption."** It is not proven. If MyVetiCare emits invoice-type and
taxpayer attributes, those are an immutable data-model decision whose later correction would
restate issued-invoice history — barred by §6.1, therefore `EXECUTION_BLOCKING`.

**`ARCH-02` = EXECUTION_BLOCKING pending counsel.** This blocks `PHASE_A_EXECUTION_READY`
condition 5 **independently of the count question**, so resolving A.3 alone would not unblock
Phase-A. Question framed for counsel at `MVC-COUNSEL-001 V1.0` §1.

## A.6 · Required before W8 can run

1. **Name the five identifiers at the V1.2→V1.3 boundary**, or correct V1.3's opening balance and
   restate every downstream figure.
2. **Adjudicate `ORG-01`, `ORG-02`, `ORG-04`, `ORG-05`** — restore to the row set, or close each
   with evidence. They may not simply remain invisible.
3. **Reissue the occupancy table** separating *occupied identifiers* from *open rows*, declaring
   every live namespace, and proving `sum = count`.
4. **Counsel answer on ARCH-02** (A.5).

*Annex A · 31 August 2026 · DRAFT pending Sponsor verdict.*

---

# ANNEX B — SPONSOR ADJUDICATION · CURRENT ACTIVE GAP REGISTER · W8

*Appended 31 Aug 2026 under Sponsor adjudication of the S-1 arithmetic matter.*

## B.1 · Adjudicated legacy disposition — recorded verbatim

```
LEGACY_DECLARED_OPENING_TOTAL     = 87      (preserved as historical declared movement total ONLY)
LEGACY_OPEN_ROW_ENUMERATION       = UNRECONCILED
LEGACY_COUNT_CERTIFIABLE          = NO
UNRESOLVED_LEGACY_POPULATION_DELTA = 5      (V1.2→V1.3 boundary; NO identifiers invented)
S1_LEGACY_ARITHMETIC              = ADJUDICATED
```

Accepted as proven: the +5 boundary movement · `ORG-01/02/04/05` dropped while open ·
`ORG-03` absorbed into `EV-16` · `ORG-06` validly closed · **occupancy counts occupied
identifiers, not open rows.** No historical identifier is fabricated. `87` is **not** represented
as an enumerable open-row population anywhere from this amendment forward.

## B.2 · Reverse completeness sweep (Sponsor §11) — executed

Denominator: the current V3.x estate — **464 distinct requirement identifiers**
(443 `REQ-MVC-*` + 21 other) across `MVC-SPEC-001 V3.0` and `MVC-BRD-001 V3.1 CANDIDATE`.

A fully-specified requirement is **not** an obligation gap. The orphan test therefore runs over
requirements and clauses carrying an **unresolved marker** (`[EVIDENCE REQUIRED]`,
`EXTERNAL_EVIDENCE_REQUIRED`, `UNRESOLVED`, `NOT SPECIFIED`, `TBD`).

| Measure | Count |
|---|---|
| Unresolved-marker obligation lines | **179** |
| Method/provenance prose (not an obligation) | 4 |
| Owned by an identifier on the line | 112 |
| Owned by an identifier within ±3 lines | 55 |
| **Unowned (candidate orphans)** | **8** |
| **Mechanical coverage** | **95.5 %** |

### B.2.1 · ⚠️ Sweep self-correction — two false negatives found
Reading the orphans in context exposed a defect in the ±3-line heuristic itself: **`L8-A` (line 5446)
and `L8-D` (line 5452) are equally unallocated but were masked by unrelated identifiers
(`ENG-13`, `ARCH-02`) sitting within the window.** The true candidate set is the **five `L8-*`
items**, not the two the sweep first returned. *An instrument that can be wrong about which item is
unowned is not yet a control — recorded so the next run does not inherit the 95.5 % figure as safe.*

## B.3 · Disposition of every orphan — exactly one each

| # | Orphan | Disposition | Basis |
|---|---|---|---|
| 1 | SPEC L5061 — "Every such dependency is classified EXTERNAL_EVIDENCE_REQUIRED…" | **NOT_A_CURRENT_GAP** | Definitional statement of the classification method, not an obligation. |
| 2 | SPEC L5062 — "The classification column is a statement about the decision…" | **NOT_A_CURRENT_GAP** | Definitional. |
| 3 | SPEC L5535 — "seven settled, three EXTERNAL_EVIDENCE_REQUIRED…" | **owned → `ENG-12`** | The limb-8 twelve-row matrix summary; `ENG-12` is its owner. |
| 4 | BRD L86 — `[EVIDENCE REQUIRED]` has no equivalent in the ratified provenance-tag set | **CUSTODY_HYGIENE** | A governance-vocabulary defect: the document needs a tag the ratified set does not contain. Register correction, not a build obligation. |
| 5 | BRD L231 — "Telemedicine legality unresolved (§S6.2)" | **owned → `P2`** · RELEASE_BLOCKING | Telemedicine counsel. Fence per V1.1 §7.2. |
| 6 | BRD L787 — "Split and unresolved across MEWA, SFDA and MOMRAH" | **owned → `REG` lane** · RELEASE_BLOCKING | Veterinary-pharmacy/dispensing regulatory split. Named holders. |
| 7 | **`L8-A`** ZATCA cryptographic stamp algorithm · **`L8-B`** pilot device fleet inventory | **NOT_A_CURRENT_GAP — VOIDED_BY_RE_SCOPE** | Both exist solely to resolve `ENG-12` limb 8's hardware-key/stamping matrix. Limb 8 is **VOIDED** at §4 of this amendment under D-2R: MyVetiCare's role in the veterinary transaction is *"NONE. Not taxpayer, not agent, not custodian, not intermediary."* A ZATCA stamp algorithm and an EGSUnit device fleet have no subject once MVC never stamps. *(`L8-A` had additionally been allocated `EV-26` by `MVC-RUN-001 V1.0`, itself released at §5.)* |
| 8 | **`L8-C`** DataMatrix read rate on real packs · **`L8-D`** label printer transport/command language | **⚠️ GENUINE CURRENT OBLIGATIONS — see B.4** | **These are NOT ZATCA.** GS1 DataMatrix capture and dispensing-label printing are **clinical dispensing** capabilities. They do **not** die with limb 8's re-scope, and they carry no allocated Annex B identifier. |
| — | `L8-E` MDM acceptance / device ownership | **NOT_A_CURRENT_GAP** | The estate states verbatim: *"Does not block the determination."* |

## B.4 · 🛑 The reverse sweep found real orphans — `L8-C` and `L8-D`

Two current Phase-A dispensing obligations carry `[EVIDENCE REQUIRED]` and state, verbatim:
*"Annex B row required; **no identifier allocated here**."*

- **`L8-C`** — GS1 DataMatrix read rate on real medicine packs. **Unmeasured.** Determines whether
  barcode-driven dispensing verification is achievable at the point of care.
- **`L8-D`** — label printer transport and command language. **Unretrieved.** Determines whether a
  compliant dispensing label can be produced at all.

**Allocation is deliberately NOT performed by this amendment.** `MVC-RUN-001 V1.0` records that
Annex B allocation is *"a discrete act requiring an occupancy sweep"* and that the true next-free
identifier is **`EV-45`** — but the allocation record it produced (`mod_annexb.md`) **is not present
in the custody corpus**, so the occupancy state after `EV-44` cannot be verified from governed bytes.
Allocating `EV-45`/`EV-46` against an unverifiable occupancy state is exactly the `EV-25`
double-proposal defect this programme has already caught once.

```
ORPHAN_CURRENT_OBLIGATIONS      = 2   (L8-C, L8-D)
DUPLICATE_CURRENT_GAP_SUBJECTS  = 0
UNCLASSIFIED_CURRENT_OPEN_ITEMS = 0
CURRENT_ACTIVE_REGISTER_RECONSTRUCTIBLE = YES (for every item except L8-C/L8-D)
```

**Per Sponsor §13, `L8-C` and `L8-D` are EXECUTION_BLOCKING and W8 does not close.**
They are cheap to discharge — one occupancy sweep over the recovered `mod_annexb.md`, then two
allocations — but neither may be done on an unverifiable occupancy state.

**Consequently `UNRESOLVED_LEGACY_POPULATION_DELTA = 5` is NOT yet reclassified to
`CUSTODY_HYGIENE`** (Sponsor §12 requires no orphan to remain).

## B.5 · Current Active Gap Register — identified open subjects

Constructed from positively evidenced unresolved subjects only (Sponsor §6/§7).

| CURRENT_ID | Subject | Class | Owner | Phase-A effect | Reopening trigger |
|---|---|---|---|---|---|
| `ARCH-02` | Platform-fee fiscal boundary — narrowed | **EXECUTION_BLOCKING_NARROW** | tax counsel | only behaviour that changes if answer = YES | counsel answer |
| `ARCH-03` | MVC owns invoice semantics/idempotency/workflow/evidence; no ZATCA execution provider | EXECUTION_BLOCKING | architecture | re-direct pending | — |
| `ARCH-04` | Marketplace; bound by `REQ-FIN-S1..S3` | RELEASE_BLOCKING | architecture | fenced | marketplace release |
| `ARCH-05` | Split taxpayer responsibility | EXECUTION_BLOCKING | Sponsor | closes on CP-1 + `REQ-FIN-*` traced | **CP-1 lock** |
| `PRD-12` | No-show revenue owner | EXECUTION_BLOCKING | product | `REQ-PRD12-NS` authored, row open | reconcile appointment model |
| `PRD-13` | Gross-not-net movement ledger | EXECUTION_BLOCKING | product | `REQ-FIN-G1..G3` authored, row open | prove no net-as-sale write path |
| `PRD-14` | Sole-practitioner initial authority grant | EXECUTION_BLOCKING | product | unresolved | explicit grant decision |
| `PRD-15` | Operator console / `REQ-UX-8`,`-9` counterparts | EXECUTION_BLOCKING | product | corrections unfinished | — |
| `ENG-12` | Umbrella; 7 limbs discharged, limb 8 VOIDED | EXECUTION_BLOCKING | engineering | re-verify 7 limbs vs re-scope | re-verification pass |
| `ENG-13` | Device identity lifecycle | EXECUTION_BLOCKING | engineering | authored `REQ-MVC-8.86–8.116`, not closed | integration + testability |
| `SPEC-01` | Execution specification | EXECUTION_BLOCKING | spec | tranche 3 blocked by `ARCH-02` | ARCH-02 answer |
| `SPEC-02` | Integration domains `INT-MVC-5..8`, DST + provisional traces | EXECUTION_BLOCKING | spec | unresolved | ratified deferral applied |
| `L8-C` | GS1 DataMatrix read rate — **unallocated** | **EXECUTION_BLOCKING (orphan)** | engineering | dispensing verification | Annex B allocation |
| `L8-D` | Label printer transport — **unallocated** | **EXECUTION_BLOCKING (orphan)** | engineering | dispensing label | Annex B allocation |
| `P2` | Telemedicine legality | RELEASE_BLOCKING | regulatory | disabled by default; **no dormant schema** | counsel clearance |
| `REG-15` | Statutory filing discharge | RELEASE_BLOCKING | regulatory | filing state separate, non-terminal | determination |
| `REG` split | MEWA / SFDA / MOMRAH authority split | RELEASE_BLOCKING | regulatory | dispensing scope | determination |
| `EV-16` | Drug-reference licence (**ex `ORG-03`**) | RELEASE_BLOCKING | commercial | `EV16_DEPENDENT_CAPABILITY=DISABLED` + `REQ-SAF-F1..F3` | executed licence |
| `D-6` | Embedded-payment determination | GOVERNED_DEFERRED | regulatory | routing must not alter seller identity | payment proposal |
| `ORG-01` | Single-founder bandwidth | CUSTODY_HYGIENE | Sponsor | none | — |
| `ORG-02` | **No named Veterinary Clinical Lead appointed** | **EXECUTION_BLOCKING** | Sponsor | the role is load-bearing in SPEC §S5.2, BRD acceptance criteria and the `INT-MVC-9` rule pack — **an unappointed owner cannot sign off clinical thresholds** | named appointment |
| `ORG-04` | Arabic clinical authoring capability | RELEASE_BLOCKING | Sponsor | Arabic clinical strings must be authored, not translated | appointment |
| `ORG-05` | Riyadh presence | GOVERNED_DEFERRED | Sponsor | commercial, not build | month-4 hire |
| `OPS-08`/`OPS-09` | Unexplained occupancy | CUSTODY_HYGIENE | governance | **blocks all OPS identifier reuse** | provenance established |
| `LEGACY-DELTA` ×5 | Unidentified V1.2→V1.3 entries | CUSTODY_HYGIENE (**provisional**) | governance | none — **pending B.4** | orphan set = 0 |

```
IDENTIFIED_CURRENT_OPEN_ITEMS = 25 subjects (+5 unidentified legacy delta)
W8 = NOT CLOSED — 2 orphans (L8-C, L8-D) per Sponsor §13
```

*Annex B · 31 August 2026 · DRAFT pending Sponsor verdict.*
