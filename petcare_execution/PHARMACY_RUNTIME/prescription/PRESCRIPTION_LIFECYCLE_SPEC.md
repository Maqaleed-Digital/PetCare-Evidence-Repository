PRESCRIPTION LIFECYCLE SPEC

States:
- created
- under_review
- safety_blocked
- approved
- ready_for_dispense
- dispensed
- recalled

Requirements:
- prescription creation linked to signed clinical context
- role-controlled review and approval
- blocked prescriptions cannot move to dispense
- approved prescriptions may proceed to fulfillment
- all state transitions produce audit events
