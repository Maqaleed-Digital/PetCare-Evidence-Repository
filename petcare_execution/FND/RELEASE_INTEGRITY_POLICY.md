# PH42-C Release Integrity Policy (Production-Grade)

This repository is evidence-driven. A "production release" is any deployable artifact promoted to a production runtime.

## Objectives
- Prevent silent drift of governance artifacts.
- Prevent dependency drift by enforcing lock determinism.
- Ensure secrets are never committed.
- Ensure the release can be verified from committed sources and deterministic evidence packs.

## Release Preconditions (MUST)
- `POLICY.md` matches `POLICY.sha256`
- `REGISTRY.json` matches `REGISTRY.sha256`
- `requirements.lock` determinism PASS (`scripts/petcare_lock_verify.sh`)
- CI gates PASS (`scripts/petcare_ci_gates.sh`)
- Evidence contract PASS (`scripts/petcare_evidence_contract.sh`) if present
- No tracked secrets or environment files
- `evidence_output/` is ignored and not tracked

## Prohibited
- Tracking any `.env*`, `.envrc`, `env.*`, secret files, private keys, vault exports
- Referencing production secrets inside `.github/workflows/*`
- Editing governance artifacts without updating their pinned sha files

## Evidence
Any production release must have a corresponding closure pack zip + sha and a filled release attestation report.
