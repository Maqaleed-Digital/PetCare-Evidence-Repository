CONSULTATION WORKFLOW SPEC

States:
- opened
- in_progress
- ready_for_signoff
- signed
- escalated

Requirements:
- consultation opens under vet authority
- note drafting may remain draft until signoff
- signed consultation becomes immutable
- escalation path may interrupt normal closure flow
- all transitions produce audit events
