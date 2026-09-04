# MVC-BRD-001 V3.2 — MyVetiCare Execution Baseline Candidate

**Class.** Execution baseline candidate. This document tells engineering what to build.
**Status.** DRAFT — non-authorising. `PHASE_A_EXECUTION_READY` is CP-2, a Sponsor act, and is
**not taken here**. Nothing in this document is ratified.
**Relationship to V3.1.** V3.2 **incorporates MVC-BRD-001 V3.1 CANDIDATE's requirement text by
reference** for every included requirement, and governs only where the two conflict. V3.1 is a
**normative annex**, not a discarded predecessor — V3.2 states invariants, scope and fences; V3.1
carries the requirement bodies. An engineer needs both. *(RT-003 RT-01.)*
**Date.** 31 August 2026 · Jeddah, KSA

**Standing rule carried forward (RULE-C2).** Authoring is not closure. Every gap open in
MVC-GAP-001 V1.7 remains open. This document changes no gap count.

---

## §0 · Document control and how to read this

V3.2 differs from V3.1 in kind, not degree. V3.1 was a *specification*: it recorded what is known,
what is not, and where the estate is unsound. V3.2 is an *execution contract*: for the Phase-A
included subset it states what shall be built, and for everything else it states explicitly that it
shall not be built and what would reopen it.

Three reading rules:

1. **Included means buildable without a further product decision.** If a requirement is in the
   Phase-A included set, an engineer may implement it without asking what it means. Where that was
   not achievable the requirement is fenced, not softened.
2. **Fenced means unreachable, not absent.** A fenced capability keeps its data-model seam so that
   enabling it later is a configuration and migration act, never a redesign. Each fence carries an
   unreachability acceptance test — a fence nobody tests is a plan, not a fence.
3. **Nothing here asserts a Saudi regulatory fact the estate does not hold.** Where a behaviour
   depends on such a fact, the fact is named, its evidence identifier is cited, and the dependent
   behaviour is disabled.

```
CURRENT_REQUIREMENT_TRACE_COVERAGE = 100%          (495/495 identifiers, computed — see §40)
CURRENT_REQUIREMENTS_COMPLETE      = NOT ESTABLISHED
```
The denominator excludes the metavariable `REQ-MVC-n`, which is notation, not an identifier.
⚠️ **These are different claims.** Trace coverage proves every identifier resolves into a section.
It does **not** prove each requirement's *content* is expressed here — that requires a
requirement-by-requirement content review which has not been performed. Do not report the second on
the strength of the first. *(RT-003 RT-02.)*

---

## §1 · Product definition

MyVetiCare is a **standalone veterinary clinical and commercial platform owned by Maqaleed
Digital**. It is not a component of maqaleed.ai. It consumes platform services only through
explicit, replaceable service contracts, and separation is evidenced rather than claimed
(REQ-MVC-2.7, REQ-MVC-2.8a Tier-1/Tier-2 provider taxonomy).

It serves three parties with different interests and different authority:

- the **clinic**, which delivers veterinary care, holds the professional licence, and is the seller
  and taxpayer of the veterinary transaction;
- the **animal owner**, who receives care, holds records about their animal, and pays the clinic;
- **Maqaleed Digital**, which supplies the platform, is the seller and taxpayer of the *platform
  service*, and never becomes a party to the veterinary transaction.

The product's value is that the clinical record it produces is **evidence** — attributable,
attested, tamper-evident, and durable across offline operation — not merely data entry.

---

## §2 · Phase-A scope — what shall be built

Phase A delivers a single-clinic-tenant veterinary practice system with a governed evidence spine
and the commercial seam for platform billing. Included:

| Area | Included in Phase A |
|---|---|
| Tenancy | governed-participant model, audit partitioned from the first migration |
| Identity & authority | staff roles, professional authority, sole-practitioner bootstrap |
| Clinical | owner/animal records, consultation, clinical note, allergy, vaccination, lab result |
| Appointments | scheduling, check-in, the seven-state lifecycle incl. degraded operation |
| Medication | prescription authoring, deterministic dose arithmetic |
| Dispensing | dispensing record, wastage, inventory movement |
| Evidence | audit chain, attestation, offline segments, device identity and sealing |
| Commercial | invoice-supporting source facts, seller/taxpayer identity, gross-not-net |
| Platform billing | handoff to BILL-001; MyVetiCare never issues a clinic tax invoice |
| Operator | Platform Operations Workspace with read/mutate separation |
| Surfaces | clinic, owner, operator; Arabic-first |

**Explicitly NOT Phase A**, and fenced in §3: telemedicine, drug-reference screening, marketplace
transactions, payment processing, regulatory filing, ARCH-02-dependent tax treatment.

---

## §3 · Fenced and release-blocked scope

Every fence carries all seven fields. A fence without an unreachability test is not a fence.

