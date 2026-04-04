PORTFOLIO_SIGNAL_CATALOG — DF27

PURPOSE

Define the approved portfolio intelligence signals and their governance characteristics.

SIGNAL MODEL

Each signal must include:
- signal_id
- signal_name
- source_scope
- visibility_scope
- description
- provenance_requirement
- policy_reference
- publication_rule

APPROVED SIGNALS

1. unit_governance_alignment
source_scope: unit
visibility_scope: portfolio
description: indicates whether a unit matches current federated governance baseline
provenance_requirement: federated validation evidence
policy_reference: DF26 policy version control
publication_rule: publish only if current and evidenced

2. unit_evidence_completeness
source_scope: unit
visibility_scope: portfolio
description: indicates whether required evidence artifacts are present and hash-anchored
provenance_requirement: manifest plus evidence directory reference
policy_reference: evidence chain requirement
publication_rule: publish only if manifest integrity is valid

3. cross_unit_policy_alignment
source_scope: portfolio
visibility_scope: portfolio
description: indicates whether all participating units are aligned to approved policy version and checksum
provenance_requirement: per-unit policy validation references
policy_reference: checksum lock
publication_rule: block if any participating unit is mismatched

4. interoperability_contract_health
source_scope: portfolio
visibility_scope: portfolio
description: summarizes contract validity and version alignment across units
provenance_requirement: contract registry references
policy_reference: interoperability contract registry
publication_rule: publish only if all included contracts are declared and valid

5. governed_exception_summary
source_scope: portfolio
visibility_scope: portfolio
description: summarizes ratified exceptions requiring human attention
provenance_requirement: exception evidence references
policy_reference: fail-closed governance model
publication_rule: informational only, never actionable

6. resilience_posture_summary
source_scope: unit
visibility_scope: portfolio
description: summarizes last validated resilience and recovery readiness state
provenance_requirement: resilience evidence references
policy_reference: resilience validation layer
publication_rule: publish only if evidence is current

PROHIBITED SIGNALS

- autonomous action recommendation
- hidden dependency inference
- unapproved operational surveillance
- uncited cross-unit ranking
- policy override suggestion
- any signal without provenance
