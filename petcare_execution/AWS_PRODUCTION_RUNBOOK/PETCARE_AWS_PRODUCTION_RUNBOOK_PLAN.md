# PETCARE AWS PRODUCTION RUNBOOK EXECUTION

## Purpose
Execute operator-side AWS production readiness under governed constraints.

## Critical Rule
NO infrastructure values may be invented.

## Operator Required Inputs (External Only)
- AWS account IDs
- Regions (KSA primary / DR secondary)
- VPC IDs
- Subnet IDs
- RDS identifiers
- IAM roles
- KMS keys
- Domain/DNS

## Execution Scope
- Validate AWS environment readiness (documented, not created here)
- Validate isolation model
- Validate security posture
- Validate database readiness
- Validate storage encryption
- Validate observability readiness
- Validate DR readiness

## Hard Gates

### G-RUN-1 Account & Region
- Accounts separated
- Region approved (KSA primary)

### G-RUN-2 Network
- VPC isolated
- Subnets segmented
- No public DB exposure

### G-RUN-3 Data Layer
- RDS PostgreSQL encrypted
- backups enabled
- PITR enabled

### G-RUN-4 Security
- IAM least privilege
- secrets not in repo
- KMS encryption active

### G-RUN-5 Observability
- logs enabled
- metrics enabled
- alerting defined

### G-RUN-6 DR
- RTO < 1h
- RPO < 5m
- DR region defined

## Stop Conditions
- any unknown infra value
- any attempt to guess infra
- any missing evidence
