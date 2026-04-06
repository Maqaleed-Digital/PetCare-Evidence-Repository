#!/usr/bin/env bash
set -euo pipefail

: "${GCP_PROJECT_ID:?Missing GCP_PROJECT_ID}"
: "${GCP_REGION:?Missing GCP_REGION}"
: "${CLOUD_RUN_SERVICE:?Missing CLOUD_RUN_SERVICE}"
: "${DOMAIN_NAME:?Missing DOMAIN_NAME}"
: "${SERVICE_URL:?Missing SERVICE_URL}"

gcloud beta run domain-mappings create \
  --project "$GCP_PROJECT_ID" \
  --region "$GCP_REGION" \
  --service "$CLOUD_RUN_SERVICE" \
  --domain "$DOMAIN_NAME" || true

echo "Requested domain mapping for ${DOMAIN_NAME}"
echo "Service URL ${SERVICE_URL}"
