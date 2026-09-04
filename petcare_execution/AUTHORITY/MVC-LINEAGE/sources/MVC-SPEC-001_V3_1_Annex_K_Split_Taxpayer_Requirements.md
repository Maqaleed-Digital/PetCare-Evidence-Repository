# MVC-SPEC-001 V3.1 — Annex K · Split-Taxpayer Requirement Groups (ARCH-05)

| Field | Value |
|---|---|
| **Instrument ID** | MVC-SPEC-001 |
| **Version** | **V3.1** — successor to V3.0. Create-only increment. |
| **Date** | 31 August 2026 · Jeddah, KSA |
| **Predecessor** | `MVC-SPEC-001 V3.0` (SHA-256 `a3f2fb2c2a4eb709187dccbee7f045a0b48e0d8364c4816de8f680e93b0a3a19`) — **incorporated by reference, preserved unmutated** |
| **Executed under** | `MVC-CLOSE-001 V1.2` (SHA-256 `2736ba03198c7ca4cefa9f9701e96bfd5e7b521945d415a9c3f98fa63fb9bbaf`), write **W7** |
| **Authority** | Sponsor decision **D-2R** (Split Taxpayer Responsibility), 30 Aug 2026 |
| **Status** | **DRAFT — pending Sponsor verdict.** Not ratified. |
| **Closes** | No gap. Authorises no build. |

> **Scope of this increment.** V3.1 = V3.0 **plus Annex K**. Tranches 1–3 of V3.0, including
> Annex H (DS-1…DS-8) and Annex I/J, are carried forward unchanged and are not restated here.
> This document adds the ten requirements on which `ARCH-05` closes.

---

## K.0 · Provenance and identifier occupancy

**Requirement texts.** Authored verbatim from `MVC-CLOSE-001 V1.0` §4 (SHA-256
`45f6a59138b1e3f781ff29d256cf4b8288d8982e27e8377050028bb28fcf6648`), which states of them:
*"All four derive from D-2R, which is settled; none depends on the content of MVC-SPEC-001 V3.0."*
They are propagated here, not re-derived.

**Independent corroboration.** The live Portfolio Decision Log row
`MVC-ARCH-05-TAXPAYER-BOUNDARY` names the same four groups as ARCH-05's closure conditions and
names **this** document as their destination: *"authored and traced in `MVC-SPEC-001 V3.1`."*

**Occupancy sweep executed before allocation** (per the standing discipline that caught the
`EV-25` collision). Swept against `MVC-SPEC-001 V3.0`, `MVC-BRD-001 V3.1 CANDIDATE` and
`MVC-RUN-001 V1.0`:

| Proposed ID | Result |
|---|---|
| `REQ-FIN-G1` · `G2` · `G3` | **FREE** — the `REQ-FIN-` namespace is entirely unoccupied |
| `REQ-FIN-S1` · `S2` · `S3` | **FREE** |
| `REQ-UX-NTI-1` · `-2` · `-3` | **FREE** — no clash with ratified `REQ-UX-{3,4,6,8,9,34,39}`; the `NTI` infix keeps the namespaces disjoint |
| `REQ-PRD12-NS` | **FREE** |

**10 allocations. 0 collisions.**

---

## K.1 · Gross-not-net — lands in PRD-13

> **REQ-FIN-G1** — Gross consideration is an immutable commercial fact. The recorded gross value
> of a clinic→owner transaction is the total consideration payable by the owner, exclusive of any
> platform fee, commission, payment cost, or deduction of any kind.
>
> **REQ-FIN-G2** — Platform fees, commissions, payment-processing costs, refunds, chargebacks and
> every other deduction are recorded as SEPARATE movements referencing the gross sale. They must
> never mutate, replace, or net against the recorded gross value.
>
> **REQ-FIN-G3** — Net settlement is a DERIVED value, computed as gross less referenced
> deductions. It is never stored as an authoritative fact.

**ACCEPTANCE.** For any transaction the recorded gross equals the value on the clinic's own
compliant tax invoice; AND no write path exists that reduces a stored gross value.
**Worked case:** `330.00` gross, `6.60` platform fee, `323.40` derived net — never `323.40` as
the sale.

**Anti-defer note.** This is the origin of `MVC-CLOSE-001` §6's TIE-BREAK rule. Storing a netted
value and correcting it later would require restating immutable ledger history. Cheap now,
unpayable later. **EXECUTION_BLOCKING by construction.**

---

## K.2 · Seller-identity invariant — lands in ARCH-05, binds ARCH-04

> **REQ-FIN-S1** — Seller / taxpayer identity is an attribute of the transaction record, set at
> creation from the clinic's own registration record, and immutable thereafter.
>
> **REQ-FIN-S2** — No payment, settlement, marketplace, or fee-collection component holds write
> authority over the seller-identity field. This is enforced structurally, not by convention or
> code review.
>
> **REQ-FIN-S3** — Payment routing, fund flow, and the identity of whichever party receives funds
> first must never determine or alter seller / taxpayer identity. The owner paying inside the
> application does not make Maqaleed the veterinary seller.

