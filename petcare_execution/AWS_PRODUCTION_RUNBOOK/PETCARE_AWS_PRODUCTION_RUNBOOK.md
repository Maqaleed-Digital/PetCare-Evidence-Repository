# AWS PRODUCTION RUNBOOK

## Execution Model
Operator executes AWS-side actions.
Repository captures governance + evidence only.

## Steps
1. Confirm AWS accounts exist
2. Confirm VPC/subnet isolation
3. Confirm RDS encryption and backups
4. Confirm S3 + KMS encryption
5. Confirm IAM least privilege
6. Confirm observability stack
7. Confirm DR setup

## Evidence Required
- ACTIVITY_LOG
- FILE_LIST
- SHA256SUMS
- MANIFEST
