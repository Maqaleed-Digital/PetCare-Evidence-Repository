# VetiCare — Data Residency Declaration

**Reference:** PDPL Article 29 (Saudi Personal Data Protection Law)
**Status:** AWAITING INFRA LEAD COMPLETION

---

## Data Residency Inventory

*Infrastructure lead to complete before G-R1 gate closure.*

| Data Category | Primary Region | Notes |
|---------------|---------------|-------|
| Primary database (SQLite → PostgreSQL) | `[ ] _______` | |
| Object storage (documents, attachments) | `[ ] _______` | |
| Audit log storage | `[ ] _______` | |
| Backup region | `[ ] _______` | |
| CDN edge nodes | `[ ] _______` | |
| Session data / Redis | `[ ] _______` | |

---

## Cross-Border Transfer Assessment

`[ ]` Cross-border transfer justification: ___________________________

Per PDPL Article 29, personal data may only be transferred outside KSA if:
1. The destination country provides adequate data protection level, OR
2. The data subject has given explicit consent, OR
3. The transfer is necessary for the performance of a contract

---

## Declaration

I confirm that the above data residency configuration complies with
PDPL Article 29 requirements for personal data of Saudi residents.

Signed: _________________________ (Infra Lead)
Date:   _________________________

Reviewed by: _____________________ (DPO / Legal)
Date:   _________________________
