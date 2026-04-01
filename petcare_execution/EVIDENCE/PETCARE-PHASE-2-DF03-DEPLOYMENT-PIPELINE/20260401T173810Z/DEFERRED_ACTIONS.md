DF03 DEFERRED ACTIONS

1. GitHub Cloud Build Triggers
   Status: DEFERRED — requires real GitHub repository connection
   Blocker: Placeholder values used for GITHUB_REPO_OWNER and GITHUB_REPO_NAME
   Action: Connect GitHub repository to Cloud Build at:
     https://console.cloud.google.com/cloud-build/triggers;region=me-central2/connect?project=823816970477
   Then re-run trigger creation with real owner/repo values.
   Triggers to create:
   - petcare-nonprod-main (branch: ^main$, cloudbuild.nonprod.yaml)
   - petcare-prod-release (tag: ^prod-release-.*$, cloudbuild.prod.yaml, require-approval)

2. Secret Manager Runtime Config
   Status: DEFERRED — placeholder values stored
   Action: Replace secret version 1 with real config values:
   - petcare-runtime-config-nonprod in prj-maq-petcare-nonprod
   - petcare-runtime-config-prod in prj-maq-petcare-prod

3. gcp.resourceLocations — Secret Manager fix applied in apply script
   Status: FIXED in script (--replication-policy=user-managed --locations=REGION)
   Note: apply.sh updated to use user-managed replication for future re-runs
