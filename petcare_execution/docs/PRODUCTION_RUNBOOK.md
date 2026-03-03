# PetCare Production Runbook

**Document ID:** PETCARE-RUNBOOK-PROD-v1
**Owner:** Waheeb Ghassan Mahmoud (CEO)
**Maintainer:** Platform Ops
**Last Updated (UTC):** 2026-03-03
**Scope:** PetCare Evidence Repository governance runtime, CI gating, verification index/policy integrity.

## 1. Production Principles

- **No guessing:** If a required artifact is missing, stop and escalate.
- **Determinism:** Regenerate artifacts only through governed tooling.
- **Evidence-first:** Every intervention produces an evidence pack.
- **Rollback-first:** Prefer reverting to last known-good tag/commit over ad-hoc patching.

## 2. Production Baseline

Required invariants before any production action:

- `bash scripts/petcare_ci_gates.sh` → PASS
- `bash scripts/petcare_release_integrity_check.sh` → PASS
- Verification index sidecar + drift + quorum gates → enforced via CI

## 3. Roles & On-Call Escalation

### Escalation Matrix

| Severity | Owner | Backup | Notify |
|---|---|---|---|
| Sev-1 | Platform Ops Lead | CEO | All stakeholders |
| Sev-2 | Platform Ops Lead | Eng Lead | Key stakeholders |
| Sev-3 | Eng On-call | Platform Ops Lead | Internal only |

### Communication Channels

- Internal: (define) Slack/WhatsApp group + GitHub issue thread
- External: (define) customer notification channel (email/SMS/app banner)

## 4. Standard Operating Procedures

### 4.1 Health & Integrity Check (baseline)

Run from repo root:

- `bash scripts/petcare_release_integrity_check.sh`
- `bash scripts/petcare_ci_gates.sh`

Expected: PASS.

### 4.2 Evidence Pack Procedure (every intervention)

- Create closure pack evidence under `evidence_output/<PHASE>/`
- Ensure ZIP + `.sha256` exist
- Record commit hash and tag if applicable

## 5. Backup/Restore Reference

- PH-L2 provides `scripts/petcare_backup_create.sh` and `scripts/petcare_restore_apply.sh`
- Target RTO budget is enforced by PH-L2 closure pack.

## 6. Rollback Procedure (tabletop + operational)

### Trigger Conditions

- CI gates fail after merge to main
- Verification index quorum/integrity fails
- Release integrity check fails
- Production incident requiring immediate restoration of known-good state

### Steps (Operational)

1) Identify last known-good release tag (example pattern): `petcare-prod-YYYYMMDD.N`
2) Verify repo clean: `git status -sb`
3) Re-run CI gates on the tag:
   - `git checkout <TAG>`
   - `bash scripts/petcare_ci_gates.sh`
4) Restore main:
   - `git checkout main`

### Evidence Required

- Tag selected
- CI gates output on tag
- Decision log (why rollback, who approved)

## 7. Approvals & Sign-off

- **CEO Sign-off required** for: Sev-1 incident close, production rollback, public launch enablement.
