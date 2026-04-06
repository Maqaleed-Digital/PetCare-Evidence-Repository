PETCARE-PHASE-6.2 — FIRST REAL USER JOURNEY VALIDATION

OBJECTIVE
Validate the first real browser journeys against the live PetCare production surface without weakening governance, bypassing UI, or introducing simulated protected access.

VALIDATION AREAS

1. Public Journey
- Home page loads
- Sign-in page loads
- Onboarding page loads
- Unauthorized page loads

2. Unauthorized Protection Journey
- Unauthenticated access to protected areas must not show raw JSON forbidden
- Unauthenticated access must route to a controlled unauthorized experience

3. Authenticated Owner Journey
- Authenticated owner resolves to owner-safe area
- Owner does not land in vet or admin space
- Owner journey remains UI-first and role-governed

4. Authenticated Vet Journey
- Authenticated vet resolves to vet area
- Vet sees role-appropriate workflow surface

5. Authenticated Admin Journey
- Authenticated admin resolves to admin area
- Admin sees governance-aware operational surface

NON-NEGOTIABLES
- No direct database manipulation
- No fake role assignment
- No API-only bypass in place of UI journey
- No hidden execution
- Fail-closed remains active
- Protected routes remain protected

SUCCESS CONDITION
This phase proves that the production system now supports real, governed browser journeys instead of dead-end access behavior.

OUTPUTS
- Scope file
- Validation matrix
- Deterministic evidence runner
- Evidence run directory with timestamp and SHA256 manifest
