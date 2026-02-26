# Production Deployment Pipeline Spec (Model)

## Goal
Define a minimal production pipeline model that preserves:
- deterministic build inputs
- provenance (tag -> commit)
- artifact integrity (digest)
- safe secret handling

## Recommended Pipeline Stages
1) Select Release
- Inputs: RELEASE_TAG, RELEASE_ENV (prod/stage)
- Verify tag integrity (tag -> commit)

2) Validate Governance
- policy drift check PASS
- registry drift check PASS
- lock verify PASS
- CI gates PASS (or proof from CI run)

3) Build Artifact
- Produce artifact (container/build bundle)
- Compute sha256 digest (or image digest)
- Record digest in attestation report

4) Deploy
- Deploy artifact by digest, not by mutable tag
- Ensure prod secrets come from secret manager (not repository)

5) Post-Deploy Attestation
- Persist: tag, commit, digest, timestamp_utc, operator identity (if applicable)
- Store in controlled location (outside of this repo if sensitive)

## Non-Goals
- This repo does not implement real deployment or secret management.
- This repo only enforces integrity checks and generates deterministic evidence packs.
