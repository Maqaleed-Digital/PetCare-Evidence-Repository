# Deployment Proof — PetCare (PH-L7)

**Document ID:** PETCARE-DEPLOY-PROOF-v1
**Owner:** Platform Ops
**Last Updated (UTC):** 2026-03-03

## Goal
Prove that a deployed runtime satisfies the PH-L6 health contract:

- `GET /health` → 200 + JSON `{status:"ok", ts_utc, ...}`
- `GET /ready` → 200 + JSON `{status:"ready", deps:{...}, ts_utc}`

## Evidence captured (PH-L7 closure pack)
- DNS resolution (hostname → IPs)
- `curl -v` TLS + headers evidence for `/health` and `/ready`
- timing metrics (namelookup/connect/appconnect/starttransfer/total)
- contract validation (JSON schema checks)

## Operator input (no guessing)
PH-L7 requires:

- `PETCARE_BASE_URL="https://<your-domain>"`

Example:
- `PETCARE_BASE_URL="https://api.petcare.sa"`
