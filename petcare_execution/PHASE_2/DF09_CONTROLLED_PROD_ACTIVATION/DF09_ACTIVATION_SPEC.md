PETCARE DF09
Controlled Production Activation Specification

Activation Modes

1. SIMULATION (DEFAULT)
- Runs DF08 workflow
- Generates evidence
- DOES NOT activate production

2. CONTROLLED_ACTIVATION
- Requires explicit approval flag
- Requires all DF06 + DF07 + DF08 conditions satisfied
- Generates activation evidence
- Does NOT automatically expose public traffic

Required Variable

PETCARE_PROD_ACTIVATION_APPROVED=true

Rules

- Missing approval → FAIL
- DF08 must pass before activation
- Evidence must be generated

Blocked Conditions

- Approval flag missing
- DF08 workflow failure
- Evidence generation failure

Governance Result

Production activation is:
- explicit
- auditable
- controlled
- non-automatic
