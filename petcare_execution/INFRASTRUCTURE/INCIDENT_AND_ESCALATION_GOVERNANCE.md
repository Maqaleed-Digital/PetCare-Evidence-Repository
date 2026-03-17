PETCARE-PRODUCTION-HYPERCARE-AND-OPERATIONS-GOVERNANCE
INCIDENT_AND_ESCALATION_GOVERNANCE

Purpose
Define the governed incident and escalation model for production operations.

Incident Classes
- Sev-1 critical outage or patient-safety-adjacent operational blocker
- Sev-2 major degradation or significant partner/clinic disruption
- Sev-3 moderate degradation with workaround
- Sev-4 minor issue or cosmetic defect

Mandatory Incident Fields
- incident_id
- severity
- detected_at_utc
- detected_by
- incident_owner
- current_status
- affected_surface
- affected_runtime
- business_impact
- mitigation
- escalation_path
- closure_time_utc

Escalation Rules
- Sev-1 immediate incident commander assignment
- Sev-1 and Sev-2 must notify operations owner
- audit path failures escalate as blocking incidents
- AI governance path failures escalate as blocking incidents
- unresolved critical incidents must appear in daily review

Closure Rule
No incident closes without:
- owner
- mitigation summary
- root cause summary or follow-up reference
- timestamped closure record