### F-1 · Remote consultation / telemedicine
```
FEATURE                      Remote consultation, Specialist Consult pattern
STATE                        DISABLED
OWNER                        Sponsor + telemedicine counsel
DEPENDENCY                   P2 — KSA veterinary telemedicine lawfulness (EV-01)
REOPEN_TRIGGER               Written counsel opinion stating lawfulness and any attaching conditions
DATA_MODEL_SEAM              Consultation.modality enum retains REMOTE; no row may carry it in Phase A
UNREACHABILITY_ACCEPTANCE_TEST  Creating a consultation with modality=REMOTE fails closed at the
                             service boundary, in every environment, and the attempt is audited
```

### F-2 · Drug-reference / interaction screening
```
FEATURE                      Interaction and duplicate-therapy screening (INT-MVC-3, INT-MVC-4)
STATE                        DISABLED
OWNER                        Maqaleed Digital commercial + Sponsor
DEPENDENCY                   EV-16 — licensed drug reference, THREE limbs: (i) written licence,
                             (ii) verbatim-display rights + territory + historical-version
                             retention, (iii) the source's severity band definitions
REOPEN_TRIGGER               All three limbs held. A licence without the taxonomy leaves INT-MVC-4
                             licensed and unconfigurable — it does not reopen the fence
DATA_MODEL_SEAM              Screening result entity exists, unpopulated; no UI path reaches it
UNREACHABILITY_ACCEPTANCE_TEST  No prescribing surface renders a screening verdict, and the
                             clinical-absence disclosure of §24 is asserted present on every
                             prescribing screen
```

### F-3 · Marketplace transactions
```
FEATURE                      Partner ordering, settlement, platform fee capture
STATE                        DISABLED for transaction; ARCHITECTURE REQUIRED in Phase A
OWNER                        Sponsor
DEPENDENCY                   ARCH-04 release conditions; EV-24, EV-38 counterparty lawfulness
REOPEN_TRIGGER               Counterparty class determination + ARCH-04 release gate
DATA_MODEL_SEAM              Governed-participant audit partitioning and seller-identity invariants
                             are built in Phase A from the first migration — see §6 and §16
UNREACHABILITY_ACCEPTANCE_TEST  No order may reach an executable state; the partition invariant is
                             asserted by a test that attempts a cross-participant write and fails
```

### F-4 · Payment processing
```
FEATURE                      Card/wallet capture, settlement to clinic
STATE                        DISABLED
OWNER                        Sponsor + payment-regulatory determination
DEPENDENCY                   D-6
REOPEN_TRIGGER               Payment-regulatory determination recorded in the Decision Log
DATA_MODEL_SEAM              Payment record entity exists; the payment layer is PROHIBITED from
                             mutating seller identity or invoice totals (§16, §19)
UNREACHABILITY_ACCEPTANCE_TEST  A write from the payment layer to seller identity or to a gross
                             amount is rejected and audited
```

### F-5 · Regulatory filing / notifiable disease submission
```
FEATURE                      Statutory notification submission (INT-MVC-2)
STATE                        DISABLED
OWNER                        MEWA determination
DEPENDENCY                   EV-07 notifiable-disease enumeration; REG-15
REOPEN_TRIGGER               The enumeration and the submission interface are both produced
DATA_MODEL_SEAM              Notifiable flag on the clinical record; no transmission path built
UNREACHABILITY_ACCEPTANCE_TEST  No outbound call to any regulator endpoint exists in the build
```

### F-6 · ARCH-02-dependent tax treatment
```
FEATURE                      Any additional product-layer tax treatment beyond the §16 baseline
STATE                        DISABLED
OWNER                        ZATCA / tax counsel
DEPENDENCY                   ARCH-02 — EXECUTION_BLOCKING_NARROW
REOPEN_TRIGGER               Counsel answer to the narrowed question in MVC-COUNSEL-001
DATA_MODEL_SEAM              See §16. The immutable baseline is settled and is NOT contingent on
                             the answer; only the additional treatment is fenced
UNREACHABILITY_ACCEPTANCE_TEST  No tax computation exists in MyVetiCare beyond recording the
                             seller/taxpayer discriminator
```

**Load-bearing note on F-6.** ARCH-02's residue must not be allowed to block the build. §16's
baseline is immutable and independent of the counsel answer. If — and only if — a YES answer would
alter the *base transaction schema*, the affected schema decision stays EXECUTION_BLOCKING; on the
evidence available it does not, because the discriminator is recorded either way.

---

## §4 · Personas and authority model

Four staff roles, a closed set (REQ-MVC-8.10 family). `PHARMACY_OPERATOR` is **deliberately absent**
— PRD-09/§S2.6 has not decided whether it is a staff permission, a counterparty class, or a held
seam. **Adding it is a Sponsor product act and may never arrive as a role-catalogue migration.**

A veterinary nurse/technician grade is **not admitted**: whether such a grade exists in KSA with
statutory clinical authority is not established. No such role is created and no regulated act is
delegated to one.

**Acceptance — fails if:** the role enumeration accepts a value outside the closed set; a role is
added by data rather than by a migration carrying a Sponsor-decision reference; or
`PHARMACY_OPERATOR` appears in any environment.

