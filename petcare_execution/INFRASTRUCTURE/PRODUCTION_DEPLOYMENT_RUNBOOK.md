PETCARE-PRODUCTION-ENVIRONMENT-READINESS-AND-DEPLOYMENT-CONTROLS
PRODUCTION_DEPLOYMENT_RUNBOOK

Purpose
Define the governed production deployment sequence.

Deployment Preconditions
- source-of-truth commit recorded
- working tree clean
- validation scripts pass
- evidence pack generation ready
- release approver named
- change window identified
- rollback path confirmed
- observability dashboards available
- on-call ownership confirmed

Deployment Sequence
1. Confirm baseline
- verify HEAD matches approved commit
- verify no uncommitted changes
- verify deployment request references evidence path

2. Pre-deploy controls
- run readiness validation
- verify environment variable contract completeness
- verify secrets references resolve through approved secret system
- verify release approval captured

3. Deploy
- deploy web runtime
- deploy API runtime
- deploy worker runtime
- apply controlled config bindings
- do not bypass approved gateway or runtime identity controls

4. Immediate post-deploy checks
- health endpoint pass
- database connectivity pass
- object storage connectivity pass
- audit event write path pass
- AI logging path pass
- alert pipeline healthy

5. Release confirmation
- capture release version
- record deployer identity
- record approver identity
- record evidence run directory
- record go-live gate result

6. Closeout
- attach evidence artifacts
- publish final commit hash as source of truth
- mark pack done only if post-deploy verification passes

Prohibited Actions
- direct production hotfix outside governed path
- manual secret injection into tracked files
- production deploy without rollback readiness
- self-approval of protected release
