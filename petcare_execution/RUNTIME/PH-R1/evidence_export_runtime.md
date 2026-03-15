# evidence_export Runtime Module

Purpose
Generate governed evidence packs for regulatory and operational review.

Owns

- evidence export orchestration
- artifact packaging
- audit linkage

Does Not Own

- clinical workflows
- authorization logic

Interfaces

Consumes

- audit ledger entries
- runtime artifacts

Produces

- evidence packages
- manifest hashes

Dependencies

identity_rbac
audit_ledger

Gate Requirements

G-S1 Security Gate
G-R1 Regulatory Gate

Evidence Expectations

evidence export test packs
manifest verification
hash reproducibility tests
