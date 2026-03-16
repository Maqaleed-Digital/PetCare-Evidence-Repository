AI GOVERNANCE RUNTIME SPEC

Purpose:
Preserve assistive-only AI controls during runtime realization.

Required controls:
- prompt logging
- output logging
- model version logging
- override recording
- evaluation hook emission

Boundary rules:
- AI cannot sign medical records
- AI cannot prescribe medication
- AI cannot finalize triage decisions
- human approval required for clinical outputs
