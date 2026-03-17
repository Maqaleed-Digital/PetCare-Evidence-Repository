PETCARE-PRODUCTION-ENVIRONMENT-READINESS-AND-DEPLOYMENT-CONTROLS
BREAK_GLASS_ACCESS_PROCEDURE

Purpose
Define controlled emergency privileged access for production.

Principles
- exceptional use only
- named requestor
- named approver
- time-bounded access
- mandatory audit trail
- post-event review

Allowed Scenarios
- production outage requiring privileged intervention
- blocked deployment requiring emergency diagnostics
- security containment action
- critical secrets resolution through approved channel

Mandatory Fields
- incident identifier
- requestor
- approver
- reason
- start time
- expiry time
- systems touched
- actions taken
- review owner

Controls
- no shared accounts
- no standing privileged access
- no undocumented changes
- all break-glass sessions logged
- review required after expiry

Closure
Break-glass event is not closed until:
- access removed
- actions documented
- evidence attached
- review owner assigned
