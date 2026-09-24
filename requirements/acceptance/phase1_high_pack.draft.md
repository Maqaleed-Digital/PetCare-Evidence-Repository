# Phase-1 High acceptance pack — DRAFT, NOT RATIFIED

Authority: MVC-ACCEPTANCE-AUTHORITY-001, MVC-COMPLETION-AMENDMENTS-001, MVC-PHARM-001
BRD SHA-256: 5450f7832260532aafd080fa54999a66e7af914f1f3452ed3cb3c64950c640dc
W1 status measured at: 6b16e28d4a07442f5e60fed102cff79d2170bfb7

## Sponsor decision

```
[SPONSOR]
DECISION=MVC-ACCEPT-PACK-P1
RESULT=<RATIFY_ALL | RATIFY_EXCEPT>
EXCEPTIONS=[<AC-id or FR-id>: <reason>, ...]
```

## Summary

| FR | Title | W1 status | Criteria | Dependencies | Interpretations |
|---|---|---|---|---|---|
| FR-01 | Multi-role user accounts (Owner, Vet, Pharmacist, Admin) | REACHABLE_TESTED | 4 | COUNSEL:L-2 | 1 |
| FR-02 | Comprehensive pet profiles (medical history, allergies, preferences) | REACHABLE_UNTESTED | 4 | — | 1 |
| FR-04 | KYC verification for controlled medication purchases | ABSENT | 5 | COUNSEL:EV-11, EXTERNAL:KYC_PROVIDER | 2 |
| FR-05 | SFDA-compliant vet registration and verification | ABSENT | 4 | EXTERNAL:VET_LICENSING_AUTHORITY | 1 |
| FR-06 | HD video consultations with screen sharing | ABSENT | 5 | COUNSEL:REG-02_TELEMEDICINE, PRODUCTION | 1 |
| FR-07 | Secure chat and file sharing (images, lab reports) | ABSENT | 3 | PRODUCTION | 1 |
| FR-09 | Multi-language support (Arabic primary, English) | BUILT_UNWIRED | 3 | — | 0 |
| FR-13 | Real-time multi-location inventory visibility | ABSENT | 4 | COUNSEL:L-2 | 1 |
| FR-14 | Prescription upload and vet verification workflow | REACHABLE_TESTED | 7 | EXTERNAL:SFDA_API, PRODUCTION | 1 |
| FR-15 | Smart order routing to nearest/optimal pharmacy | ABSENT | 4 | COUNSEL:MVC-PHARM-001_§6c, EXTERNAL:MAPS_API | 1 |
| FR-16 | Temperature-controlled delivery tracking | ABSENT | 4 | EXTERNAL:LOGISTICS_PARTNER | 1 |
| FR-19 | SFDA batch tracking and recall notifications | ABSENT | 4 | EXTERNAL:SFDA_API | 0 |
| FR-20 | Cash-on-delivery with digital receipting | ABSENT | 4 | EXTERNAL:LOGISTICS_PARTNER | 1 |
| FR-23 | Vaccination and treatment reminders | ABSENT | 4 | EXTERNAL:SMS_GATEWAY | 1 |
| FR-27 | Real-time dashboard for pharmacy operations | REACHABLE_TESTED | 4 | COUNSEL:L-2 | 1 |
| FR-30 | SFDA compliance reporting automation | ABSENT | 5 | EXTERNAL:SFDA | 2 |

## FR-01 — Multi-role user accounts (Owner, Vet, Pharmacist, Admin)

Candidate source: RATIFIED_CANDIDATE_MAPPING · Customer-facing: True · Client acceptance applies: True

**AC-FR-01-01** — A person can register and sign in as one of the BRD roles owner, vet or admin (BRD §5.1 table FR-01; data model P368 'role (owner/vet/pharmacist/admin)'), and the served application authorises each request from the signed session, never from a client-supplied role.
- Fails if: any served route accepts a role, actor or tenant asserted by the client in place of the signed session; or a registered identity cannot sign in and reach the surface of its role.
- Evidence: SERVED_APP_E2E, UI, TENANT_ISOLATION
- Sources: BRD:FR-01, REQ:REQ-MVC-8.34
- Dependency: NONE

**AC-FR-01-02** — Every regulated act (prescribing, dispensing) is authorised by a live practitioner authority attribute evaluated at the moment of the act, in addition to role and tenant membership.
- Fails if: any permission check resolves a regulated act from a role, group, permission string or token claim without reading a live authority attribute (verbatim limb of REQ-MVC-8.32).
- Evidence: SERVED_APP_E2E, AUDIT
- Sources: BRD:FR-01, REQ:REQ-MVC-8.32
- Dependency: NONE

**AC-FR-01-03** — Tenant membership is a server-held, time-bounded relationship; ending it does not make any historical record unattributable, and every account action is written to the audit chain with the session actor.
- Fails if: tenant_id is read from a token or provider assertion at an authorisation decision point; or ending a membership renders any historical record unattributable; or an account action is absent from the audit chain.
- Evidence: PERSISTENCE, AUDIT, TENANT_ISOLATION
- Sources: BRD:FR-01, REQ:REQ-MVC-8.34
- Dependency: NONE

