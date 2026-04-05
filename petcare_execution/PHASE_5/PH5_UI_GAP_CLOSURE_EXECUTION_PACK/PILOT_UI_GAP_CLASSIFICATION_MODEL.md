Pilot UI Gap Classification Model

Purpose

Define the governed classification structure for pilot-blocking and pilot-relevant UI gaps.

Gap Classes

PGC-01
route_gap
A required pilot route is missing, broken, or non-reachable

PGC-02
workflow_gap
A pilot workflow cannot complete end-to-end

PGC-03
role_surface_gap
A required role-specific UI surface is incomplete or unavailable

PGC-04
deployment_gap
Frontend deployment, environment linkage, or route serving is not valid

PGC-05
auth_gap
Required authentication or session entry path is missing or broken

PGC-06
audit_visibility_gap
Pilot-relevant actions are not visible through required logs, panels, or evidence-linked UI path

Status Values

1. missing
2. partial
3. blocked
4. fixed_pending_validation
5. closed_validated

Universal Rule

No pilot blocker may transition to closed_validated without explicit validation evidence.
