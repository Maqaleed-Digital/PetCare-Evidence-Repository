# Security Baseline — PetCare

**Document ID:** PETCARE-SECBASE-v1
**Owner:** Platform Ops
**Last Updated (UTC):** 2026-03-03

## 1. Secrets Handling

- No secrets committed to repo (enforced by release integrity heuristic)
- No env files tracked (enforced)
- Workflows must not reference prod-like tokens (heuristic)

## 2. Change Control

- Branch protections + required checks enforced
- Policy/registry drift checks enforced
- Verification index sidecar + drift + quorum enforced

## 3. Supply Chain & Dependencies

- Lockfile determinism enforced
- pip check enforced
- compile + tests enforced in CI gates

## 4. Evidence Integrity

- Closure packs include MANIFEST + closure_sha256 + zip sha256
- Evidence size guard enforced

