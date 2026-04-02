PETCARE DF07
Environment Contract

Required for release gate check
PETCARE_RELEASE_COMMIT
PETCARE_ARTIFACT_DIGEST
PETCARE_RELEASE_APPROVER
PETCARE_DEPLOY_OPERATOR
PETCARE_ROLLBACK_TARGET
PETCARE_NONPROD_SERVICE_URL
PETCARE_PROD_SERVICE_URL
PETCARE_EVIDENCE_ROOT

Optional
PETCARE_CHANGE_RECORD
PETCARE_OBSERVATION_WINDOW_SECONDS

Required for post-deploy verification
PETCARE_VERIFY_URL
PETCARE_VERIFY_HEALTH_PATH
PETCARE_VERIFY_READY_PATH
PETCARE_EXPECT_HTTP_CODE

Default values used by scripts if not overridden
PETCARE_VERIFY_HEALTH_PATH=/health
PETCARE_VERIFY_READY_PATH=/ready
PETCARE_EXPECT_HTTP_CODE=200
PETCARE_OBSERVATION_WINDOW_SECONDS=300

Rules
All required variables must be non-empty
Artifact digest must be immutable-reference style, not latest-only
Rollback target must be explicitly recorded
Evidence root must resolve inside repository-controlled evidence paths

Fail-Closed
Any missing required variable blocks the gate.