**AC-FR-01-04** — The BRD 'Pharmacist' role is realised only as a class-scoped pharmacy authority requiring an establishment licence and an individual credential; no general-purpose pharmacy role exists.
- Fails if: any role grants pharmacy authority not scoped to a supply class; or a pharmacy authority is usable without both an establishment licence and an actor credential.
- Evidence: SERVED_APP_E2E, AUDIT
- Sources: BRD:FR-01, SPONSOR_ACT:MVC-PHARM-001 §6b
- Dependency: COUNSEL:L-2
- Interpretation for Sponsor: BRD FR-01 names Pharmacist as a role; MVC-PHARM-001 §6b forbids a general-purpose pharmacy role and §5 holds the POM/RESTRICTED/CONTROLLED dispensing credential pending counsel. Confirm that FR-01 is satisfied by class-scoped authority rather than a 'pharmacist' role.


## FR-02 — Comprehensive pet profiles (medical history, allergies, preferences)

Candidate source: RATIFIED_CANDIDATE_MAPPING · Customer-facing: True · Client acceptance applies: True

**AC-FR-02-01** — An owner can create and view a pet profile carrying the BRD fields name, species, breed, birth date, weight, medical conditions and allergies (BRD P373-P374), persisted durably and scoped to the owner's tenant.
- Fails if: a profile created through the served app is lost on process restart; or any profile field listed in BRD P373-P374 cannot be recorded; or a profile is readable from another tenant.
- Evidence: SERVED_APP_E2E, PERSISTENCE, TENANT_ISOLATION, UI
- Sources: BRD:FR-02, REQ:REQ-MVC-7.3
- Dependency: NONE

**AC-FR-02-02** — The profile shows the pet's medical history (records, prescriptions, lab results; BRD P111, P380) and owner preferences (BRD FR-02 title).
- Fails if: the profile surface cannot display a recorded prescription or lab result for that pet; or preferences cannot be stored.
- Evidence: SERVED_APP_E2E, UI, ARABIC_RTL
- Sources: BRD:FR-02
- Dependency: NONE

**AC-FR-02-03** — Animal identification (e.g. microchip id, BRD P375) is a structured field with identifier type, value and capture date, never free text.
- Fails if: identification is stored as unstructured text; or the field is made mandatory on the strength of an unsourced obligation (limbs of REQ-MVC-6.10).
- Evidence: PERSISTENCE
- Sources: BRD:FR-02, REQ:REQ-MVC-6.10
- Dependency: NONE

**AC-FR-02-04** — Every profile create and change is attributed in the audit chain to the session actor.
- Fails if: a profile mutation is written with a client-supplied actor or without an audit event.
- Evidence: AUDIT, SERVED_APP_E2E
- Sources: BRD:FR-02
- Dependency: NONE
- Interpretation for Sponsor: W1 measured POST /api/pets writing a client-supplied audit actor (x_actor_id); this criterion would fail today.


## FR-04 — KYC verification for controlled medication purchases

Candidate source: RATIFIED_CANDIDATE_MAPPING · Customer-facing: True · Client acceptance applies: True

**AC-FR-04-01** — A controlled or restricted medication cannot be supplied unless the verification the BRD requires for such purchases has been completed and recorded (BRD FR-04; REG-05 'Controlled Substance Tracking' P237).
- Fails if: any path supplies a RESTRICTED or CONTROLLED product without a recorded, passed verification; or the purchaser is not shown, in the purchase flow, that verification is required and why.
- Evidence: SERVED_APP_E2E, UI, AUDIT
- Sources: BRD:FR-04, REQ:REQ-MVC-4.25, SPONSOR_ACT:MVC-PHARM-001 §5
- Dependency: COUNSEL:EV-11
- Interpretation for Sponsor: BRD FR-04 says purchaser 'KYC'; the candidate REQ-MVC-4.25 places the control on prescriber authority. Confirm which party the verification binds before this criterion is testable.

**AC-FR-04-02** — Until counsel resolves EV-11 and L-2, the restricted-substance workflow is disabled in every environment and cannot be enabled by flag, admin action or configuration.
- Fails if: any code path, feature flag, admin action or configuration value can enable a restricted-substance dispensing, register or wastage workflow while EV-11 is open (verbatim limb of REQ-MVC-6.19).
- Evidence: SERVED_APP_E2E
- Sources: BRD:FR-04, REQ:REQ-MVC-6.19, SPONSOR_ACT:MVC-PHARM-001 §5
- Dependency: NONE

**AC-FR-04-03** — Supply class is taken from SFDA product registration; a veterinary medicine with no verified class is treated as POM.
- Fails if: any product's supply class is set by MyVetiCare or tenant staff; or an unclassified veterinary medicine is sold without the POM prescription gate.
- Evidence: PERSISTENCE, AUDIT, TENANT_ISOLATION
- Sources: BRD:FR-04, SPONSOR_ACT:MVC-PHARM-001 §6a
- Dependency: NONE

