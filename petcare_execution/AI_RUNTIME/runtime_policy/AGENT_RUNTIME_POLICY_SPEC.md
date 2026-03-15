PetCare — PETCARE-AI-FND-6
Runtime Policy Bundles, Prompt Registry Binding, and Audit Bundle Export

Status
Implementation-ready governed runtime policy artifact

Purpose
Introduce governed runtime policy and export structures for the PetCare agentic runtime:
- runtime policy bundles per task family
- prompt registry binding for governed template references
- audit bundle export for deterministic AI audit packaging
- deterministic validation for policy integrity and export completeness

Architecture Alignment
This pack extends the PetCare AI runtime with:
- explicit policy bundle governance
- explicit prompt registry binding
- deterministic audit bundle export readiness
- stable validation for policy and export structures

Scope
In scope:
- runtime policy bundle contract
- prompt registry binding contract
- audit bundle export contract
- policy validation pack
- Python validation runner
- evidence generation

Out of scope:
- autonomous diagnosis
- autonomous prescriptions
- autonomous treatment authorization
- autonomous consultation closure
- external network calls
- changes to validated PH runtimes
- changes to governance scripts
- changes to closure scripts

Implementation Units
1. runtime_policy_bundles.ts
Defines governed runtime policy bundles for each approved task family, including:
- assistive-only rule
- required reviewer
- required logging
- override eligibility
- blocked action classes

2. prompt_registry_binding.ts
Defines deterministic prompt template references that bind:
- task family
- agent kind
- prompt template id
- prompt schema version
- policy bundle id

3. audit_bundle_export.ts
Defines deterministic audit export structures for:
- policy bundle snapshot
- prompt binding snapshot
- registry linkage hint
- safety taxonomy linkage hint
- validation summary

4. policy_validation_pack.ts
Defines the canonical files and symbols expected for this pack.

5. policy_validation_runner.py
Runs structural validation without relying on repo-local node packages.

Required Outcomes
- runtime policy bundles are explicit and deterministic
- prompt registry binding is explicit and deterministic
- audit bundle export is explicit and deterministic
- validation succeeds without repo-local package dependency
- all outputs remain assistive only

Determinism Rules
- no randomness
- no current-time logic in governance decisions
- no hidden I/O
- no mutation of validated PH runtimes
- same input must produce same output shape

Protected Zones
Do not modify:
- consent semantics
- RBAC semantics
- audit taxonomy
- clinical sign-off immutability
- escalation referral semantics

Stop Condition
If this pack requires protected-zone semantic mutation:
- do not proceed with semantic change
- write STOP_REPORT.md
- explain exact required change and why
