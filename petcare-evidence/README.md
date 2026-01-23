# PetCare KSA — Pilot Evidence Repository

## Purpose
This repository stores read-only, exported evidence from the PetCare KSA live pilot.
It is used for audit traceability, governance review, Emergent AI read-only analysis,
and Sprint-7 Scale-Up Readiness inputs.

⚠️ This repository is NOT connected to production systems.

## Governance Rules (MANDATORY)
- No production secrets
- No live database connections
- No automation or GitHub Actions triggered by AI
- No write access granted to AI systems
- All data is exported, redacted, and reviewed by humans before commit

Emergent AI access is READ-ONLY.

## Repository Structure
/pilot-evidence/
  /day-3/
  /day-4/
  /day-5/

/emergent/
  /prompts/
  /outputs/

## Access Control
Humans: Write access (limited)
Emergent AI: Read-only access (contents:read)

Any deviation from this policy is a governance violation.
