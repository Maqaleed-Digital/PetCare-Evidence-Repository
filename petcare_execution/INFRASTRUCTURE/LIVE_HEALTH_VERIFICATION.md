PETCARE-LIVE-PRODUCTION-DEPLOYMENT-AND-VERIFICATION
LIVE_HEALTH_VERIFICATION

Purpose
Define the minimum live production health verification checklist.

Critical Health Checks
- public entrypoint reachable
- API health endpoint pass
- worker runtime healthy
- database connectivity pass
- object storage connectivity pass
- gateway routing healthy
- no critical startup failures

Verification Evidence
- timestamp UTC
- operator name
- environment name
- pass/fail per check
- short note for any degraded condition

Failure Rule
Any failed critical health check prevents live_verified status and requires rollback decision review.
