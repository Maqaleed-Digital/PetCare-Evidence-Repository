OWNER TO APPOINTMENT FLOW

Purpose:
Define the deterministic orchestration from owner request into appointment lifecycle.

States:
- requested
- confirmed
- reschedule_requested
- cancelled
- completed

Rules:
- owner identity and pet ownership required
- clinic reference required
- booking outcome must return explicit state
- flow transitions must emit audit-compatible events
