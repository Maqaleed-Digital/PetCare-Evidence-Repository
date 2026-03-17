PETCARE-PRODUCTION-INFRASTRUCTURE-DEPLOYMENT
SECRETS_MANAGEMENT

Purpose
Define the production secret and key handling baseline.

Secret Classes
- database credentials
- application secrets
- API provider keys
- AI provider keys
- storage credentials if required
- signing secrets
- observability tokens

Rules
- production secrets are never committed
- production secrets are never echoed in logs
- production secrets are fetched at runtime
- access is identity-scoped
- rotation plan required

Storage Pattern
- centralized secrets manager
- per-environment segregation
- key/value access scoped by runtime identity
- audit visibility for access events where supported

Rotation Policy
- defined owner per secret class
- rotation tested in non-production first
- emergency revoke path documented

Repository Policy
Allowed:
- secret names
- secret placeholders
- retrieval documentation
- validation references

Forbidden:
- real secret values
- screenshots containing secrets
- copied shell history with secrets
- production credential exports

Validation
The validation script must fail if:
- a placeholder for real secret values is replaced with a live-looking credential inside tracked files
- direct secret literals appear in infrastructure docs or scripts
