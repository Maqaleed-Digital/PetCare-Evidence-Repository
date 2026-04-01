PETCARE PHASE 2
DF-01 GCP Foundation Setup
Status: LOCKED

1. Objective

Provision the governed GCP foundation for PetCare using the existing organization and folder model.

2. Deployment Scope

Included:
- project creation
- billing linkage
- API enablement
- IAM baseline groups and service accounts
- shared DNS, observability, KMS projects
- prod and nonprod network host projects
- VPC creation
- subnet creation
- firewall baseline
- flow logs
- org audit logging baseline
- KMS keyring and keys
- Secret Manager enablement
- Artifact Registry enablement
- evidence capture

Excluded:
- workload deployment
- Cloud Run services
- GKE clusters
- Cloud SQL instances
- production application release
- sandbox workload deployment
- CI/CD pipeline rollout

3. Locked Environment Model

Folders:
- Platform
- Shared Services
- Production
- Non-Production
- Sandbox

Projects:
- prj-maq-network-host-prod
- prj-maq-network-host-nonprod
- prj-maq-dns-shared
- prj-maq-observability
- prj-maq-secrets-kms
- prj-petcare-sandbox

4. Governance Rules

Must remain true:
- no shared credentials across environments
- no shared VPC between sandbox and production
- no sandbox to production routing
- no sandbox access to production data stores
- no hidden project creation outside declared structure
- no direct production write path from sandbox

5. Region Strategy

Primary region:
- me-central2

Secondary region:
- left as variable for later DR activation

6. DF-01 Result

This pack creates the cloud control plane and environment baseline only.
