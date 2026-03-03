# PetCare Incident Response Playbook

**Document ID:** PETCARE-IRP-v1
**Owner:** Platform Ops
**Last Updated (UTC):** 2026-03-03

## 1. Severity Definitions

- **Sev-1:** Production down, data integrity risk, security incident, or loss of quorum/integrity in verification index affecting release governance.
- **Sev-2:** Partial outage, degraded performance, failed deployment with quick mitigation, non-critical integrity warnings.
- **Sev-3:** Minor bug, cosmetic issue, non-blocking CI issue in non-release context.

## 2. Triage Workflow

1) **Detect:** monitoring/CI alert/user report
2) **Stabilize:** stop the bleeding (freeze deploys, block merges if needed)
3) **Validate integrity:** run release integrity + CI gates
4) **Mitigate:** rollback or hotfix (rollback preferred)
5) **Recover:** restore services, confirm integrity and quorum
6) **Postmortem:** evidence pack + corrective actions

## 3. First 15 Minutes Checklist (Sev-1)

- Announce incident internally (time started, impact)
- Freeze changes: no merges, no deploys
- Run:
  - `bash scripts/petcare_release_integrity_check.sh`
  - `bash scripts/petcare_ci_gates.sh`
- Capture outputs into an evidence pack
- Decide rollback vs fix (rollback preferred)
- Notify CEO for approval

## 4. Communications Templates

### Internal update
- Start time (UTC):
- Impact:
- Current status:
- Next update time:

### External update
- We are experiencing a service disruption.
- Status: investigating / mitigating / recovered.
- Next update time.

## 5. Post-Incident Requirements

- Root cause summary
- Evidence ZIP path + sha256
- Remediation tasks (with owners + deadlines)
- "What would have prevented this?" section
