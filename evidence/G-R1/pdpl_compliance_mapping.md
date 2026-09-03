# VetiCare — PDPL Compliance Mapping

**Law:** Saudi Personal Data Protection Law (PDPL), effective March 2023  
**Version:** 1.0

---

## Article 4 — Lawful Basis for Processing

| Data Processing Activity | Lawful Basis | Platform Control |
|--------------------------|-------------|-----------------|
| Pet health record access by vet | Consent (`consent.granted`) | `require_consent('clinical_care')` dependency |
| Consultation creation | Consent | Consent checked before POST /api/consultations |
| Admin access to all patient data | Legitimate interest + consent | `require_consent('platform_admin')` |
| Audit log recording | Legal obligation | Automatic — all events logged |
| Session management | Contract performance | Auth flow |
| Waitlist data collection | Consent (explicit at signup) | Waitlist form + audit event |

---

## Article 5 — Purpose Limitation

- Consent records include `purpose` field — access is limited to stated purpose
- `require_consent(purpose)` enforces this at the API level
- Changing purpose requires new consent grant (new row, new `correlation_id`)

---

## Article 6 — Data Minimisation

- Only fields necessary for clinical care are collected in `consultations`
- IBAN stored as hash only (P05 — `wps_readiness`)
- Audit log stores event metadata — no PII in `event_type` or `payload` keys beyond user_id

---

## Article 14 — Data Subject Rights

| Right | Mechanism |
|-------|-----------|
| Right of access | `GET /api/account/data-export` (stub — implement pre-launch) |
| Right to rectification | `PATCH /api/account` for non-clinical data |
| Right to erasure | `DELETE /api/account` — clinical data excluded per SFDA |
| Right to portability | Data export in JSON format |
| Right to object | Consent revocation via `POST /api/consent/revoke` |

---

## Article 29 — Cross-Border Transfers

See `data_residency_declaration.md` — infra lead to complete.

---

## Controls Summary

| Control | Status |
|---------|--------|
| Consent registry (grant/revoke) | ✓ Implemented (P03) |
| Purpose-limitation dependency | ✓ Implemented (P03) |
| Audit trail for consent events | ✓ Implemented (P03) |
| Data retention policy | ✓ Documented |
| Data residency declaration | ⚠ Awaiting infra lead |
| DSR portal | ⚠ Stub only — implement pre-launch |
| DPO appointment | ⚠ Pending — legal team |