**AC-FR-04-04** — The identity-verification step is exercised against a contract/adapter test of the chosen KYC provider.
- Fails if: the adapter accepts an unverified or failed verification as passed.
- Evidence: SERVED_APP_E2E
- Sources: BRD:FR-04
- Dependency: EXTERNAL:KYC_PROVIDER
- Interpretation for Sponsor: BRD names no KYC provider; one must be chosen before the live criterion can exist.

**AC-FR-04-05** — Live verification completes against the chosen KYC provider in production.
- Fails if: a production controlled-medication purchase completes without a live provider verification record.
- Evidence: SERVED_APP_E2E, AUDIT
- Sources: BRD:FR-04
- Dependency: EXTERNAL:KYC_PROVIDER


## FR-05 — SFDA-compliant vet registration and verification

Candidate source: NONE · Customer-facing: True · Client acceptance applies: True

**AC-FR-05-01** — A veterinarian registers with licence details and is not able to perform clinical acts until the licence is verified (BRD FR-05; medical governance 'Vet Credentialing: rigorous verification' P598).
- Fails if: an unverified vet can issue a prescription or sign a clinical record; or registration completes without licence details.
- Evidence: SERVED_APP_E2E, UI, AUDIT
- Sources: BRD:FR-05
- Dependency: NONE
- Interpretation for Sponsor: BRD v1.0 says 'SFDA-compliant'; V3.0 proposes MEWA as the licensing regulator. AA-2 keeps the v1.0 wording in force. Confirm the licensing authority to verify against.

**AC-FR-05-02** — Verification state and its evidence (who verified, when, against what) are persisted, audited and re-checked for expiry at the moment of each clinical act.
- Fails if: a vet whose licence has expired can still perform a clinical act; or a verification has no recorded verifier and timestamp.
- Evidence: PERSISTENCE, AUDIT, TENANT_ISOLATION
- Sources: BRD:FR-05
- Dependency: NONE

**AC-FR-05-03** — Licence verification passes an adapter/contract test against the licensing authority's lookup.
- Fails if: the adapter returns verified for an unknown or lapsed licence number.
- Evidence: SERVED_APP_E2E
- Sources: BRD:FR-05
- Dependency: EXTERNAL:VET_LICENSING_AUTHORITY

**AC-FR-05-04** — Licence verification runs live against the licensing authority in production.
- Fails if: a production vet becomes verified without a live authority lookup or a recorded manual verification by a named staff member.
- Evidence: AUDIT
- Sources: BRD:FR-05
- Dependency: EXTERNAL:VET_LICENSING_AUTHORITY


## FR-06 — HD video consultations with screen sharing

Candidate source: NONE · Customer-facing: True · Client acceptance applies: True

**AC-FR-06-01** — An owner and a verified vet can hold a scheduled video consultation with screen sharing from the served application (BRD FR-06; Milestone 1.2 P445; Journey 1 P267).
- Fails if: a booked consultation cannot connect both parties with video; or screen sharing is unavailable in-session.
- Evidence: SERVED_APP_E2E, UI, ARABIC_RTL
- Sources: BRD:FR-06
- Dependency: NONE

**AC-FR-06-02** — Video meets NFR-03: HD (720p) minimum with adaptive bitrate.
- Fails if: a consultation on a qualifying connection renders below 720p without an adaptive-bitrate step-down record.
- Evidence: SERVED_APP_E2E
- Sources: BRD:FR-06
- Dependency: NONE

**AC-FR-06-03** — Consultation success rate exceeds 99% over the Phase-1 measurement window (BRD §13.1 P574).
- Fails if: measured production consultation success rate is 99% or below.
- Evidence: SERVED_APP_E2E
- Sources: BRD:FR-06
- Dependency: PRODUCTION

**AC-FR-06-04** — The consultation, its participants and outcome are persisted and audited within the owner's tenant.
- Fails if: a consultation record is missing, unattributed, or readable across tenants.
- Evidence: PERSISTENCE, AUDIT, TENANT_ISOLATION
- Sources: BRD:FR-06
- Dependency: NONE

**AC-FR-06-05** — Remote consultation is offered only in the form counsel confirms lawful in KSA.
- Fails if: the product offers remote veterinary consultation before REG-02 / telemedicine counsel is recorded.
- Evidence: UI
- Sources: BRD:FR-06
- Dependency: COUNSEL:REG-02_TELEMEDICINE
- Interpretation for Sponsor: BRD REG-02 lists telemedicine guidelines as a regulatory requirement; the repository records KSA veterinary telemedicine as unresolved.


## FR-07 — Secure chat and file sharing (images, lab reports)

Candidate source: RATIFIED_CANDIDATE_MAPPING · Customer-facing: True · Client acceptance applies: True

