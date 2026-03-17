PETCARE-LIVE-PRODUCTION-DEPLOYMENT-AND-VERIFICATION
LIVE_OBSERVABILITY_VERIFICATION

Purpose
Verify that production observability signals are active after deployment.

Required Signal Checks
- logs flowing
- metrics flowing
- traces flowing where configured
- alert routing reachable
- production dashboard reachable

Evidence Required
- signal name
- verification timestamp UTC
- operator name
- pass/fail
- note for degraded but non-blocking conditions

Blocking Rule
If logs or alerts are unavailable, live_verified status is blocked.
