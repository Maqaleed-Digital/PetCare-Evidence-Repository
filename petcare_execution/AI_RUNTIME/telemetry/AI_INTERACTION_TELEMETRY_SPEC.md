PetCare — PETCARE-AI-INT-5
AI Interaction Telemetry

Purpose
Capture AI interaction telemetry and clinician override signals for evaluation.

Signals Recorded
- interaction events
- clinician overrides
- agent usage metrics
- safety alerts

Architecture

UI Surface
→ telemetry collector
→ governance runtime
→ evaluation pipeline
→ evidence export

Safety
Telemetry does not grant clinical authority.
AI actions remain assistive-only.