**AC-FR-07-01** — Owner and vet can exchange messages and share files (images, lab reports) within a consultation context from the served app (BRD FR-07).
- Fails if: an image or lab-report file cannot be attached and retrieved by the other party; or a message is visible to anyone outside the consultation.
- Evidence: SERVED_APP_E2E, UI, TENANT_ISOLATION, ARABIC_RTL
- Sources: BRD:FR-07
- Dependency: NONE

**AC-FR-07-02** — Messages and files are encrypted in transit and at rest (NFR-05) and every attempt to deliver a notification writes a delivery record.
- Fails if: any delivery attempt lacks a record; or a record references a mutable template instead of carrying the rendered body (limbs of REQ-MVC-8.67).
- Evidence: PERSISTENCE, AUDIT
- Sources: BRD:FR-07, REQ:REQ-MVC-8.67
- Dependency: NONE
- Interpretation for Sponsor: Candidate REQ-MVC-8.67 (LOW confidence) covers notification delivery evidence only, not chat; confirm it is an acceptable source.

**AC-FR-07-03** — Shared files are validated for type and size and stored in an object store, not on the serving node.
- Fails if: an unsupported file type is accepted; or files are held on node-local storage in production.
- Evidence: PERSISTENCE
- Sources: BRD:FR-07
- Dependency: PRODUCTION


## FR-09 — Multi-language support (Arabic primary, English)

Candidate source: NONE · Customer-facing: True · Client acceptance applies: True

**AC-FR-09-01** — Every customer-facing surface is available in Arabic (primary, default) and English, with the owner able to switch language (BRD FR-09).
- Fails if: any customer-facing page renders English-only text in Arabic mode; or Arabic is not the default for a new visitor.
- Evidence: UI, ARABIC_RTL
- Sources: BRD:FR-09
- Dependency: NONE

**AC-FR-09-02** — Arabic renders right-to-left with correct direction on every customer-facing page and the persistent language choice survives a new session.
- Fails if: any customer-facing page renders LTR layout in Arabic mode; or the chosen language resets on reload.
- Evidence: UI, ARABIC_RTL, SERVED_APP_E2E
- Sources: BRD:FR-09
- Dependency: NONE

**AC-FR-09-03** — Notifications and generated documents (receipts, reminders) are produced in the recipient's chosen language.
- Fails if: an Arabic-preferring owner receives a notification or document only in English.
- Evidence: SERVED_APP_E2E, ARABIC_RTL
- Sources: BRD:FR-09
- Dependency: NONE


## FR-13 — Real-time multi-location inventory visibility

Candidate source: RATIFIED_CANDIDATE_MAPPING · Customer-facing: False · Client acceptance applies: True

**AC-FR-13-01** — Stock is visible per location for every pharmacy in the tenant (BRD P394 'locations: {pharmacy_id: quantity}'; P93, P103), and a stock change at one location is visible to all authorised users of the tenant without manual refresh.
- Fails if: a stock change at location A is not reflected for location B's authorised user within the agreed interval; or stock of another tenant is visible.
- Evidence: SERVED_APP_E2E, UI, TENANT_ISOLATION
- Sources: BRD:FR-13
- Dependency: NONE
- Interpretation for Sponsor: BRD says 'real-time'; the agreed propagation interval must be set by the Sponsor.

**AC-FR-13-02** — Stock is an immutable movement ledger with a derived balance.
- Fails if: any stock quantity is stored as authoritative mutable state; or any code path updates or deletes a movement row; or any shown balance cannot be reproduced by summing the movements for that (product, batch) (REQ-MVC-7.30).
- Evidence: PERSISTENCE, AUDIT
- Sources: BRD:FR-13, REQ:REQ-MVC-7.30, REQ:REQ-MVC-4.68
- Dependency: NONE

**AC-FR-13-03** — Inventory checks meet NFR-04: sub-second query response.
- Fails if: an inventory check on production-sized data takes one second or more.
- Evidence: PERSISTENCE
- Sources: BRD:FR-13
- Dependency: NONE

**AC-FR-13-04** — POM, RESTRICTED and CONTROLLED stock are excluded from non-veterinarian inventory handling until counsel.
- Fails if: a non-veterinarian actor can move or adjust POM/RESTRICTED/CONTROLLED stock.
- Evidence: SERVED_APP_E2E, AUDIT
- Sources: BRD:FR-13, SPONSOR_ACT:MVC-PHARM-001 §5
- Dependency: COUNSEL:L-2


## FR-14 — Prescription upload and vet verification workflow

Candidate source: RATIFIED_CANDIDATE_MAPPING · Customer-facing: True · Client acceptance applies: True

**AC-FR-14-01** — A prescription can be issued or uploaded with its documents and moves ISSUED -> VET_VERIFIED -> DISPENSED only through the governed transitions, persisted durably (BRD FR-14; P384-P387; P92).
- Fails if: a prescription can be dispensed without vet verification; or a transition outside the governed set is accepted; or the prescription is lost on restart.
- Evidence: SERVED_APP_E2E, PERSISTENCE, UI
- Sources: BRD:FR-14, REQ:REQ-MVC-7.11
- Dependency: NONE

