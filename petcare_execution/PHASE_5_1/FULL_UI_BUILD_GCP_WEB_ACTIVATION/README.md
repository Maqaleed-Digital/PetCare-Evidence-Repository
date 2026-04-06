PETCARE PH5.1 — FULL UI BUILD + GCP WEB ACTIVATION

Objective
Build the governed PetCare web UI, deploy it on GCP, and block domain go-live until environment, auth, API wiring, and audit-event verification all pass.

Hard rules
- Fail closed
- No mock auth in production
- No domain go-live before verification
- Commit is the only source of truth

Primary surfaces
- Public landing
- Owner portal
- Vet portal
- Pharmacy portal
- Admin portal

Deployment target
- GCP Cloud Run
- Domain mapped only after all gates pass
