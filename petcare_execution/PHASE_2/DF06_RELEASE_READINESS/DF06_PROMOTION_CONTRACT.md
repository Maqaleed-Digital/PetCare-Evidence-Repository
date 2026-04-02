PETCARE DF06
Nonprod to Prod Promotion Contract

Purpose
Define the only allowed path for promoting PetCare from verified nonprod to production.

Allowed Promotion Path
1. Code merged to main
2. Commit pushed
3. Immutable build artifact created
4. Nonprod deploy uses the same artifact digest
5. Nonprod verification passes
6. Release authority approves promotion
7. Prod deploy uses the exact same artifact digest
8. Post-deploy verification passes
9. Evidence pack sealed

Forbidden Promotion Paths
Direct local deploy to prod
Rebuild for prod from the same commit without digest continuity
Manual code edits on server
Sandbox to prod promotion
Nonprod service account reused in prod
Production deploy without explicit approval record

Required Release Record
Source commit
Artifact digest
Nonprod revision
Target prod revision
Approver identity
Deployer identity
Verification timestamp
Rollback target revision
Evidence pack path

Authority Separation
Requestor cannot be the only approver
Deployer cannot self-approve promotion
Verifier must capture post-deploy checks

Promotion Gate
Promotion remains blocked until DF06 readiness criteria are all PASS.

Promotion Verification
Health endpoint expected healthy
Readiness endpoint expected healthy
No elevated error rate after deploy window
No auth regression
Expected secrets bound to prod runtime only
