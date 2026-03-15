PetCare — PETCARE-AI-INT-4
UI Surface Copilot Panels

Purpose
Expose assistive AI insights inside UI surfaces while preserving governance boundaries.

Panels

consultation_copilot_panel
triage_ai_panel
pharmacy_ai_review_panel
emergency_coordination_panel

Architecture

UI Panel
→ workflow adapter
→ agent orchestrator
→ governance runtime
→ context assembly
→ model gateway

Safety

AI outputs are advisory only.

AI cannot:
- diagnose
- prescribe
- authorize treatment
- close consultations

Human review required for all clinical decisions.
