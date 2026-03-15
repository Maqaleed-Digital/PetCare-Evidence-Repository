PetCare — PETCARE-AI-FND-5
Runtime Registry, Safety Event Taxonomy, and Evidence Export Hooks

Status
Implementation-ready governed registry artifact

Purpose
Introduce governed registry and evidence structures for the PetCare agentic runtime:
- runtime registry for agent/task/capability boundaries
- safety event taxonomy for blocked and review-triggering events
- evidence export hooks for deterministic AI audit packaging
- deterministic validation for registry integrity and taxonomy coverage

Architecture Alignment
This pack extends the PetCare AI runtime with:
- explicit registry governance
- explicit safety event classification
- deterministic evidence export readiness
- stable validation for runtime governance structures

Scope
In scope:
- runtime registry contract
- safety event taxonomy contract
- evidence export hook contract
- registry validation pack
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
1. runtime_registry.ts
Defines governed registry entries for:
- agent kind
- task families
- allowed capabilities
- required reviewer
- assistive-only boundary

2. safety_event_taxonomy.ts
Defines deterministic safety event classifications for:
- blocked autonomous action attempts
- override requests
- escalation-required cases
- review-required cases
- registry-policy mismatches

3. evidence_export_hooks.ts
Defines deterministic evidence export structures for:
- registry snapshot
- safety event bundle
- validation summary
- export manifest hints

4. registry_validation_pack.ts
Defines the canonical files and symbols expected for this pack.

5. registry_validation_runner.py
Runs structural validation without relying on repo-local node packages.

Required Outcomes
- runtime registry is explicit and deterministic
- safety event taxonomy is explicit and deterministic
- evidence export hooks are explicit and deterministic
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
