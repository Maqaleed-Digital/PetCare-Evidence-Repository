# PH42-C Production Runtime Attestation Spec

This spec defines the minimum set of facts that MUST be captured for a production runtime to be considered verified.

## Attestation Fields (MUST)
- timestamp_utc
- git_head (commit SHA)
- policy_sha256 (POLICY.sha256 content)
- registry_sha256 (REGISTRY.sha256 content)
- requirements_lock_sha256 (sha256 of requirements.lock)
- python_version (major.minor.micro)
- ci_required_checks_present (PASS/FAIL based on scripts/petcare_required_checks_assert.sh if present)
- release_integrity_check (PASS/FAIL based on scripts/petcare_release_integrity_check.sh)
- notes (optional)

## Storage
- Written into `EVIDENCE/PH42C_RELEASE_ATTESTATION_REPORT.md`
- A filled copy of the report is included inside the PH42-C closure pack snapshots.
