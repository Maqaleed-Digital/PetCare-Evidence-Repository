#!/usr/bin/env bash
set -euo pipefail

: "${WEB_ROOT:?Missing WEB_ROOT}"
: "${GCP_PROJECT_ID:?Missing GCP_PROJECT_ID}"
: "${GCP_REGION:?Missing GCP_REGION}"
: "${AR_REPO:?Missing AR_REPO}"
: "${CLOUD_RUN_SERVICE:?Missing CLOUD_RUN_SERVICE}"
: "${NEXT_PUBLIC_APP_NAME:?Missing NEXT_PUBLIC_APP_NAME}"
: "${NEXT_PUBLIC_DOMAIN:?Missing NEXT_PUBLIC_DOMAIN}"
: "${NEXT_PUBLIC_API_BASE_URL:?Missing NEXT_PUBLIC_API_BASE_URL}"
: "${NEXT_PUBLIC_AUTH_MODE:?Missing NEXT_PUBLIC_AUTH_MODE}"
: "${AUTH_ISSUER:?Missing AUTH_ISSUER}"
: "${AUTH_AUDIENCE:?Missing AUTH_AUDIENCE}"
: "${SESSION_SECRET:?Missing SESSION_SECRET}"
: "${AUDIT_PROBE_ENDPOINT:?Missing AUDIT_PROBE_ENDPOINT}"

cd "$WEB_ROOT"
npm install
npm run typecheck
npm run build

IMAGE_URI="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${AR_REPO}/${CLOUD_RUN_SERVICE}:$(git -C "$WEB_ROOT/.." rev-parse --short HEAD)-$(date -u +%Y%m%d%H%M%S)"

gcloud builds submit --project "$GCP_PROJECT_ID" --tag "$IMAGE_URI" "$WEB_ROOT"

gcloud run deploy "$CLOUD_RUN_SERVICE" \
  --project "$GCP_PROJECT_ID" \
  --region "$GCP_REGION" \
  --image "$IMAGE_URI" \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "NEXT_PUBLIC_APP_NAME=${NEXT_PUBLIC_APP_NAME}" \
  --set-env-vars "NEXT_PUBLIC_DOMAIN=${NEXT_PUBLIC_DOMAIN}" \
  --set-env-vars "NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}" \
  --set-env-vars "NEXT_PUBLIC_AUTH_MODE=${NEXT_PUBLIC_AUTH_MODE}" \
  --set-env-vars "AUTH_ISSUER=${AUTH_ISSUER}" \
  --set-env-vars "AUTH_AUDIENCE=${AUTH_AUDIENCE}" \
  --set-env-vars "SESSION_SECRET=${SESSION_SECRET}" \
  --set-env-vars "AUDIT_PROBE_ENDPOINT=${AUDIT_PROBE_ENDPOINT}"

gcloud run services describe "$CLOUD_RUN_SERVICE" \
  --project "$GCP_PROJECT_ID" \
  --region "$GCP_REGION" \
  --format='value(status.url)'
