# MVC-SQ1-PLATFORM-IDENTITY-AUDIT-001

- id: MVC-SQ1-PLATFORM-IDENTITY-AUDIT-001
- status: RATIFIED
- date: 2026-09-26
- lock: YES
- scope: AC-FR-01-03

Recorded under MVC-BUILD-RUNNER-001 v1.2 GA-1.

```
SPONSOR ACT MVC-SQ1-PLATFORM-IDENTITY-AUDIT-001 — STATUS=RATIFIED, DATE=2026-09-26, LOCK=YES, SCOPE=AC-FR-01-03
 RATIFY: Registration and failed sign-in are account actions. Pre-tenant identity/security events go to a separate
 platform identity audit chain; they must not use a fake/sentinel tenant and must not weaken the tenant-required invariant
 of tenant audit records. Failed sign-in belongs to that platform identity chain even when the targeted identity is
 associated with a tenant.
```