---

## §5 · Surfaces

Clinic, owner, operator and partner surfaces follow the S1–S8 surface grammar and the seven-state
lifecycle including degraded operation. **Arabic-first** (§S4.5): Arabic is the primary language of
the clinical and owner surfaces, not a translation layer.

⚠️ **Arabic scope discipline.** Arabic/RTL is a *product* requirement of the surfaces and, where
EV-15 establishes it, of the dispensing label's **content**. It is **not** a platform discriminator
for the label *transport* — see §13.

---

## §6 · Tenancy and governed-participant model

- Every row that can be attributed to a participant carries the participant discriminator.
- **Audit partitioning exists from the first migration**, not as a later hardening step. This is
  the single most expensive invariant to retrofit and the reason implementation A was chosen (see
  MVC-IMPLEMENTATION-BASELINE-001 §3).
- Tenant identity derives from **verified server-side identity only**. It may never be taken from a
  client-supplied header or any client-controlled value.
- Row-level isolation is necessary but not sufficient; the tenant predicate must itself be
  trustworthy.

**Acceptance — fails if:** any tenant-scoped read or write resolves its tenant from request-supplied
data; or a cross-participant write succeeds in any environment.

---

## §7 · Clinical workflows · §8 Appointments · §9 Medical records

Consultation, clinical note, allergy record, vaccination record, lab result and UPHR document form
the clinical spine. The **Draft / Attested** convention (§S4.3) is what makes the record evidence:
a draft is mutable and carries no evidentiary weight; attestation binds the record to a professional
identity at a point in time and is thereafter append-only.

Appointments carry the seven-state lifecycle with degraded operation mapped, so that a clinic that
loses connectivity continues to work and reconciles afterwards (§25).

**Acceptance — fails if:** an attested record can be mutated in place; or an attestation can be
recorded against an identity that did not hold professional authority at that time (§28).

---

## §10 · Medication and prescription · §11 Pharmacy, inventory, dispensing

Prescription authoring is Phase A. **Deterministic dose arithmetic is Phase A** and is independent
of EV-16 — it computes from body weight, concentration and a prescribed rate, and it involves no
reference corpus.

Dispensing records the event, the dispenser, the quantity, the inventory movement, and wastage with
witness. Two acts are **deliberately unclassified** because classifying them requires a regulatory
fact the estate does not hold:

- *whether a non-veterinarian may lawfully dispense a veterinary medicine in KSA, and under what
  supervision* — carried by PRD-14;
- *witness qualification for wastage* — carried by PRD-14 / REQ-MVC-7.35.

Until those resolve, both acts are restricted to the veterinarian role. **That is a fail-closed
default, not a determination.**

### §11.1 · REQ-DISP-AUTH-FAILCLOSED — dispensing authority fails closed *(NORMATIVE)*

> **REQ-DISP-AUTH-FAILCLOSED.** For every dispensing action whose professional-authority class is
> absent, unknown, unclassified, or not explicitly authorised by a ratified authority rule, the
> system SHALL permit execution only by an actor whose verified professional class is
> `VETERINARIAN`. It SHALL reject execution by any other actor class — including nurse, assistant,
> technician, receptionist, pharmacy operator, customer, owner and platform operator — and SHALL
> reject execution where the actor's professional class cannot be established. Professional class
> SHALL be derived from verified server-side identity and SHALL NOT be inferred from a UI role
> name, a request header, or any other client-controlled value.

**Why this is normative and not a note.** ORG-02's reclassification to `RELEASE_BLOCKING` (§41)
holds *only* while this default holds. Left as prose it is unenforceable — and
MVC-IMPL-FINDINGS-001 §P0-3 shows the current implementation does the **opposite**: dispensing
requires `PHARMACY_OPERATOR`, a role V3.2 §4 says must not exist, and a veterinarian is denied.

**ACCEPTANCE — five negative controls, each of which must be demonstrated FAILING before it is
reported passing:**

| Test | Actor / condition | Required result |
|---|---|---|
| `T-DISP-01` | `VETERINARIAN` + classified permitted act | governed result — ALLOW |
| `T-DISP-02` | `VETERINARIAN` + currently unclassified act | ALLOW, under the explicit veterinarian fallback only |
| `T-DISP-03` | non-veterinarian (incl. `PHARMACY_OPERATOR`) + unclassified act | **DENY** |
| `T-DISP-04` | actor professional class unknown / unresolvable | **DENY** |
| `T-DISP-05` | authority metadata missing on the action | **DENY** |
| `T-DISP-06` | client asserts professional class via header/body | **DENY server-side** |

**Build fails if** any dispensing path authorises on a client-asserted class, or if any
non-veterinarian class is permitted an unclassified dispensing act without a ratified authority
rule naming it.

```
ORG02_FAIL_CLOSED_REQUIREMENT_ID = REQ-DISP-AUTH-FAILCLOSED
ORG02_NEGATIVE_TEST_IDS          = T-DISP-03, T-DISP-04, T-DISP-05, T-DISP-06
ORG02_BUILD_FAIL_INVARIANT       = YES
```