**AC-FR-14-02** — Dispensing authority fails closed: a POM/RESTRICTED/CONTROLLED dispense is authorised only for a veterinarian until counsel, and never on a client-asserted class.
- Fails if: any dispensing path authorises on a client-asserted class (REQ-DISP-AUTH-FAILCLOSED); or a non-veterinarian dispenses a POM product.
- Evidence: SERVED_APP_E2E, AUDIT
- Sources: BRD:FR-14, REQ:REQ-DISP-AUTH-FAILCLOSED, SPONSOR_ACT:MVC-PHARM-001 §5
- Dependency: NONE

**AC-FR-14-03** — The prescription gate applies to POM, RESTRICTED and CONTROLLED products only; GENERAL and OTC need no prescription.
- Fails if: a GENERAL or OTC product is blocked for lack of a prescription; or a POM product is supplied without one.
- Evidence: SERVED_APP_E2E
- Sources: BRD:FR-14, SPONSOR_ACT:MVC-PHARM-001 §4, SPONSOR_ACT:MVC-PHARM-001 §6a
- Dependency: NONE

**AC-FR-14-04** — A vet whose professional status does not permit prescribing is shown the prescribing control as unavailable, with the reason.
- Fails if: the scenario yields a signed prescription through any path; or the control fails on submit instead of being presented as unavailable; or the refusal does not name the attribute and its expiry (REQ-MVC-8.38).
- Evidence: SERVED_APP_E2E, UI
- Sources: BRD:FR-14, REQ:REQ-MVC-8.38
- Dependency: NONE

**AC-FR-14-05** — Every prescription read and transition is tenant-scoped and audited with the session actor.
- Fails if: a prescription is readable from another tenant; or a transition has no audit event naming the session actor.
- Evidence: TENANT_ISOLATION, AUDIT, PERSISTENCE
- Sources: BRD:FR-14
- Dependency: NONE

**AC-FR-14-06** — Prescription validation passes an adapter/contract test of the SFDA prescription-validation interface (BRD P419).
- Fails if: the adapter treats an invalid or unknown prescription as valid.
- Evidence: SERVED_APP_E2E
- Sources: BRD:FR-14
- Dependency: EXTERNAL:SFDA_API
- Interpretation for Sponsor: BRD P621 assumes SFDA will provide API access; unconfirmed.

**AC-FR-14-07** — 95% of prescriptions are verified within 30 minutes in production (BRD §13.1 P572).
- Fails if: measured production verification time exceeds 30 minutes for more than 5% of prescriptions.
- Evidence: SERVED_APP_E2E
- Sources: BRD:FR-14
- Dependency: PRODUCTION


## FR-15 — Smart order routing to nearest/optimal pharmacy

Candidate source: NONE · Customer-facing: True · Client acceptance applies: True

**AC-FR-15-01** — An order is routed to the nearest pharmacy that holds the items and is licensed for their supply class (BRD FR-15; Journey 1 P270; Milestone 1.3 P452).
- Fails if: an order is routed to a pharmacy without stock of an item; or to one not licensed for that supply class; or not to the nearest qualifying pharmacy under the defined distance measure.
- Evidence: SERVED_APP_E2E, TENANT_ISOLATION
- Sources: BRD:FR-15, SPONSOR_ACT:MVC-PHARM-001 §6b
- Dependency: COUNSEL:MVC-PHARM-001_§6c
- Interpretation for Sponsor: V3.0 proposes rejecting FR-15; AA-2 keeps it in force. 'Optimal' needs a Sponsor-defined tie-break.

**AC-FR-15-02** — Routing distance is computed through an adapter/contract test of the maps provider (BRD P423).
- Fails if: the router uses a hard-coded distance or ignores the owner's location.
- Evidence: SERVED_APP_E2E
- Sources: BRD:FR-15
- Dependency: EXTERNAL:MAPS_API

**AC-FR-15-03** — Routing uses the live maps provider in production.
- Fails if: production routing decisions are made without a live maps lookup.
- Evidence: SERVED_APP_E2E
- Sources: BRD:FR-15
- Dependency: EXTERNAL:MAPS_API

**AC-FR-15-04** — Each routing decision is recorded with its inputs and the chosen pharmacy, and is visible to the owner.
- Fails if: a routed order has no recorded routing decision; or the owner cannot see which pharmacy fulfils it.
- Evidence: AUDIT, UI, PERSISTENCE
- Sources: BRD:FR-15
- Dependency: NONE


## FR-16 — Temperature-controlled delivery tracking

Candidate source: NONE · Customer-facing: True · Client acceptance applies: True

**AC-FR-16-01** — For a product whose storage requirements need temperature control (BRD P393), the delivery carries a temperature log (BRD P401) visible to the owner in the app (Journey 1 P272).
- Fails if: a temperature-controlled delivery completes with no temperature log; or the owner cannot see it.
- Evidence: SERVED_APP_E2E, UI, PERSISTENCE
- Sources: BRD:FR-16
- Dependency: NONE

