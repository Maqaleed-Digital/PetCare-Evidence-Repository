# Release Tagging Policy (Production)

## Purpose
Define how production releases are tagged and verified to prevent accidental or unauthorized deployment.

## Tag Format
- Tags MUST follow: `petcare-prod-YYYYMMDD.N` (example: `petcare-prod-20260226.1`)
- Tag MUST point to an exact commit SHA (annotated tags recommended)

## Requirements
- Tag MUST exist in git history (`git rev-parse <tag>` succeeds)
- Tag MUST resolve to a commit object (not a lightweight ref to non-commit)
- Tag MUST be on the intended branch tip OR explicitly approved (documented in attestation report)

## Provenance
A production release attestation MUST include:
- Tag name
- Resolved commit SHA
- `git describe --tags --always` output
- Clean working tree confirmation
- CI gates PASS confirmation

## Prohibitions
- No deployment from untagged commits
- No deployment from dirty working tree
- No deployment if drift checks fail
