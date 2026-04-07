PETCARE — PH6 LIVE PILOT EXECUTION

Status: READY FOR CONTROLLED REAL-WORLD OPERATIONAL EXECUTION
Parent Application Source of Truth: c6e57769

Objective

Execute the first governed live pilot using real production actors and real audited workflow activity.

Required Live Scope

- 1 real clinic
- 1 to 2 real veterinarians
- 1 to 3 real owner cases
- Real credential issuance
- Real appointment
- Real consultation
- Real clinical sign-off
- Real prescription event if clinically applicable

Non-Negotiable Rules

- No demo users
- No seeded data
- No database injection
- No UI bypass
- No fake consultation
- No fake prescription
- No synthetic evidence

Authoritative Workflow

appointment → consultation → sign-off → prescription

Execution Boundary

This pack governs operational execution only.
It does not authorize product scope expansion.
It does not authorize a full i18n rebuild.
It does not authorize chain-clinic onboarding.

Success Condition

PH6 is operationally complete only when:
- real actors are enrolled
- real workflow completes
- evidence is captured
- closure summary is recorded
