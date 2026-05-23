# G-S1 — Security Test-Coverage Scaffold (Gap Log)

Gap tracker between the internal Phase-02 security tests already in this
repository and the **external** assurance the G-S1 gate ultimately requires.
This document is **prep only** — it does not assert G-S1 closure. The G-S1
parent `MANIFEST.json` status remains `AWAITING_HUMAN_CLOSURE`.

## Covered — internal tests

Source: `evidence/G-S1/MANIFEST.json`, `test_results.txt`, `rbac_test_log.md`,
`mfa_design.md`, `event_taxonomy.md`.

- RBAC: protected routes enforce role; 403 emits an audit event
  (Fix-F3 admin aliasing landed: `clinic_admin.viewed` + `platform_admin.viewed`
  live alongside the deprecated `admin_hub.viewed`).
- MFA design documented in `mfa_design.md`.
- Audit event taxonomy documented in `event_taxonomy.md`.
- Phase-02 security test file (`tests/test_phase02_security.py`, in the
  Emergent backend repo, not this evidence repo): 6/6 passed at the time of
  the manifest (2026-04-17). Re-verification at activation time is required.

## Not covered — external assurance still required

These categories cannot be discharged by internal unit tests. They land via
the pen-test intake structure (`pentest_intake/`) when a vendor engagement
completes.

- [ ] Network-layer probing of deployed Cloud Run services.
- [ ] Active OWASP-top-10 exercise against the production-shaped surface
      (not just route-level RBAC tests).
- [ ] Session / cookie boundary testing under realistic traffic — including
      `petcare_session` and `petcare_role` lifecycle, and the
      `x-petcare-role` header contract under hostile reuse scenarios.
- [ ] Infrastructure-misconfiguration audit — IAM least-privilege, accidental
      public surfaces, Cloud Build artefact handling, secrets in env vars
      and cloudbuild.yaml.
- [ ] Auth-issuer trust boundary (`securetoken.google.com/prj-maq-petcare-prod`)
      validated against forged tokens.
- [ ] Retest of any finding that the engineering team remediates after the
      pen test.

## Not in scope of this scaffold

- Test code changes. This file is a tracker, not a test runner.
- Asserting `status: PASS` on G-S1. Gate closure is a human decision and is
  external to engineering close-out.
- Pulling pen-test results into git. The intake structure exists; the
  artefacts arrive from the vendor through the Infrastructure Lead.
