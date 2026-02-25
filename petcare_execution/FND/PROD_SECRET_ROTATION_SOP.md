PetCare PH42-A
Production Secret Rotation SOP
Status: Canonical for PH42-A (Operational Procedure)

1. Purpose

Define a minimum viable, regulator-grade procedure for rotating production secrets safely.

2. Scope

Applies to PROD-only credentials and keys:
- API keys and service tokens
- Database credentials
- Encryption keys (data at rest key references)
- Signing keys (bundle signing, tokens)
- Third-party integration secrets

3. Roles

- Security Owner: approves rotation windows, confirms completion
- Platform Owner: coordinates services impacted by rotation
- Operator: executes rotation steps and captures evidence

4. Rotation Frequency

- Standard: every 90 days
- Emergency: immediately upon suspected compromise or policy breach

5. Preconditions

- Confirm service inventory list exists
- Confirm rollback plan exists
- Confirm maintenance window (if needed)
- Confirm logging enabled for secret access in secret store

6. Standard Rotation Steps

Step 1: Identify secret to rotate
- Name, environment, consumers, last rotated date

Step 2: Generate replacement secret
- Use approved generator and storage method
- Store in PROD secret namespace only

Step 3: Dual-run window (if supported)
- Configure consumers to accept both old and new secret temporarily
- Validate new secret works

Step 4: Cutover
- Remove old secret from consumers
- Confirm service health

Step 5: Revoke old secret
- Revoke or delete old secret from secret store
- Confirm no consumers still access it

Step 6: Evidence
- Record rotation timestamp_utc
- Record impacted services list
- Capture validation output
- Store evidence in appropriate evidence pack (PH42-E audit binder later)

7. Emergency Rotation Steps

- Immediately revoke suspect secret
- Generate and deploy replacement
- Execute incident response runbook (PH42-E)
- Produce post-incident report with timeline and remediation

8. Minimum Evidence Template (paste-ready)

Rotation Evidence
- secret_id:
- environment: prod
- rotated_by:
- rotation_reason: scheduled | emergency
- started_utc:
- completed_utc:
- impacted_services:
- validation_summary:
- revoke_confirmed: yes | no
