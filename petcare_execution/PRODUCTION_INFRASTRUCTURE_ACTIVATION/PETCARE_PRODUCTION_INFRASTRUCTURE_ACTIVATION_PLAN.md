# PETCARE-PRODUCTION-INFRASTRUCTURE-ACTIVATION

## Objective

Activate the production infrastructure execution layer for PetCare as a sovereign, standalone, AI-assisted, HITL-enforced, KSA-ready veterinary platform.

## Locked Execution Scope

This pack activates:
- production infrastructure activation governance
- environment isolation verification
- runtime activation checkpoints
- HITL and assistive-only AI boundary verification
- tenant isolation checkpoint
- observability and audit activation checkpoint
- fail-safe and disaster recovery checkpoint
- deterministic evidence generation

This pack does not:
- invent AWS account ids
- invent secrets
- invent domain names
- invent VPC ids
- invent RDS instance identifiers
- invent deployed resources not evidenced by operator execution

## Required Operator Inputs

The operator must confirm outside this pack:
- AWS organization and environment accounts already exist or are being provisioned by authorized infra owner
- KSA primary deployment region is approved
- UAE disaster recovery region is approved
- production secrets are managed outside source control
- production access is least-privilege and separated from non-production

## Activation Gates

### G-ACT-1 Environment Isolation
Pass conditions:
- prod, staging, dev are isolated
- no shared credentials
- no shared databases
- no cross-environment direct access

### G-ACT-2 AI Boundary Enforcement
Pass conditions:
- AI remains assistive-only
- no autonomous diagnosis
- no autonomous prescribing
- no autonomous medical finalization
- human approval enforced at required checkpoints

### G-ACT-3 Audit and Evidence
Pass conditions:
- audit trail enabled
- activation outputs recorded
- evidence manifest generated
- file hashes captured

### G-ACT-4 Tenant and Data Controls
Pass conditions:
- tenant_id discipline enforced
- RLS checkpoint documented
- PHI handling remains environment-bound
- data residency posture preserved

### G-ACT-5 Operational Readiness
Pass conditions:
- observability checkpoint documented
- rollback path documented
- fail-safe mode documented
- DR target checkpoint documented

## Activation Sequence

1. Validate baseline commit and clean working tree
2. Write authoritative activation artifacts
3. Generate local evidence bundle skeleton
4. Record activation checklist state
5. Commit and push as the new source of truth

## Stop Conditions

Stop immediately if:
- baseline commit mismatches
- working tree is dirty
- file write fails
- hash generation fails
- commit fails
- push fails

## Expected Output

- governed activation plan
- governed activation checklist
- governed activation runbook
- deterministic execution script
- evidence directory with manifest and file list
- pushed commit hash
