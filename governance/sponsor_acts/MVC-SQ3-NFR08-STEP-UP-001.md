# MVC-SQ3-NFR08-STEP-UP-001

- id: MVC-SQ3-NFR08-STEP-UP-001
- status: RATIFIED
- date: 2026-09-27
- lock: YES
- scope: NFR-08

Recorded under MVC-BUILD-RUNNER-001 v1.3 GA-2.

```
ACT_ID=MVC-SQ3-NFR08-STEP-UP-001
STATUS=RATIFIED
DATE=2026-09-27
LOCK=YES
SCOPE=NFR-08

RATIFY:

Sensitive operations requiring MFA step-up are:
1. dispensing a POM product;
2. prescribing a POM product;
3. signing consultation notes;
4. signing medical records;
5. changing roles;
6. changing permissions;
7. changing tenant membership;
8. enrolling MFA;
9. resetting MFA;
10. bulk export of any data;
11. export of personal data;
12. changing payout details;
13. changing bank details;
14. issuing credentials; and
15. issuing API keys.

STEP-UP FRESHNESS:
The normal successful MFA step-up freshness window is 15 minutes.

ALWAYS-FRESH OPERATIONS:
Role changes, MFA enrolment/reset, and payout or bank-detail changes require a new successful step-up for every operation
regardless of any remaining normal 15-minute freshness window.

ENROLMENT AND RECOVERY STEP-UP:
- Where the principal has no active MFA factor (initial enrolment, or re-enrolment after a reset), MFA enrolment requires
  a successful primary re-authentication performed for that operation, in place of MFA step-up.
- Adding or replacing a factor while an active factor exists requires MFA step-up with the existing factor.
- A successful recovery-code redemption counts as one step-up event authorizing exactly one operation.

LOST-FACTOR RECOVERY:
- Issue exactly ten single-use recovery codes at MFA enrolment.
- Recovery codes are displayed to the principal once at issuance.
- Store recovery codes only in a one-way hashed representation suitable for verification.
- A recovery code is invalid after its first successful use.
- Recovery codes must never be logged in plaintext.

ADMIN-ASSISTED RESET:
- An admin-assisted MFA reset requires authorization by a second admin in the same tenant.
- The subject principal cannot act as either approving admin for their own reset.
- Successful assisted reset revokes all active sessions for the subject principal.
- Successful assisted reset requires MFA re-enrolment before sensitive operations may resume.

SMS:
SMS is not an MFA factor under this act. Do not introduce an SMS dependency for NFR-08.

SOLE-ADMIN RECOVERY:
Where a tenant has no eligible second admin, recovery is a platform-support / operations procedure. Do not invent or
implement that procedure under this act. Record it as an operations dependency, not as an internally closable NFR-08
gap, unless the ratified NFR-08 evidence definition explicitly requires its implementation.

This act does not authorize production activation, production evidence, cloud changes, credential entry, external
provider configuration, database apply, or modification of the frozen NFR requirement/evidence definition.
```
