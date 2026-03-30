# PetCare Execution Policy (Canonical)

This repository is evidence-driven. “Production-ready” means:
- CI gates run deterministically and pass.
- Evidence artifacts (manifest + zip + sha) are published deterministically.
- Drift of governance artifacts is detected and blocks merges.

## Guardrails
- No payments processing
- No custody of customer funds
- No AML automation
- Tenant isolation required for any multi-tenant logic
- All audit outputs must be reproducible from committed sources + locked dependencies

## CI Requirements
- `scripts/petcare_ci_gates.sh` must pass locally and in CI.
- `requirements.lock` must match `pip freeze` for the intended environment.

## Governance Drift
The following are canonical and must not drift without an explicit update:
- `POLICY.md` and `POLICY.sha256`
- `REGISTRY.json` and `REGISTRY.sha256`

Any mismatch is a CI failure.
