PETCARE DF10
Traffic Control Contract

Purpose
Define the traffic-control decision model for production exposure.

Traffic States
1. BLOCK_ALL_PUBLIC
2. PRIVATE_VERIFIED
3. CONTROLLED_PUBLIC_SIMULATION
4. CONTROLLED_PUBLIC_APPROVED

Allowed Transition Order
BLOCK_ALL_PUBLIC -> PRIVATE_VERIFIED
PRIVATE_VERIFIED -> CONTROLLED_PUBLIC_SIMULATION
CONTROLLED_PUBLIC_SIMULATION -> CONTROLLED_PUBLIC_APPROVED

Forbidden Transitions
BLOCK_ALL_PUBLIC -> CONTROLLED_PUBLIC_APPROVED without prior governed checks
PRIVATE_VERIFIED -> uncontrolled public exposure
Any state transition without evidence generation

Required Preconditions
DF08 workflow must pass
DF09 controlled activation path must pass
Evidence path must be configured
Rollback plan must be recorded for public path

Fail-Closed Conditions
Any missing prerequisite blocks transition
Any missing approval blocks public path
Any evidence failure blocks transition
Any missing rollback plan blocks public path

Governance Result
Traffic control remains deterministic, staged, and reversible.