**AC-FR-16-02** — Temperature readings are ingested through an adapter/contract test of the logistics partner interface (BRD P422).
- Fails if: the adapter accepts a reading without timestamp or value, or silently drops out-of-range readings.
- Evidence: SERVED_APP_E2E
- Sources: BRD:FR-16
- Dependency: EXTERNAL:LOGISTICS_PARTNER

**AC-FR-16-03** — Live deliveries report temperature from the logistics partner in production.
- Fails if: a production temperature-controlled delivery has no partner-reported readings.
- Evidence: SERVED_APP_E2E
- Sources: BRD:FR-16
- Dependency: EXTERNAL:LOGISTICS_PARTNER
- Interpretation for Sponsor: V3.0 proposes rejecting FR-16; AA-2 keeps it in force.

**AC-FR-16-04** — An out-of-range reading raises an alert to the pharmacy and is audited.
- Fails if: an out-of-range reading produces no alert or no audit event.
- Evidence: AUDIT, TENANT_ISOLATION
- Sources: BRD:FR-16
- Dependency: NONE


## FR-19 — SFDA batch tracking and recall notifications

Candidate source: RATIFIED_CANDIDATE_MAPPING · Customer-facing: True · Client acceptance applies: True

**AC-FR-19-01** — Every stock movement and dispense records the batch (BRD P392 'batch_number, expiry_date').
- Fails if: a movement can be written without a batch; or signed_quantity is zero; or a movement row is ever updated or deleted (REQ-MVC-7.32).
- Evidence: PERSISTENCE, AUDIT
- Sources: BRD:FR-19, REQ:REQ-MVC-7.32, REQ:REQ-MVC-7.12
- Dependency: NONE

**AC-FR-19-02** — A recall of a product and batch resolves to every affected dispense and owner through stored relationships, and notifies each affected owner.
- Fails if: any hop resolves through free text; or the indeterminate partition is absent or hidden; or an output omits its completeness statement (REQ-MVC-6.22); or an affected owner is not notified.
- Evidence: SERVED_APP_E2E, UI, TENANT_ISOLATION, AUDIT
- Sources: BRD:FR-19, REQ:REQ-MVC-6.22
- Dependency: NONE

**AC-FR-19-03** — Batch tracking and recall ingestion pass an adapter/contract test of the SFDA interface (BRD P419).
- Fails if: the adapter accepts a recall without product and batch identifiers.
- Evidence: SERVED_APP_E2E
- Sources: BRD:FR-19
- Dependency: EXTERNAL:SFDA_API

**AC-FR-19-04** — Recalls are received live from SFDA in production.
- Fails if: a production SFDA recall is not reflected in the platform.
- Evidence: SERVED_APP_E2E
- Sources: BRD:FR-19
- Dependency: EXTERNAL:SFDA_API


## FR-20 — Cash-on-delivery with digital receipting

Candidate source: NONE · Customer-facing: True · Client acceptance applies: True

**AC-FR-20-01** — An owner can choose cash on delivery at checkout, and the order records COD as its payment method (BRD FR-20).
- Fails if: COD cannot be selected for an eligible order; or the order does not record COD.
- Evidence: SERVED_APP_E2E, UI, PERSISTENCE
- Sources: BRD:FR-20
- Dependency: NONE

**AC-FR-20-02** — On delivery the owner receives a digital receipt in the chosen language, and the receipt is persisted against the order.
- Fails if: a delivered COD order has no digital receipt; or the receipt is not retrievable later.
- Evidence: SERVED_APP_E2E, UI, ARABIC_RTL, PERSISTENCE
- Sources: BRD:FR-20
- Dependency: NONE
- Interpretation for Sponsor: BRD says 'digital receipting'; V3.0 proposes ZATCA e-invoicing. Confirm whether a tax invoice (ZATCA) is required for Phase-1 acceptance.

**AC-FR-20-03** — Cash collection is confirmed through an adapter/contract test of the logistics partner (BRD P422).
- Fails if: an order is marked paid without a collection confirmation.
- Evidence: SERVED_APP_E2E, AUDIT
- Sources: BRD:FR-20
- Dependency: EXTERNAL:LOGISTICS_PARTNER

**AC-FR-20-04** — Cash collection is confirmed live by the logistics partner in production, and receipts reconcile to collections per tenant.
- Fails if: a production collection has no partner confirmation; or receipts and collections do not reconcile within a tenant.
- Evidence: AUDIT, TENANT_ISOLATION
- Sources: BRD:FR-20
- Dependency: EXTERNAL:LOGISTICS_PARTNER


## FR-23 — Vaccination and treatment reminders

Candidate source: NONE · Customer-facing: True · Client acceptance applies: True

**AC-FR-23-01** — A vaccination or treatment due date recorded for a pet produces a reminder to the owner before it falls due (BRD FR-23; Journey 1 P265; P113).
- Fails if: a recorded due date produces no reminder; or a reminder is sent for another tenant's pet.
- Evidence: SERVED_APP_E2E, UI, PERSISTENCE, TENANT_ISOLATION
- Sources: BRD:FR-23
- Dependency: NONE
- Interpretation for Sponsor: BRD does not fix the reminder lead time; Sponsor to set it.

