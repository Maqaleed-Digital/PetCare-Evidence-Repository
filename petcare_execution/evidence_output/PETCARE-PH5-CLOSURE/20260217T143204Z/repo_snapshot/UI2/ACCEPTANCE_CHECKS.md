# UI-2 Acceptance Checks

## AC-1: Key Normalization
- no absolute paths
- no .. traversal

## AC-2: Tenant Scoping
- missing tenant rejected
- cross-tenant reads rejected

## AC-3: Deterministic Listing
- list keys returns lexical order

## AC-4: Export Bundle Determinism
- FILES.txt paths sorted
- HASHES.txt sorted by path
- MANIFEST.json includes stable file list
