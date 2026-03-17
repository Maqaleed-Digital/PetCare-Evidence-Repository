PETCARE-PRODUCTION-HYPERCARE-AND-OPERATIONS-GOVERNANCE
LIVE_ISSUE_TRIAGE_AND_SEVERITY_MODEL

Purpose
Define the live issue triage and severity model for governed production operations.

Severity Dimensions
- user impact
- clinic or pharmacy impact
- regulatory or audit impact
- AI governance impact
- operational workaround availability
- urgency

Decision Rules
- any audit-path outage is at least Sev-2
- any AI governance path outage is at least Sev-2
- any complete runtime outage is Sev-1
- any cosmetic-only issue with no operational impact is Sev-4

Triage Outputs
- severity
- owner
- target response window
- target mitigation window
- review inclusion flag

Rule
Every live issue must receive an explicit severity and owner before it can leave intake.
