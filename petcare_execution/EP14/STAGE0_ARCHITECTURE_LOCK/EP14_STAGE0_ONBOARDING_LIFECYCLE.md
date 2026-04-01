PETCARE EP-14
Onboarding Lifecycle Model
Status: LOCKED

1. Lifecycle Objective

Define the governed partner lifecycle for EP-14.

2. States

INACTIVE
- default state
- no sandbox access
- no active credential use

SANDBOX_ENABLED
- sandbox credentials issued
- sandbox gateway access allowed
- production access not allowed

VALIDATING
- partner actively testing integration
- webhook replay testing allowed
- evidence collection in progress

CERTIFIED
- sandbox validation complete
- certification evidence approved
- partner eligible for later activation process
- no authority expansion granted by certification itself

ACTIVE
- partner may operate against authorized non-sandbox surfaces in a later governed phase
- still bound by EP-13 request-intake-only and governance limits

SUSPENDED
- access temporarily disabled
- investigation or remediation in progress

REVOKED
- access permanently revoked
- credentials invalidated

3. Transition Rules

INACTIVE → SANDBOX_ENABLED
- partner approved for sandbox start
- sandbox credentials created

SANDBOX_ENABLED → VALIDATING
- first successful sandbox interaction recorded

VALIDATING → CERTIFIED
- required test evidence collected
- webhook replay success confirmed
- contract conformance verified

CERTIFIED → ACTIVE
- explicit later-phase activation step only
- outside Stage 0 and outside sandbox scope

ACTIVE → SUSPENDED
- governance breach
- operational concern
- credential misuse

SUSPENDED → ACTIVE
- remediation complete
- reactivation approved

ANY STATE → REVOKED
- severe breach
- termination decision
- credential invalidation complete

4. Governance Rule

No lifecycle state grants:
- payment authority
- treasury authority
- approval authority
- production execution authority

5. Lock Result

Partner onboarding lifecycle is frozen for EP-14 Stage 0.
