PETCARE-LIVE-PRODUCTION-DEPLOYMENT-AND-VERIFICATION
LIVE_RELEASE_REGISTRATION

Purpose
Register the live production release as a governed production event.

Required Registration Fields
- release version
- deployed commit hash
- pack identifier
- production environment identifier
- release approver
- deploy operator
- deployment timestamp UTC
- evidence path
- rollback readiness status
- observability readiness status

Rules
- deployed commit hash must match the approved source commit used for deployment
- no anonymous production release
- evidence path must be captured at registration time
- rollback readiness must be explicitly confirmed
- registration must be updated if rollback occurs

Release Status Values
- approved_for_deploy
- deployed_pending_verification
- live_verified
- rolled_back
- superseded

Success Rule
A release is considered live_verified only after all live verification packs pass.
