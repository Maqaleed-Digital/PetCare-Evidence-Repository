GOVERNED_VISIBILITY_EVIDENCE_MODEL — DF27

PURPOSE

Define the evidence structure required for portfolio intelligence and cross-unit visibility outputs.

REQUIRED RECORD FOR EACH VISIBILITY OUTPUT

- visibility_output_id
- output_type
- generated_timestamp
- source_of_truth_commit
- participating_units
- signal_ids
- policy_version
- policy_checksum_reference
- contract_references
- source_evidence_references
- publication_state
- validator_result

EVIDENCE CHAIN RULES

1. every output must trace to one or more source evidence references
2. every output must reference current portfolio policy version
3. every output must identify participating units explicitly
4. every output must be reproducible from approved source signals
5. every blocked output must still produce an evidence record

PUBLICATION STATES

- published
- blocked
- restricted
- stale

VALIDATION RULES

If signal_ids are missing:
- validator_result = fail
- publication_state = blocked

If source_evidence_references are missing:
- validator_result = fail
- publication_state = blocked

If policy version is missing:
- validator_result = fail
- publication_state = blocked

If any contract reference required by the output is missing:
- validator_result = fail
- publication_state = blocked

PORTFOLIO AUDIT POSITION

This evidence model enables:
- portfolio-level traceability
- cross-unit visibility auditability
- reproducible intelligence outputs
- governed publication control
