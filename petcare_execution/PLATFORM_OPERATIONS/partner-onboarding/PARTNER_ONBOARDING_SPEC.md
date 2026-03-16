PARTNER ONBOARDING SPEC

Purpose:
Define the deterministic onboarding path for clinics, pharmacies, and operational partners.

States:
- created
- verification_pending
- verified
- activation_ready
- active
- rejected

Rules:
- unverified partners may not activate
- verification status must be explicitly recorded
- partner activation eligibility must be deterministic
- all verification decisions are audit compatible