**ACCEPTANCE.** A build in which any payment-layer component can write the seller-identity field
FAILS. The test is a **static write-authority check**, not a runtime assertion.

**Binding on ARCH-04.** The marketplace release remains fenced; this invariant must survive its
eventual release. A future embedded-payments capability inherits `REQ-FIN-S3` unchanged.

---

## K.3 · NOT_A_TAX_INVOICE contract — lands in the owner-facing surface

> **REQ-UX-NTI-1** — Any owner-facing artefact displaying priced line items carries an explicit
> machine-readable and human-readable `NOT_A_TAX_INVOICE` designation.
>
> **REQ-UX-NTI-2** — Such an artefact must NOT: present VAT as a charge levied by the platform;
> carry a QR code, cryptographic stamp, invoice sequence number, ICV, PIH or clearance reference;
> or use the terms "tax invoice" / "simplified tax invoice" or their Arabic equivalents.
>
> **REQ-UX-NTI-3** — It must state that the clinic issues the tax invoice.

**ACCEPTANCE.** The artefact **fails ZATCA tax-invoice form on inspection.** Presence of any
prohibited element is a build failure. **A disclaimer alone does not satisfy this requirement.**

**Surface-class note.** This lands on the Customer Workspace instantiation, not on a new surface.
`REQ-UX-39` closes the portfolio surface-class set at four (GOV-21, resolved). No fifth class is
created or implied.

---

## K.4 · No-show revenue owner — lands in PRD-12

> **REQ-PRD12-NS** — Every no-show, late-cancellation or deposit-forfeiture charge carries an
> explicit revenue owner — CLINIC or PLATFORM — determined at scheme configuration time, not at
> charge time. A charge with no declared revenue owner cannot be raised.

**ACCEPTANCE.** No code path can raise a charge whose revenue owner is null, inferred, or
defaulted.

**Why configuration-time.** A charge-time determination would let fund routing decide revenue
ownership, which `REQ-FIN-S3` forbids. The two requirements are mutually reinforcing and must not
be implemented independently.

---

## K.5 · Trace — clause → requirement → acceptance criterion

| D-2R clause | Requirement | Acceptance criterion | Target module |
|---|---|---|---|
| 1 · Veterinary transaction — clinic is seller/taxpayer | `REQ-FIN-S1`, `S2`, `S3` | static write-authority check | ARCH-05 / ARCH-04 |
| 2 · Platform service — Maqaleed is seller/taxpayer for fees only | `REQ-FIN-S1` | identity set from registration record | ARCH-05 |
| 3 · Clinic ZATCA never discharged by MVC | `REQ-UX-NTI-1..3` | fails ZATCA tax-invoice form on inspection | owner-facing surface |
| 4 · Maqaleed ZATCA via `BILL-001` carve-out | *(finance lane — out of MyVetiCare scope)* | — | — |
| 5 · Clinic fiscal credentials not held by default | `REQ-FIN-S2` | no component holds write authority | ARCH-05 |
| 6 · Clinic ERP / e-invoicing = replaceable seam | *(carried in V3.0 integration tranche)* | — | SPEC-02 |
| 7 · Embedded payments must not change seller identity | `REQ-FIN-S3` | routing cannot alter identity | ARCH-04 |
| 8 · Managed ZATCA-as-a-service = future optional product | *(fenced; priced at BENCH V1.1 B-1..B-4)* | — | — |
| Gross-not-net (movement ledger) | `REQ-FIN-G1`, `G2`, `G3` | gross = clinic tax-invoice value; no reducing write path | PRD-13 |
| No-show revenue ownership | `REQ-PRD12-NS` | no null/inferred/defaulted revenue owner | PRD-12 |

**Clauses 4, 6 and 8 carry no new requirement here by design** — 4 is the finance lane under
`BILL-001`, 6 is already specified in V3.0's integration tranche, and 8 is a fenced future
product requiring separate regulatory and commercial authorisation.

---

## K.6 · What this increment does not do

**It does not close ARCH-05.** Per the live register row, ARCH-05 closes on these requirements
being *authored and traced* **AND** the Decision Log row being locked at **CP-1** — a human act,
not taken by drafting.

**RULE-C2 applies unchanged.** Authoring is not closure. With these ten, **256 requirements** have
now been authored across the completion passes, and the count of gaps closed by authoring alone
remains **zero**. A specification gap closes when the specification is complete and integrated
into a candidate that passes reconciliation.

It authorises no implementation, deployment, schema mutation, procurement or delivery tranche.
MyVetiCare remains **SPECIFIED — NOT AUTHORIZED**. Runtime **DEPLOYED-BUT-NOT-SERVING**.
Gate 4 unreached.

*MVC-SPEC-001 V3.1 · Annex K · 31 August 2026 · Jeddah, KSA · DRAFT pending Sponsor verdict · Closes no gap, authorises no build.*
