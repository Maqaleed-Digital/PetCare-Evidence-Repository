PETCARE-LIVE-PRODUCTION-DEPLOYMENT-AND-VERIFICATION
ROLLBACK_DRILL_CONFIRMATION

Purpose
Confirm rollback readiness remains real at go-live.

Required Drill Confirmation Fields
- release version
- prior stable release version
- drill confirmation date UTC
- operator name
- rollback path reference
- result
- notes

Result Values
- confirmed
- confirmed_with_conditions
- failed

Rule
No live deployment should be marked live_verified unless rollback readiness is explicitly confirmed.
