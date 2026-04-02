PETCARE DF10
Production Exposure Policy

Principle
Production is private-by-default.
Public exposure is blocked unless explicitly approved, evidence-backed, and reversible.

Exposure Modes
1. PRIVATE_ONLY
2. CONTROLLED_PUBLIC_SIMULATION
3. CONTROLLED_PUBLIC_APPROVED

Rules
PRIVATE_ONLY is the default mode.
CONTROLLED_PUBLIC_SIMULATION may validate the exposure path without modifying real production exposure.
CONTROLLED_PUBLIC_APPROVED requires explicit approval and evidence, and remains a contract only until a later live execution phase is authorized.

Required Approval Variables for Public Exposure Path
PETCARE_PUBLIC_EXPOSURE_APPROVED=true
PETCARE_PUBLIC_EXPOSURE_CHANGE_REF must be non-empty
PETCARE_PUBLIC_EXPOSURE_ROLLBACK_PLAN must be non-empty

Blocked Conditions
Missing public exposure approval
Missing change reference
Missing rollback plan
Failure in DF09 controlled activation path
Failure in evidence generation

Governance Result
DF10 does not expose production publicly.
DF10 establishes the enforced control surface and policy for later approved execution.
