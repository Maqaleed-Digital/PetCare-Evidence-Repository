# PH42-C Deployment Separation Model (Dev / Stage / Prod)

## Principle
Dev, Stage, and Prod are isolated environments. No shared secrets and no shared mutable state.

## Separation Rules (MUST)
- Separate secret stores per environment
- Separate API keys per environment
- Separate tenant data or datasets per environment
- Separate audit outputs per environment (no mixing prod logs with non-prod)
- Production uses immutable deploy artifacts (tagged commit or pinned digest)

## Governance Rules
- Any promotion from Stage to Prod requires:
  - Release integrity checks PASS
  - Runtime attestation recorded
  - Evidence pack zip + sha recorded
