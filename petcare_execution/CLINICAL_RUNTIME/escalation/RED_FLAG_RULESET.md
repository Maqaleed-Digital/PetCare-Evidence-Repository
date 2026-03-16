RED FLAG RULESET

Purpose:
Define the deterministic escalation trigger model.

Escalation triggers:
- species-specific red flags
- acute deterioration indicators
- emergency safety conditions
- medication-related critical adverse signals

Rules:
- matched red flag forces escalation_required=true
- escalation path cannot be bypassed silently
- matched rule identifiers must be retained in output