---

## §12 · Medicine identification — the EV-39 / EV-41 boundary

**This section exists to prevent a specific, expensive error.**

```
EV-39  EXTERNAL · UNRESOLVED · owner SFDA
       Whether GS1 DataMatrix is the MANDATED carrier symbology for veterinary medicines in KSA,
       and whether unit-level serialisation is required at a clinic node.
       Closure requires the SFDA track-and-trace (RSD) instrument.
       It expressly DOES NOT close on observing DataMatrix on packs in circulation —
       that evidences practice, not a mandate.

EV-41  INTERNAL · UNRESOLVED · owner the programme
       A measured first-attempt read rate on real packs the practices stock, under clinic
       lighting, on the fleet devices of EV-40, per candidate client platform, against a pass
       bar stated BEFORE the run.
```

**Binding sequencing: EV-39 is retrieved before EV-41 is run.** Measuring a read rate for a
symbology that is not the mandated one proves nothing and consumes the design-partner relationship.

**Therefore the capture path is specified parametrically.** Engineering shall build a symbology-
agnostic capture interface with the concrete symbology bound by configuration at EV-39 closure.
**No requirement in Phase A may hard-code GS1 DataMatrix.**

Scope note carried from the register: EV-41 constrains a **PWA** determination for the dispensing
surface and does not constrain a native one.

**Acceptance — fails if:** any Phase-A artefact names a specific symbology as settled; or an
acceptance criterion is recorded as met on a read-rate result obtained without a pre-stated pass bar,
on generated test symbols, or on one device class generalised to the fleet.

---

## §13 · Label printing — the EV-42 boundary

```
EV-42  EXTERNAL · UNRESOLVED · owner the printer vendor's published specification,
       with the programme's printer selection as an internal precondition
       Per model: transport (network / BLE / classic Bluetooth / USB), command language,
       whether it accepts a raster payload at label resolution, and — where iOS hardware is in
       scope — accessory-programme participation.
```

⚠️ **Arabic rendering is NOT a discriminator here, and must not be introduced as one.** Thermal
printers perform no contextual shaping and no bidi reordering. The conformant construction is to
render the label as a **raster** and send the bitmap; a browser engine and a native text engine both
do that correctly. The limb-8 matrix Row 5 discriminates on **transport and dialog-free issuance
only**. Whether Arabic is mandatory on the label's *content* is a separate legal question owned by
**EV-15**.

Engineering shall build a **hardware abstraction boundary**: a label-render stage producing a raster
at label resolution, and a transport stage selected by configuration. Print-success acknowledgement,
retry and error behaviour are Phase A; the concrete driver is bound at EV-42 closure.

**Acceptance — fails if:** the label path depends on the printer performing text shaping; or a
printer model is hard-coded; or a successful desktop-driver print is offered as evidence, which
exercises a different path.

---

## §14 · Marketplace · §15 Commercial model

Marketplace *architecture* is Phase A (§3 F-3); marketplace *transactions* are fenced. Governed-
participant audit partitioning and the seller-identity invariants are built now because retrofitting
them is a rebuild.

---

### §15.1 · No-show, late-cancellation and deposit forfeiture *(NORMATIVE — REQ-PRD12-NS)*

> **REQ-PRD12-NS.** Every no-show, late-cancellation or deposit-forfeiture charge SHALL carry an
> explicit revenue owner — `CLINIC` or `PLATFORM` — determined at **scheme configuration time**,
> never at charge time. A charge with no declared revenue owner SHALL NOT be raised.

`REVENUE_OWNER` is never null, never inferred, never silently defaulted.

**Why configuration-time.** A charge-time determination would let fund routing decide revenue
ownership, which REQ-FIN-S3 forbids. REQ-PRD12-NS and REQ-FIN-S3 are mutually reinforcing and
must not be implemented independently.

**ACCEPTANCE — fails if:** any code path can raise a charge whose revenue owner is null, inferred
or defaulted; or if revenue ownership is resolved at charge time.

---

## §16 · Seller/taxpayer separation — the immutable baseline

**This is settled and is not contingent on ARCH-02.**

```
VETERINARY TRANSACTION      seller / taxpayer = THE CLINIC
PLATFORM SERVICE            seller / taxpayer = MAQALEED DIGITAL
MAQALEED'S OWN ZATCA        BILL-001 / Odoo KSA  — outside MyVetiCare
CLINIC ZATCA EXECUTION      OUTSIDE MyVetiCare
CLINIC FISCAL CREDENTIALS HELD BY MVC   = NO
```

MyVetiCare owns: commercial transaction semantics, seller/taxpayer identity, invoice-supporting
source facts, idempotency, workflow and evidence state, and routing of the platform-service charge
to BILL-001. MyVetiCare does **not** own clinic ZATCA execution and does **not** hold clinic fiscal
credentials.

**Invariants, each independently testable — with the negative control that proves it:**

