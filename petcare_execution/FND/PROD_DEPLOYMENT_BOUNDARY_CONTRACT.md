# Production Deployment Boundary Contract

## Purpose
This contract defines the boundary between:
- Governance/Evidence Repository (this repo) and
- Production Runtime Environment / Deployment Pipeline.

It ensures releases are deterministic, traceable, and do not leak secrets.

## Contract Assertions (Must Hold)
1) Governance Drift Protected
- `scripts/petcare_policy_drift_check.sh` PASS
- `scripts/petcare_registry_drift_check.sh` PASS

2) Dependency Determinism
- `scripts/petcare_lock_verify.sh` PASS

3) CI Gates Deterministic
- `scripts/petcare_ci_gates.sh` PASS (local and CI)

4) Evidence Safety
- `evidence_output/` MUST NOT be tracked by git
- `.env*`, `env.*`, `.envrc` MUST NOT be tracked

5) Release Tag Integrity
- Production deploy MUST reference a release tag per `FND/RELEASE_TAGGING_POLICY.md`
- Tag must resolve to a specific commit SHA, recorded in attestation

6) Artifact Digest Contract (Optional but Recommended)
If a deployment artifact is used (container image / build zip / wheel):
- A digest MUST be captured (sha256) and recorded
- Artifact digest MUST be verified before deployment

## Enforcement
This repo provides scripts for enforcement:
- `scripts/petcare_release_tag_verify.sh`
- `scripts/petcare_prod_deploy_artifact_contract.sh`
