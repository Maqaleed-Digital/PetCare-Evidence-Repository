PetCare — PETCARE-AI-LIVE-1
Controlled Pilot Activation and Live Evidence Capture

Purpose

Establish the controlled live pilot execution layer for PetCare AI.

Scope

• pilot activation plan
• clinic activation checklist
• human approval enforcement contract
• kill-switch drill contract
• live evidence capture contract
• validation pack
• deterministic evidence generation

Architecture Alignment

This stage sits above:

PETCARE-AI-FND
PETCARE-AI-INT
PETCARE-AI-OPS

It operationalizes approved AI usage without changing runtime behavior.

Safety Guarantees

• AI remains assistive-only
• human approval remains mandatory
• kill-switch remains available
• rollback remains available
• only approved pilot clinics may activate

Determinism Rules

• no randomness
• no network calls
• deterministic governance artifact generation
• no mutation of validated PH runtimes

Stop Condition

If pilot activation requires mutation of protected runtime or governance zones:

STOP execution
Create STOP_REPORT.md
Document required change
