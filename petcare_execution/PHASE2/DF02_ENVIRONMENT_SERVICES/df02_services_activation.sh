#!/usr/bin/env bash
set -euo pipefail

RUN_DIR="${RUN_DIR:-./run}"
mkdir -p "$RUN_DIR"

PRJ_PROD="prj-maq-network-host-prod"
PRJ_NONPROD="prj-maq-network-host-nonprod"
PRJ_SANDBOX="prj-petcare-sandbox"
PRJ_SHARED="prj-maq-observability"

REGION="me-central2"

enable_services() {
  local PROJECT="$1"
  gcloud services enable \
    artifactregistry.googleapis.com \
    logging.googleapis.com \
    monitoring.googleapis.com \
    secretmanager.googleapis.com \
    --project="$PROJECT" >> "$RUN_DIR/services_$PROJECT.txt" 2>&1
}

enable_services "$PRJ_PROD"
enable_services "$PRJ_NONPROD"
enable_services "$PRJ_SANDBOX"
enable_services "$PRJ_SHARED"

create_artifact_repo() {
  local PROJECT="$1"
  local REPO="petcare-artifacts"
  gcloud artifacts repositories describe "$REPO" --project="$PROJECT" --location="$REGION" >/dev/null 2>&1 || \
  gcloud artifacts repositories create "$REPO" \
    --repository-format=docker \
    --location="$REGION" \
    --description="PetCare artifacts" \
    --project="$PROJECT" >> "$RUN_DIR/artifact_$PROJECT.txt" 2>&1
}

create_artifact_repo "$PRJ_PROD"
create_artifact_repo "$PRJ_NONPROD"
create_artifact_repo "$PRJ_SANDBOX"

gcloud logging sinks create petcare-central-logs \
  storage.googleapis.com/prj-maq-observability-logs \
  --project="$PRJ_SHARED" \
  --log-filter="severity>=ERROR" >> "$RUN_DIR/logging_sink.txt" 2>&1 || true

gcloud monitoring policies list --project="$PRJ_SHARED" \
  > "$RUN_DIR/monitoring_baseline.txt" 2>&1

echo "DF-02 COMPLETE" >> "$RUN_DIR/status.txt"
