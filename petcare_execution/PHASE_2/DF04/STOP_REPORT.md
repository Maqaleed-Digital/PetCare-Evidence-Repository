# DF04 STOP REPORT

**Status:** BLOCKED — repo changes required before build can succeed

## Execution state

All IAM grants applied (build SA, default Cloud Build SA, Compute Engine default SA).
Source upload succeeds. Nested Cloud Build starts but buildpack fails.

## Blockers

### 1. Missing requirements.txt — HARD BLOCKER

`app/backend/` contains only `server.py`. The Google Cloud buildpack requires a
`requirements.txt` to install Python dependencies.

The app uses:
- `fastapi`
- `uvicorn` (for ASGI serving)
- `python-multipart` (FastAPI dependency)
- Any other packages imported in server.py (csv, pathlib are stdlib, os, json are stdlib)

**Required repo change:**
Create `Maqaleed-Digital/PetCare-Platform:app/backend/requirements.txt` with at minimum:
```
fastapi
uvicorn[standard]
```

### 2. Missing entrypoint declaration — FIXABLE WITHOUT REPO CHANGE

The buildpack cannot find `main.py` or `app.py`. The callable is `server:app`.

**Fix option A (no repo change):** Add `--set-env-vars=GOOGLE_ENTRYPOINT=uvicorn server:app --host 0.0.0.0 --port $$PORT` to the gcloud run deploy command in cloudbuild.nonprod.app.yaml.

**Fix option B (repo change):** Add `app/backend/Procfile`:
```
web: uvicorn server:app --host 0.0.0.0 --port $PORT
```

## IAM grants applied during this DF04 execution

| SA | Role |
|---|---|
| petcare-df03-build-sa | roles/artifactregistry.admin |
| petcare-df03-build-sa | roles/run.admin |
| petcare-df03-build-sa | roles/storage.admin |
| petcare-df03-build-sa | roles/cloudbuild.builds.editor |
| petcare-df03-build-sa | roles/serviceusage.serviceUsageConsumer |
| 823816970477@cloudbuild.gserviceaccount.com | roles/serviceusage.serviceUsageConsumer |
| 823816970477@cloudbuild.gserviceaccount.com | roles/logging.logWriter |
| 823816970477@cloudbuild.gserviceaccount.com | roles/artifactregistry.writer |
| 823816970477@cloudbuild.gserviceaccount.com | roles/storage.objectAdmin |
| 823816970477-compute@developer.gserviceaccount.com | roles/cloudbuild.builds.builder |

## Required action

Push to `Maqaleed-Digital/PetCare-Platform` on `main`:
1. Create `app/backend/requirements.txt` (minimum: `fastapi`, `uvicorn[standard]`)
2. Optionally create `app/backend/Procfile`: `web: uvicorn server:app --host 0.0.0.0 --port $PORT`

Once pushed, re-run DF04 apply with the updated cloudbuild.nonprod.app.yaml (GOOGLE_ENTRYPOINT will be set via --set-env-vars in the interim).

## Next pack

DF04 continues after repo is updated. Production contract (DF05) remains unchanged.
