PETCARE-PRODUCTION-INFRASTRUCTURE-DEPLOYMENT
SECURITY_MODEL

Purpose
Capture the minimum production security model required for go-live readiness.

Security Principles
- zero trust
- least privilege
- explicit authorization
- end-to-end encryption
- immutable audit trail
- privileged access logging
- controlled break-glass

Identity Model
Human Roles
- platform admin
- clinic admin
- veterinarian
- pharmacy operator
- operations responder
- security responder

Machine Roles
- web runtime identity
- API runtime identity
- worker runtime identity
- workflow runtime identity
- CI deploy identity
- observability collector identity

Control Requirements
1. Secrets
- all secrets in secrets manager only
- no .env production values committed
- runtime fetch only

2. Keys
- KMS-backed keys
- rotation policy required
- audit log for key use where supported

3. Data
- encryption at rest
- encryption in transit
- access logs for regulated records

4. Access
- RBAC preserved
- admin separation of duties
- production write access minimized

5. Audit
- deployment actions logged
- privileged access logged
- security-relevant config changes logged

Break-Glass Rule
- emergency privileged access allowed only under named procedure
- approval and reason required
- time-bounded access
- post-event review mandatory

Security Gate Evidence
- security checklist
- network validation output
- manifest with file hashes
- deployment validation pass
