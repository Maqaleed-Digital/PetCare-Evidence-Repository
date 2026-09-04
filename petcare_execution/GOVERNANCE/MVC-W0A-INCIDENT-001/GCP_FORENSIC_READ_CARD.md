# GCP forensic read card — for the Sponsor

The credential gate is still shut. Re-confirmed this session: `gcloud projects describe`
and `gcloud run services list` both fail with *"Reauthentication failed. cannot prompt
during non-interactive execution."* on all three stored accounts. **No login was attempted.**

Run these **read-only** commands in a real terminal after `gcloud auth login` with an
account holding viewer access to `prj-maq-petcare-prod`. Nothing here mutates.

```bash
PROJ=prj-maq-petcare-prod
REG=me-central2
SVC=petcare-api-prod

# 0. Does the project exist, and is billing/state live?
gcloud projects describe $PROJ

# 1. THE DECIDING QUESTION — is there an allUsers invoker binding?
#    This is the single read that converts PROBABLE_NOT_PROVEN into YES or NO.
gcloud run services get-iam-policy $SVC --project=$PROJ --region=$REG

# 2. Current revision + image digest actually deployed
gcloud run services describe $SVC --project=$PROJ --region=$REG \
  --format='value(status.latestReadyRevisionName,status.latestCreatedRevisionName,spec.template.spec.containers[0].image)'

# 3. Was SECRET_KEY set in the service environment? (name only — do NOT print values)
gcloud run services describe $SVC --project=$PROJ --region=$REG \
  --format='value(spec.template.spec.containers[0].env[].name)'

# 4. Revision history WITH creation dates — did any revision land after 2026-05-23?
gcloud run revisions list --service=$SVC --project=$PROJ --region=$REG \
  --format='table(metadata.name,metadata.creationTimestamp,spec.containers[0].image)' --sort-by=~metadata.creationTimestamp

# 5. Cloud Build history — same question from the build side
gcloud builds list --project=$PROJ --limit=50 \
  --format='table(id,createTime,status,source.repoSource.commitSha,images[0])'

# 6. Artifact Registry image tags and push times
gcloud artifacts docker images list --project=$PROJ \
  --include-tags --format='table(package,tags,createTime,version)' 2>/dev/null

# 7. Log retention — is the evidence still inside the window?
gcloud logging buckets list --project=$PROJ --location=global \
  --format='table(name,retentionDays,lifecycleState)'

# 8. Any anonymous request actually served? (adjust window to the revision dates from 4)
gcloud logging read \
  'resource.type="cloud_run_revision" AND resource.labels.service_name="'$SVC'"' \
  --project=$PROJ --limit=50 --freshness=400d \
  --format='table(timestamp,httpRequest.status,httpRequest.requestUrl)'

# 9. Session issuance during the window — login/auth routes
gcloud logging read \
  'resource.type="cloud_run_revision" AND resource.labels.service_name="'$SVC'" AND httpRequest.requestUrl:"/api/auth/"' \
  --project=$PROJ --limit=100 --freshness=400d \
  --format='table(timestamp,httpRequest.status,httpRequest.requestUrl)'
```

## How to read the results

| Result | Meaning |
|---|---|
| Step 1 shows `allUsers` with `roles/run.invoker` | `PUBLICLY_REACHABLE=YES` |
| Step 1 shows no `allUsers` | `PUBLICLY_REACHABLE=NO` — and the 503 was a broken revision, not an open door |
| Step 4 shows **no revision created after 2026-05-23** | `VULNERABLE_IMAGE_EXECUTED=NO` — the incident closes |
| Step 4 shows a revision after 2026-05-23 **and** step 3 lists no `SECRET_KEY` | the vulnerable default was live — escalate immediately |
| Step 4 shows a revision after 2026-05-23 **and** step 3 lists `SECRET_KEY` | the env supplied a real key; the default never applied |
| Step 7 retention shorter than the elapsed window | log evidence already expired — record `LOG_EVIDENCE_AT_RISK=REALISED` |

**Do step 1 and step 4 first.** Between them they resolve the whole question.
Do not delete the project or the service before these are read — teardown destroys
the only evidence that can close this and converts an open question into a
permanently indeterminate one.
