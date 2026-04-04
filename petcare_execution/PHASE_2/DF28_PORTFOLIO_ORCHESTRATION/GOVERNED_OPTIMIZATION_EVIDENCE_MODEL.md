GOVERNED_OPTIMIZATION_EVIDENCE_MODEL — DF28

PURPOSE

Define the evidence structure required for governed portfolio orchestration and cross-unit optimization outputs.

REQUIRED RECORD FOR EACH OPTIMIZATION OUTPUT

- optimization_output_id
- output_type
- generated_timestamp
- source_of_truth_commit
- participating_units
- contributing_signal_ids
- rule_id
- policy_version
- policy_checksum_reference
- evidence_references
- explanation_summary
- approval_requirement
- output_state
- validator_result

EVIDENCE CHAIN RULES

1. every optimization output must trace to approved input signals
2. every optimization output must reference an approved orchestration rule
3. every optimization output must identify policy version and checksum context
4. every optimization output must state human approval requirement explicitly
5. every blocked optimization output must still generate an evidence record
6. every explanation summary must be reproducible from source evidence and rule logic

OUTPUT STATES

- recommended
- blocked
- restricted
- stale

VALIDATION RULES

If contributing_signal_ids are missing:
- validator_result = fail
- output_state = blocked

If rule_id is missing:
- validator_result = fail
- output_state = blocked

If evidence_references are missing:
- validator_result = fail
- output_state = blocked

If approval_requirement is missing:
- validator_result = fail
- output_state = blocked

If policy version or checksum reference is missing:
- validator_result = fail
- output_state = blocked

PORTFOLIO AUDIT POSITION

This evidence model enables:
- reproducible optimization guidance
- explainable recommendation outputs
- audit-ready orchestration traceability
- fail-closed publication control
