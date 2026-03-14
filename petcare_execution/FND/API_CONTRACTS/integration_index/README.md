# API Contracts — Integration Index

## Purpose

This directory is the canonical index of all inter-service API contracts in the petcare
platform foundation. It provides a single lookup point for:

- Which services expose which contract files
- Which service-to-service integrations exist
- The dependency order for standing up the foundation services

## Phase

PH-FND-3 — API Contract Artifacts

## Contract Registry

See [`CONTRACT_REGISTRY.json`](./CONTRACT_REGISTRY.json) for the machine-readable index.

## Contract Directory Structure

```
FND/API_CONTRACTS/
├── shared/
│   ├── API_CONVENTIONS.md           # HTTP conventions, auth, naming
│   ├── ERROR_CONTRACT.json          # Canonical error envelope
│   └── PAGINATION_AND_FILTERING.md # Cursor pagination + filter syntax
├── identity_rbac/
│   ├── ENDPOINTS.md
│   ├── REQUEST_RESPONSE_SCHEMA.json
│   └── AUTHORIZATION_RULES.md
├── consent_registry/
│   ├── ENDPOINTS.md
│   ├── REQUEST_RESPONSE_SCHEMA.json
│   └── PURPOSE_ENFORCEMENT.md
├── audit_ledger/
│   ├── ENDPOINTS.md
│   ├── REQUEST_RESPONSE_SCHEMA.json
│   └── AUDIT_TRIGGER_RULES.md
├── clinical_signoff/
│   ├── ENDPOINTS.md
│   ├── REQUEST_RESPONSE_SCHEMA.json
│   └── SIGNOFF_GUARDS.md
├── evidence_export/
│   ├── ENDPOINTS.md
│   ├── REQUEST_RESPONSE_SCHEMA.json
│   └── EXPORT_GUARDS.md
└── integration_index/
    ├── README.md                    # This file
    └── CONTRACT_REGISTRY.json       # Machine-readable index
```

## Dependency Startup Order

Services must start in this order to satisfy their dependencies:

1. `audit_ledger` (no service dependencies)
2. `identity_rbac` (depends on audit_ledger)
3. `consent_registry` (depends on audit_ledger, identity_rbac)
4. `clinical_signoff` (depends on audit_ledger, identity_rbac, consent_registry)
5. `evidence_export` (depends on audit_ledger, identity_rbac, consent_registry)

## Conventions Reference

All contracts in this directory conform to:
- `shared/API_CONVENTIONS.md` for HTTP method, auth, naming, and versioning rules
- `shared/ERROR_CONTRACT.json` for error response format
- `shared/PAGINATION_AND_FILTERING.md` for list endpoint behaviour
