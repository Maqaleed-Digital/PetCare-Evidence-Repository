# Data Retention Policy — PetCare

**Document ID:** PETCARE-RETENTION-v1
**Owner:** Platform Ops
**Last Updated (UTC):** 2026-03-03

## 1. Retention Categories (Baseline)

- **Governance artifacts (policies, registry, verification index):** retain indefinitely (audit required)
- **Evidence packs:** retain per operational budget (default: 30 days in CI artifacts; local evidence per ops policy)
- **Operational logs:** retain 30–90 days unless required for audit/incident
- **Production customer data (runtime systems):** subject to PDPL + business requirements (define per module)

## 2. Deletion & Disposal

- Evidence pruning uses governed tooling (no manual deletion for audited packs)
- For any deletion of audited material, create a "deletion evidence pack" with approvals

## 3. RTO/RPO Alignment

- Backup/restore capabilities validated in PH-L2
- Production RPO target must be defined once DB exists (future pack)

