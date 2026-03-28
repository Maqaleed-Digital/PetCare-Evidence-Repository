# EP-01 RBAC ROLE MATRIX

Pack ID: PETCARE-EP01-EP02-IMPLEMENTATION-BASELINE

## 1. PHASE 1 authoritative roles

- Owner
- Veterinarian
- Pharmacy Operator
- Partner Clinic Admin
- Platform Admin

## 2. Role semantics

### Owner
Primary authority over own pet records, consent decisions, appointment actions, and owned document visibility.

### Veterinarian
Clinical access for assigned or authorized care contexts only.
May create and update consultation-linked medical content.
May review AI assistive output.
May not bypass consent and purpose limitation rules.

### Pharmacy Operator
Medication workflow access limited to approved prescription and fulfillment contexts.
No unrestricted clinical record access.

### Partner Clinic Admin
Operational access for clinic configuration, roster, availability, and clinic-scoped administrative records.
No unrestricted cross-clinic medical record access.

### Platform Admin
Platform governance and operational oversight access.
May view audit and configuration surfaces according to purpose limitation.
Must not act as a clinical decision maker by role alone.

## 3. Minimum capability matrix

| Capability | Owner | Veterinarian | Pharmacy Operator | Partner Clinic Admin | Platform Admin |
|---|---|---|---|---|---|
| View own pet profile | Yes | Authorized only | No | No | Purpose-limited only |
| Update pet profile demographics | Yes | Authorized limited update | No | No | No |
| View medical timeline | Owner-scoped | Authorized care-scoped | Limited medication-relevant only | No | Purpose-limited only |
| Create consultation notes | No | Yes | No | No | No |
| Sign clinical note | No | Yes | No | No | No |
| View prescription status | Yes for own pet | Yes | Yes for assigned workflow | Limited ops visibility | Purpose-limited only |
| Manage consent | Yes | No | No | No | No |
| View audit logs | No | Limited personal action trace only if exposed later | No | Limited operational logs later if approved | Yes |
| Export evidence | No | No | No | No | Yes |

## 4. Least-privilege rules

- default deny
- all access must be role- and purpose-bound
- tenant and clinic context must be enforced
- clinical access is not equivalent to unrestricted administrative access
- pharmacy access is workflow-limited
- platform admin access must remain governed and auditable

## 5. Enforcement baseline

Access checks must evaluate:
- role
- tenant_id
- clinic_id when applicable
- actor_id
- purpose_of_use
- consent state
- relationship to resource
- workflow state when applicable

## 6. Unauthorized path requirement

When access fails:
- return forbidden response
- record audit event
- include denial reason code internally
- do not leak protected record existence unnecessarily

## 7. Protected semantics

This file defines protected role semantics for PHASE 1.
No executor may redefine role meaning without STOP_REPORT.md.