**AC-FR-23-02** — Reminders are delivered in the owner's chosen language and each send is audited.
- Fails if: an Arabic-preferring owner receives an English-only reminder; or a send has no audit record.
- Evidence: ARABIC_RTL, AUDIT
- Sources: BRD:FR-23
- Dependency: NONE

**AC-FR-23-03** — SMS reminders pass an adapter/contract test of the SMS gateway (BRD P421).
- Fails if: the adapter reports success for a rejected send.
- Evidence: SERVED_APP_E2E
- Sources: BRD:FR-23
- Dependency: EXTERNAL:SMS_GATEWAY

**AC-FR-23-04** — SMS reminders are delivered live through the SMS gateway in production.
- Fails if: production reminders have no gateway delivery status.
- Evidence: SERVED_APP_E2E
- Sources: BRD:FR-23
- Dependency: EXTERNAL:SMS_GATEWAY


## FR-27 — Real-time dashboard for pharmacy operations

Candidate source: NONE · Customer-facing: True · Client acceptance applies: True

**AC-FR-27-01** — Pharmacy operations staff see a dashboard of the tenant's orders and verified prescriptions awaiting fulfilment that updates without manual refresh (BRD FR-27; P101).
- Fails if: a new verified prescription does not appear within the agreed interval; or another tenant's item appears.
- Evidence: SERVED_APP_E2E, UI, TENANT_ISOLATION
- Sources: BRD:FR-27
- Dependency: NONE
- Interpretation for Sponsor: BRD says 'real-time'; the propagation interval must be set by the Sponsor. W1 measured a request/response queue.

**AC-FR-27-02** — Actions taken from the dashboard are limited by supply class: GENERAL/OTC actions by a class-scoped actor, POM dispense by a veterinarian only until counsel.
- Fails if: a non-veterinarian completes a POM dispense from the dashboard; or an actor acts on a class outside its scope.
- Evidence: SERVED_APP_E2E, AUDIT
- Sources: BRD:FR-27, SPONSOR_ACT:MVC-PHARM-001 §4, SPONSOR_ACT:MVC-PHARM-001 §5
- Dependency: COUNSEL:L-2

**AC-FR-27-03** — Every dashboard action is audited with the session actor and persisted.
- Fails if: a dashboard action has no audit event or uses a client-supplied actor.
- Evidence: AUDIT, PERSISTENCE
- Sources: BRD:FR-27
- Dependency: NONE

**AC-FR-27-04** — The dashboard is usable in Arabic with RTL layout.
- Fails if: the dashboard renders English-only or LTR in Arabic mode.
- Evidence: UI, ARABIC_RTL
- Sources: BRD:FR-27
- Dependency: NONE


## FR-30 — SFDA compliance reporting automation

Candidate source: RATIFIED_CANDIDATE_MAPPING · Customer-facing: False · Client acceptance applies: False

**AC-FR-30-01** — The platform produces the SFDA compliance reports the BRD requires, including the controlled-substance audit trail (BRD FR-30; REG-05 P237; NFR-06), generated automatically from recorded events.
- Fails if: a required report must be assembled manually; or a report figure cannot be traced to recorded events.
- Evidence: PERSISTENCE, AUDIT, TENANT_ISOLATION
- Sources: BRD:FR-30
- Dependency: NONE
- Interpretation for Sponsor: BRD does not enumerate the report set; V3.0 proposes MEWA case-register and antimicrobial reporting. Sponsor to fix the Phase-1 report list.

**AC-FR-30-02** — Antimicrobial prescribing is individually recorded and aggregable by agent, class, species, practitioner and period.
- Fails if: an antimicrobial aggregate is producible only by text search; or any register output omits its coverage statement (REQ-MVC-6.20).
- Evidence: PERSISTENCE
- Sources: BRD:FR-30, REQ:REQ-MVC-6.20
- Dependency: NONE

**AC-FR-30-03** — Notifiable-disease reports carry the statutory clock from detection.
- Fails if: a notifiable-disease case exists with no reporting clock.
- Evidence: AUDIT
- Sources: BRD:FR-30, REQ:REQ-MVC-4.28
- Dependency: NONE
- Interpretation for Sponsor: Candidate REQ-MVC-4.28 has no source-authored fails-if; this criterion text is drafted here.

**AC-FR-30-04** — Report submission passes an adapter/contract test of the regulator interface.
- Fails if: the adapter accepts a report missing a mandatory field.
- Evidence: SERVED_APP_E2E
- Sources: BRD:FR-30
- Dependency: EXTERNAL:SFDA

**AC-FR-30-05** — Reports are submitted live to the regulator in production.
- Fails if: a production reporting period passes without a recorded submission.
- Evidence: AUDIT
- Sources: BRD:FR-30
- Dependency: EXTERNAL:SFDA

## Non-functional requirements