| # | Invariant | Negative control | Must |
|---|---|---|---|
| 1 | Seller identity derives from the transaction's nature, never from payer, surface or payment instrument | `T-SELL-01` create a clinic transaction paid in-app by the owner | seller resolves **CLINIC**, not Maqaleed |
| 2 | The payment layer **cannot write** seller identity or a gross amount | `T-SELL-02` a payment-layer component attempts the write | **REJECTED** — and per Annex K §K.2 this is a **static write-authority check**, not a runtime assertion |
| 3 | Seller identity on a completed transaction is **immutable** | `T-SELL-03` attempt to update seller identity post-completion | **REJECTED**; correction only by a new record |
| 4 | Gross is never stored net | `T-SELL-04` attempt to persist an amount net of a platform fee | **REJECTED** |

`T-SELL-02` and `T-SELL-03` are **ARMED negative controls** — demonstrate each firing against a
planted defect before reporting either as passing.

---

## §17 · Gross-not-net

Amounts are recorded **gross**. A platform fee is a separate, separately-attributed record. Netting
at the point of record destroys the clinic's own revenue truth and is prohibited.

**Acceptance — fails if:** any stored amount on a veterinary transaction is net of a platform fee;
or the platform fee cannot be removed without recomputing the clinic's revenue.

---

## §18 · Platform billing handoff · §19 Payment future seam · §20 Refunds and credit notes

Platform charges route to BILL-001.

**Refund and credit-note semantics.** In Phase A a clinic-issued veterinary transaction adjustment
remains the **clinic's** fiscal responsibility. MyVetiCare records the commercial and clinical
adjustment and **SHALL NOT issue the clinic's fiscal credit note**. A credit note is a new
evidentiary record referencing the original, never an edit; the original record and the seller
identity on it are preserved. Any future routed payment reversal (fenced, F-4) SHALL NOT rewrite
seller identity or recorded gross consideration, and platform-fee reversal remains a separately
modelled movement.

**The owner-facing artefact — normative:**

> **REQ-UX-NTI-1** — Any owner-facing artefact displaying priced line items SHALL carry an explicit
> machine-readable and human-readable `NOT_A_TAX_INVOICE` designation.
>
> **REQ-UX-NTI-2** — Such an artefact SHALL NOT: present VAT as a charge levied by the platform;
> carry a QR code, cryptographic stamp, invoice sequence number, ICV, PIH or clearance reference;
> or use the terms "tax invoice" / "simplified tax invoice" or their Arabic equivalents.
>
> **REQ-UX-NTI-3** — It SHALL state that the clinic issues the tax invoice.

**ACCEPTANCE.** The artefact **fails ZATCA tax-invoice form on inspection**. Presence of any
prohibited element is a build failure. **A disclaimer alone does not satisfy this requirement.**
It lands on the Customer Workspace instantiation; no fifth surface class is created (REQ-UX-39).

---

## §21 · Telemedicine fence · §22 Regulatory filing fence · §23 Drug-reference fence

See §3 F-1, F-5, F-2 respectively.

---

## §24 · Clinical-absence disclosure — binding

`REQ-SAF-F1`, `REQ-SAF-F2`, `REQ-SAF-F3` are binding in Phase A.

**The system must never imply that licensed drug-interaction or reference screening occurred when it
did not.** Because deterministic dose arithmetic *is* available and screening is *not*, the surface
must distinguish them explicitly:

```
DOSE_CALCULATION_AVAILABLE      = YES
DRUG_REFERENCE_SCREENING_AVAILABLE = NO   (until EV-16 all three limbs are held)
```

This is more load-bearing, not less, because the canonical implementation ships an AI copilot
substrate: a clinician who sees machine-generated clinical text is *more* likely to assume screening
occurred.

**Acceptance — fails if:** any prescribing surface renders without the disclosure; or any AI-
generated clinical output is presented without it; or the disclosure can be dismissed persistently.

---

## §25 · Offline evidence architecture · §26 Audit and evidence chain

Offline segments, sealed-unsynchronised receipts, and fork/gap/replay evidence. A clinic operating
offline produces evidence that is verifiable on reconnection; a gap in the chain is **detectable and
reportable**, never silently healed. A clinic must be able to see whether its own audit chain
verified (REQ-UX-9 counterpart).

---

## §27 · Device authority

```
Enrolment            is NOT authorisation to seal.
Sealing authority    is granted separately and explicitly.
Withdrawal           is PROSPECTIVE ONLY.
Previously valid anchored evidence is NEVER destructively deleted.
```

Device identity, enrolment, sealing authorisation, withdrawal, revocation, lost/stolen state,
sealed-unsynchronised receipt, retention and classification are Phase A (ENG-13). Hardware-backed
key storage is a property of a **device**, not of an OS version — no requirement may be recorded as
verified on a capability a subset of the fleet lacks (EV-40).

**Negative controls — each invariant above is prose until one of these exists:**

