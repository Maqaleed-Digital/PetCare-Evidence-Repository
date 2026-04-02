PETCARE DF06
Rollback and Recovery Model

Purpose
Define the rollback expectations that must exist before first production activation.

Rollback Triggers
Health failure after deploy
Readiness failure after deploy
Critical auth regression
Critical secret/config regression
Elevated 5xx rate beyond baseline
Material business workflow failure
Operator decision from release authority

Rollback Layers
Application revision rollback
Configuration rollback
Secret version rollback
Traffic rollback to last known good revision

Rollback Preconditions
Previous known good prod revision recorded
Previous known good config reference recorded
Previous known good secret version references recorded
Backward compatibility assessed before deployment

Database Safety Rule
No release may depend on irreversible schema change without an approved restore or compensating plan.
App-first and additive migration sequencing is required.

Recovery Evidence Required
Rollback decision timestamp
Trigger reason
Target revision
Operator identity
Verification result after rollback
Incident reference if applicable

Success Condition
Service health restored
Service readiness restored
Auth model intact
No unintended exposure introduced
Evidence captured
