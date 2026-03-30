# Tenant Isolation Policy (UI-5)

## Required
- Every API call must include x-tenant-id
- Storage keys are tenant-scoped logically (single-tenant store per request)

## Prohibited
- Cross-tenant reads
- Cross-tenant listings without tenant scope
- Any implicit tenant context

## Audit Expectations (Phase-1)
- Record boundary violations must be rejected
- Export bundle must include deterministic manifest + hashes
