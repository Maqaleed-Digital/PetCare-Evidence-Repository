PETCARE PHASE 2
DF-01 IAM Baseline
Status: LOCKED

Groups expected:
- gcp-petcare-org-admins
- gcp-petcare-billing-admins
- gcp-petcare-security-admins
- gcp-petcare-network-admins
- gcp-petcare-observability-admins
- gcp-petcare-platform-admins
- gcp-petcare-prod-readonly
- gcp-petcare-nonprod-admins
- gcp-petcare-sandbox-admins

Service accounts expected:
- sa-petcare-net-prod
- sa-petcare-net-nonprod
- sa-petcare-dns
- sa-petcare-obs
- sa-petcare-kms

Role model:
- least privilege
- environment separation
- no prod admin role on sandbox principals
- no sandbox principal on prod projects
- no shared service account across prod and sandbox

Manual note:
Identity group creation is handled in Google Cloud Identity or Admin Console if not already present.
This pack applies IAM bindings assuming groups exist or will exist immediately after execution.