**NFR-01 — System Response Time** · Phase-1 relevant: True — Phase-1 surfaces are user-facing; BRD states a single response target.
- Metric: p95 server response time · Method: load test of Phase-1 served routes at the NFR-02 concurrency · Threshold: < 2 seconds for 95% of requests · Environment: NON_PROD · Dependency: NONE

**NFR-02 — Concurrent Users** · Phase-1 relevant: True — BRD §13.1 P571 makes 10,000 concurrent users a Phase-1 acceptance criterion.
- Metric: simultaneous active sessions without degradation · Method: load test with degradation defined as breaching NFR-01 · Threshold: Support 10,000 simultaneous users · Environment: NON_PROD · Dependency: NONE

**NFR-03 — Video Consultation Quality** · Phase-1 relevant: True — FR-06 video consultation is Phase-1 High.
- Metric: delivered video resolution and bitrate adaptation · Method: instrumented consultation sessions across network profiles · Threshold: HD (720p) minimum, adaptive bitrate · Environment: NON_PROD · Dependency: NONE

**NFR-04 — Database Performance** · Phase-1 relevant: True — FR-13 inventory visibility is Phase-1 High.
- Metric: inventory query latency · Method: timed inventory checks on production-sized data · Threshold: Sub-second query response for inventory checks · Environment: NON_PROD · Dependency: NONE

**NFR-05 — Data Encryption** · Phase-1 relevant: True — Phase-1 stores personal and pet health data.
- Metric: encryption at rest and in transit · Method: configuration inspection of stores and TLS scan of every endpoint · Threshold: AES-256 at rest, TLS 1.3 in transit · Environment: PRODUCTION · Dependency: PRODUCTION

**NFR-06 — SFDA Compliance** · Phase-1 relevant: True — FR-04 and FR-30 are Phase-1 High and depend on it.
- Metric: completeness of the controlled-substance audit trail · Method: trace every controlled-substance event to an audit record · Threshold: Full audit trail for controlled substances · Environment: NON_PROD · Dependency: COUNSEL:EV-11

**NFR-07 — Data Residency** · Phase-1 relevant: True — Phase-1 production holds customer data. Interpretation for Sponsor: BRD §7.2 P360 recommends 'AWS/GCP in Bahrain region', which conflicts with this NFR; the NFR target is used here.
- Metric: storage and processing location of all data · Method: inventory of every data store and backup with its region · Threshold: All data stored in KSA-based servers · Environment: PRODUCTION · Dependency: PRODUCTION

**NFR-08 — Access Controls** · Phase-1 relevant: True — Phase-1 has role-based surfaces and regulated acts.
- Metric: role enforcement and MFA on sensitive operations · Method: served-app tests per role plus MFA challenge on each sensitive operation · Threshold: Role-based with MFA for sensitive operations · Environment: NON_PROD · Dependency: NONE

**NFR-09 — HIPAA Equivalent** · Phase-1 relevant: True — Phase-1 holds pet health records. Interpretation for Sponsor: the BRD target is not measurable as written; PDPL (REG-03) is proposed as the concrete standard.
- Metric: conformance to the adopted data-protection standard · Method: control-by-control inspection against the adopted standard · Threshold: Pet health data protection standards · Environment: PRODUCTION · Dependency: COUNSEL:REG-03_PDPL

**NFR-10 — System Uptime** · Phase-1 relevant: True — BRD §13.1 P576 requires > 99.5% uptime in the first 90 days.
- Metric: availability over the first 90 days · Method: external uptime monitoring of production · Threshold: 99.5% availability (excluding maintenance) · Environment: PRODUCTION · Dependency: PRODUCTION

**NFR-11 — Disaster Recovery** · Phase-1 relevant: True — Phase-1 production requires recovery objectives.
- Metric: measured recovery time and data-loss window · Method: timed restore drill from production backups · Threshold: RTO < 4 hours, RPO < 15 minutes · Environment: PRODUCTION · Dependency: PRODUCTION

**NFR-12 — Backup Strategy** · Phase-1 relevant: True — Phase-1 production requires backups.
- Metric: backup schedule adherence · Method: inspection of backup schedule and restore of a sample · Threshold: Daily incremental, weekly full backups · Environment: PRODUCTION · Dependency: PRODUCTION

**NFR-13 — Horizontal Scaling** · Phase-1 relevant: False — Growth beyond the Phase-1 load (NFR-02) is not a Phase-1 acceptance item; BRD places scale optimisation at Milestone 2.3 (P471).

**NFR-14 — Geographic Expansion** · Phase-1 relevant: False — BRD places GCC expansion preparation at Milestone 2.3 (P473).

**NFR-15 — API Rate Limiting** · Phase-1 relevant: True — BRD places rate limiting in the Phase-1 gateway (P317). Interpretation for Sponsor: the target is not measurable as written; a numeric limit must be set.
- Metric: request rate limit per client · Method: served-app test that excess requests are throttled and normal traffic is not · Threshold: Protect against abuse while allowing legitimate use · Environment: NON_PROD · Dependency: NONE