| Control | Attempt | Must |
|---|---|---|
| `T-DEV-01` | an **enrolled but unauthorised** device attempts to seal | **DENY** — enrolment is not authorisation |
| `T-DEV-02` | verify evidence sealed **before** an authority withdrawal | still **VALID** — withdrawal is prospective only |
| `T-DEV-03` | any code path attempts destructive deletion of anchored evidence | **REJECTED** |
| `T-DEV-04` | a device whose class lacks hardware-backed key storage is marked verified | **REJECTED** (EV-40) |

`T-DEV-01` and `T-DEV-03` are **ARMED negative controls**.

---

## §28 · Professional authority

Human/professional authority is **separate from device sealing authority** and must not be conflated.
Sole-practitioner initial authority grant is specified (PRD-14): a one-vet practice must be able to
bootstrap without a second PRINCIPAL, and the bootstrap is a recorded act, never a silent exception.

**Negative controls:**

| Control | Attempt | Must |
|---|---|---|
| `T-PROF-01` | attest a clinical record as an identity that did **not** hold professional authority at that time | **DENY** |
| `T-PROF-02` | derive professional authority from a device's sealing authority | **DENY** — the two are separate |
| `T-PROF-03` | sole-practitioner bootstrap executed | **ALLOWED and RECORDED** in the audit trail; never silent |
| `T-PROF-04` | professional class asserted by client header or body | **DENY server-side** |

`T-PROF-01`, `T-PROF-02` and `T-PROF-04` are **ARMED negative controls**.

---

## §29 · Operator console — Platform Operations Workspace

**Not the Executive Center.** Maintains: read vs mutate permission separation; pre-state and
post-state on every mutation; a synthetic-vs-real scope marker; provenance and evidence visibility.

**Acceptance — fails if:** a mutate control is rendered to a read-only actor. Not disabled —
**not rendered**.

---

## §30 · Background jobs · §31 Notifications · §32 APIs and integration contracts

Integration contracts INT-MVC-1..9. INT-MVC-2/3/4 are fenced (§3). The INT-MVC-9 inclusion-rule
class remains a **Sponsor act** and is isolated to that decision; it does not block unrelated
SPEC-02 content.

---

## §33 · Security and access control · §34 Privacy

Deny-by-default. Authorisation is server-side and derived from verified identity. Purpose limitation
is a first-class binding (PDPL). Animal health data linkable to an identified owner is treated as
personal data pending EV-21.

---

## §35 · Observability · §36 Compatibility and migration

Migration invariants: audit partition present in the first migration; seller identity non-nullable
on every commercial record; no destructive deletion of anchored evidence; every migration reversible
or explicitly recorded as irreversible with a Sponsor reference.

---

## §37 · External authority dependencies · §38 External commercial dependencies

```
ARCH-02  ZATCA / tax counsel            EXECUTION_BLOCKING_NARROW
P2       telemedicine counsel           RELEASE_BLOCKING
REG-15   regulatory determination       RELEASE_BLOCKING
D-6      payment-regulatory             GOVERNED_DEFERRED
EV-39    SFDA symbology mandate         blocks EV-41 execution, not Phase-A build
EV-16    drug-reference licence         NOT SECURED — three limbs
EV-26    ZATCA stamp profile            published, unretrieved
EV-40/41/42/43  device fleet, read rate, printer, MDM
ORG-02   Veterinary Clinical Lead       see §41
```

---

## §39 · Acceptance criteria

Every included requirement carries an acceptance criterion that **can be failed**. A criterion that
cannot be failed is not a criterion (REQ-MVC-10.15). No acceptance criterion may be recorded as met
while it rests on an open `[EVIDENCE REQUIRED]` item (REQ-MVC-10.16).

**REQ-MVC-10.15 and REQ-MVC-10.16 are BINDING on the build**, not governance commentary. They are
enforced by the armed negative controls of MVC-EXEC-001 §7. *(RT-003 RT-04.)*

---

## §40 · Requirement traceability

`CURRENT_REQUIREMENT_TRACE_COVERAGE = 100%` — 495 of 495 identifiers resolve into a V3.2 section.
The full computed map is Appendix T. No requirement is silently omitted; fenced requirements resolve
into §3 with their reopening trigger.

---

## §41 · Release gates

```
CP-1  ARCH-05 ratification and immutable lock          Sponsor — NOT TAKEN
CP-2  PHASE_A_EXECUTION_READY                          Sponsor — NOT TAKEN
CP-3  FULL_PRODUCT_BUILD_READY                         Sponsor — NOT TAKEN
```

**ORG-02 · Veterinary Clinical Lead — reclassified.** The role's responsibilities are explicit and
the clinical thresholds engineering needs are already specified or fail-closed by §10's restriction.
Engineering is therefore **not** required to invent clinical decisions to proceed.

```
VETERINARY_CLINICAL_LEAD_ROLE = DEFINED
NAMED_CLINICAL_LEAD           = REQUIRED_BEFORE_CLINICAL_ACCEPTANCE_OR_RELEASE
ORG-02                        = RELEASE_BLOCKING
ORG02_CONDITION               = REQ-DISP-AUTH-FAILCLOSED (§11.1) authored, enforced and PROVEN
ORG02_CONDITION_SATISFIED_IN_IMPLEMENTATION = NO
```

