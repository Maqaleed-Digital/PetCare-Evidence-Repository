# PDPL Compliance Posture (KSA) — PetCare

**Document ID:** PETCARE-PDPL-v1
**Owner:** CEO
**Last Updated (UTC):** 2026-03-03
**Scope:** Governance + evidence repository controls and operational posture. (Product runtime controls must mirror these policies.)

## 1. Data Classification (High-level)

- **Public:** marketing content, public docs
- **Internal:** operational logs, non-sensitive governance artifacts
- **Confidential:** identifiers, customer communications, internal access logs
- **Sensitive:** health-related pet records, payment identifiers, government identifiers (if ever collected)

## 2. Core PDPL Principles Implemented

- Purpose limitation (collect only what is necessary)
- Data minimization and access control
- Retention limitation (time-bound retention + deletion)
- Integrity and confidentiality (hashes, sidecars, CI gates, controlled release)
- Auditability (evidence packs, deterministic manifests)

## 3. Access Control & Least Privilege

- GitHub branch protections and required checks enforce change control
- Release integrity checks prevent tracking secrets/env files
- Evidence artifacts are checksummed and optionally signed in higher stages

## 4. Incident Handling (PDPL-aligned)

- Follow `docs/INCIDENT_RESPONSE_PLAYBOOK.md`
- For Sev-1 security/privacy incident:
  - freeze deploy/merge
  - generate evidence pack
  - CEO notified for decision and external comms

## 5. Data Subject Rights (Operational)

Operational commitment to:
- access / correction / deletion requests (as applicable in runtime systems)
- log all requests and actions in an evidence pack for traceability

