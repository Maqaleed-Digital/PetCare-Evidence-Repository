# VetiCare — Data Retention Policy

**Version:** 1.0  
**Effective Date:** 2026-04-17  
**Authority:** Programme Governor — Waheeb Mahmoud

---

## Retention Schedule

| Data Category | Retention Period | Basis |
|---------------|-----------------|-------|
| Pet health records | Lifetime of pet + 7 years | Veterinary professional standards |
| Consultation records (signed) | 10 years minimum | SFDA clinical record requirements |
| Audit logs (`audit_events` table) | 5 years minimum | Regulatory / PDPL Article 14 |
| Consent records | Indefinitely (revoked records preserved) | PDPL accountability — proof of lawful basis |
| Session tokens (`pilot_sessions`) | Purged on expiry | No retention needed after expiry |
| Waitlist data | 2 years from registration | PDPL Article 5 (purpose limitation) |
| Adverse events | 10 years | SFDA pharmacovigilance requirements |

---

## Deletion Policy

- Owner account deletion requests: handled via `DELETE /api/account`
- Clinical records (consultations, health records) are **EXCLUDED** from deletion —
  SFDA and KSA veterinary law require retention regardless of account deletion request
- Consent records: never deleted (revoked records retained as proof of historical consent)
- Audit log: never deleted — required for regulatory audit trail

---

## Automated Purge

- Expired sessions: purged by background job (daily, 02:00 UTC)
- No other automated purge is active in pilot phase

---

## PDPL Compliance Note

Retention periods are the minimum required. Data retained beyond purpose
must have documented justification per PDPL Article 5.
