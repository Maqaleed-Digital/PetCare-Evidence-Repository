PETCARE-PRODUCTION-ENVIRONMENT-READINESS-AND-DEPLOYMENT-CONTROLS
RELEASE_APPROVAL_WORKFLOW

Purpose
Define the named approval path for production release authorization.

Workflow
1. Build complete
2. Validation complete
3. Evidence pack generated
4. Release request assembled
5. Approval granted
6. Deployment executed
7. Post-deploy verification complete
8. Release closed

Required Approval Fields
- release version
- source commit hash
- approver name
- deploy operator
- environment
- change window
- linked evidence path
- rollback readiness confirmed

Separation Rules
- approver and deploy operator should be distinct for protected releases
- no production self-approval
- no release without linked evidence

Decision Outcomes
- approved
- approved with conditions
- rejected
- deferred

Approval Exit Criteria
- all required files present
- readiness validation pass
- go-live gate pass
- rollback runbook present