The reclassification holds **only** while REQ-DISP-AUTH-FAILCLOSED holds. It is now a
**build-failable invariant** with four negative controls (§11.1), not prose — because
MVC-IMPL-FINDINGS-001 §P0-3 found the current implementation does the **opposite**: dispensing
requires `PHARMACY_OPERATOR` and denies the veterinarian.

⚠️ **ORG-02 stays RELEASE_BLOCKING on the specification, but the condition is currently
UNSATISFIED in the implementation.** Remediating that is backlog item W0-06 and is a precondition
of clinical acceptance, not of engineering start. If the fail-closed default is ever relaxed, a
named clinical lead must decide it first and ORG-02 returns to EXECUTION_BLOCKING.

---
*MVC-BRD-001 V3.2 · DRAFT · non-authorising · CP-2 not taken.*

---

## Appendix T · Requirement trace map (computed)

Derived mechanically from the BRD V3.1 S0–S10 part structure and the SPEC V3.1 / GAP V1.7
namespaces. Not hand-assigned. Denominator excludes the metavariable `REQ-MVC-n`.

| V3.2 § | Section | Requirements traced | Count |
|---:|---|---|---:|
| §0 | Document control | REQ-MVC-0.1, REQ-MVC-0.2, REQ-MVC-0.3 | 3 |
| §1 | Product definition | REQ-MVC-1, REQ-MVC-1.1, REQ-MVC-1.2, REQ-MVC-1.3, REQ-MVC-1.4, REQ-MVC-1.5 … (+8) | 14 |
| §2 | Phase-A scope | REQ-MVC-2.1, REQ-MVC-2.10, REQ-MVC-2.11, REQ-MVC-2.12, REQ-MVC-2.13, REQ-MVC-2.14 … (+29) | 35 |
| §3 | Fenced scope | REQ-MVC-2.1, REQ-MVC-2.10, REQ-MVC-2.11, REQ-MVC-2.12, REQ-MVC-2.13, REQ-MVC-2.14 … (+29) | 35 |
| §4 | Personas & authority | REQ-MVC-3.1, REQ-MVC-3.2, REQ-MVC-3.3, REQ-MVC-3.4, REQ-MVC-3.5, REQ-MVC-3.6 | 6 |
| §5 | Surfaces | REQ-MVC-4.1, REQ-MVC-4.10, REQ-MVC-4.100, REQ-MVC-4.101, REQ-MVC-4.102, REQ-MVC-4.103 … (+114) | 120 |
| §6 | Tenancy | REQ-MVC-8.1, REQ-MVC-8.10, REQ-MVC-8.100, REQ-MVC-8.101, REQ-MVC-8.102, REQ-MVC-8.103 … (+124) | 130 |
| §7 | Clinical workflows | REQ-MVC-4.1, REQ-MVC-4.10, REQ-MVC-4.100, REQ-MVC-4.101, REQ-MVC-4.102, REQ-MVC-4.103 … (+115) | 121 |
| §8 | Appointments | REQ-MVC-4.1, REQ-MVC-4.10, REQ-MVC-4.100, REQ-MVC-4.101, REQ-MVC-4.102, REQ-MVC-4.103 … (+106) | 112 |
| §9 | Medical records | REQ-MVC-4.1, REQ-MVC-4.10, REQ-MVC-4.100, REQ-MVC-4.101, REQ-MVC-4.102, REQ-MVC-4.103 … (+106) | 112 |
| §14 | Marketplace | REQ-MVC-9.1, REQ-MVC-9.10, REQ-MVC-9.11, REQ-MVC-9.12, REQ-MVC-9.13, REQ-MVC-9.2 … (+7) | 13 |
| §15 | Commercial model | REQ-MVC-9.1, REQ-MVC-9.10, REQ-MVC-9.11, REQ-MVC-9.12, REQ-MVC-9.13, REQ-MVC-9.2 … (+8) | 14 |
| §16 | Seller/taxpayer | REQ-FIN-G1, REQ-FIN-G2, REQ-FIN-G3, REQ-FIN-S1, REQ-FIN-S2, REQ-FIN-S3 … (+130) | 136 |
| §17 | Gross-not-net | REQ-FIN-G1, REQ-FIN-G2, REQ-FIN-G3, REQ-FIN-S1, REQ-FIN-S2, REQ-FIN-S3 … (+13) | 19 |
| §18 | Billing handoff | REQ-FIN-G1, REQ-FIN-G2, REQ-FIN-G3, REQ-FIN-S1, REQ-FIN-S2, REQ-FIN-S3 … (+130) | 136 |
| §19 | Payment seam | REQ-MVC-9.1, REQ-MVC-9.10, REQ-MVC-9.11, REQ-MVC-9.12, REQ-MVC-9.13, REQ-MVC-9.2 … (+7) | 13 |
| §20 | Refund/credit note | REQ-MVC-9.1, REQ-MVC-9.10, REQ-MVC-9.11, REQ-MVC-9.12, REQ-MVC-9.13, REQ-MVC-9.2 … (+7) | 13 |
| §21 | Telemedicine fence | REQ-MVC-4.1, REQ-MVC-4.10, REQ-MVC-4.100, REQ-MVC-4.101, REQ-MVC-4.102, REQ-MVC-4.103 … (+106) | 112 |
| §22 | Regulatory filing fence | REQ-MVC-6.1, REQ-MVC-6.10, REQ-MVC-6.11, REQ-MVC-6.12, REQ-MVC-6.13, REQ-MVC-6.14 … (+44) | 50 |
| §23 | Drug-reference fence | REQ-MVC-5.1, REQ-MVC-5.2, REQ-MVC-5.3, REQ-MVC-5.3a, REQ-MVC-5.3b, REQ-MVC-5.3c … (+8) | 14 |
| §24 | Clinical-absence disclosure | REQ-ABS-4, REQ-MVC-5.1, REQ-MVC-5.2, REQ-MVC-5.3, REQ-MVC-5.3a, REQ-MVC-5.3b … (+10) | 16 |
| §25 | Offline evidence | REQ-MVC-7.1, REQ-MVC-7.10, REQ-MVC-7.11, REQ-MVC-7.12, REQ-MVC-7.13, REQ-MVC-7.14 … (+51) | 57 |
| §26 | Audit chain | REQ-MVC-7.1, REQ-MVC-7.10, REQ-MVC-7.11, REQ-MVC-7.12, REQ-MVC-7.13, REQ-MVC-7.14 … (+51) | 57 |
| §27 | Device authority | REQ-MVC-8.1, REQ-MVC-8.10, REQ-MVC-8.100, REQ-MVC-8.101, REQ-MVC-8.102, REQ-MVC-8.103 … (+124) | 130 |
| §28 | Professional authority | REQ-VET-1, REQ-VET-10, REQ-VET-11, REQ-VET-3, REQ-VET-5, REQ-VET-6 … (+3) | 9 |
| §29 | Operator console | REQ-UX-3, REQ-UX-34, REQ-UX-39, REQ-UX-4, REQ-UX-6, REQ-UX-8 … (+2) | 8 |
| §32 | APIs/integration | REQ-INT-1, REQ-MVC-8.1, REQ-MVC-8.10, REQ-MVC-8.100, REQ-MVC-8.101, REQ-MVC-8.102 … (+125) | 131 |
| §33 | Security/access | REQ-MVC-6.1, REQ-MVC-6.10, REQ-MVC-6.11, REQ-MVC-6.12, REQ-MVC-6.13, REQ-MVC-6.14 … (+173) | 179 |
| §34 | Privacy | REQ-MVC-6.1, REQ-MVC-6.10, REQ-MVC-6.11, REQ-MVC-6.12, REQ-MVC-6.13, REQ-MVC-6.14 … (+43) | 49 |
| §35 | Observability | REQ-MVC-8.1, REQ-MVC-8.10, REQ-MVC-8.100, REQ-MVC-8.101, REQ-MVC-8.102, REQ-MVC-8.103 … (+124) | 130 |
| §36 | Compatibility/migration | REQ-MVC-7.1, REQ-MVC-7.10, REQ-MVC-7.11, REQ-MVC-7.12, REQ-MVC-7.13, REQ-MVC-7.14 … (+53) | 59 |
| §37 | External authority deps | REQ-MVC-6.1, REQ-MVC-6.10, REQ-MVC-6.11, REQ-MVC-6.12, REQ-MVC-6.13, REQ-MVC-6.14 … (+45) | 51 |
| §38 | External commercial deps | REQ-MVC-B.1, REQ-MVC-B.2 | 2 |
| §39 | Acceptance criteria | REQ-MVC-10.1, REQ-MVC-10.10, REQ-MVC-10.11, REQ-MVC-10.12, REQ-MVC-10.13, REQ-MVC-10.14 … (+24) | 30 |
| §40 | Requirement traceability | REQ-MVC-10.1, REQ-MVC-10.10, REQ-MVC-10.11, REQ-MVC-10.12, REQ-MVC-10.13, REQ-MVC-10.14 … (+30) | 36 |
| §41 | Release gates | REQ-MVC-10.1, REQ-MVC-10.10, REQ-MVC-10.11, REQ-MVC-10.12, REQ-MVC-10.13, REQ-MVC-10.14 … (+24) | 30 |

```
DISTINCT_REQUIREMENT_IDENTIFIERS = 495
TRACED_INTO_V3_2                = 495
UNTRACED                        = 0
CURRENT_REQUIREMENT_TRACE_COVERAGE = 100.0%
```

Rows appear under every section that governs them; a requirement governed by two
sections is traced to both. The coverage figure counts DISTINCT identifiers, so
multiple mappings never inflate it.
