#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/Users/waheebmahmoud/dev/petcare-evidence-repository"
PACK_ROOT="$REPO_ROOT/petcare_execution/PHASE2/GCP_FOUNDATION_DF01"
EVIDENCE_ROOT="$REPO_ROOT/petcare_execution/EVIDENCE/PETCARE-PHASE-2-GCP-FOUNDATION-DF01"
UTC_NOW="${UTC_NOW:-$(date -u +"%Y%m%dT%H%M%SZ")}"
RUN_DIR="$EVIDENCE_ROOT/$UTC_NOW"

mkdir -p "$RUN_DIR"

ORG_ID="126195085761"
FOLDER_PLATFORM="13707960634"
FOLDER_SHARED="917191009362"
FOLDER_PROD="183275688268"
FOLDER_NONPROD="243177111666"
FOLDER_SANDBOX="165587546409"

PRJ_NET_PROD="prj-maq-network-host-prod"
PRJ_NET_NONPROD="prj-maq-network-host-nonprod"
PRJ_DNS="prj-maq-dns-shared"
PRJ_OBS="prj-maq-observability"
PRJ_KMS="prj-maq-secrets-kms"
PRJ_SANDBOX="prj-petcare-sandbox"

REGION_PRIMARY="me-central2"

if [ -z "${BILLING_ACCOUNT_ID:-}" ]; then
  echo "BILLING_ACCOUNT_ID is required" | tee "$RUN_DIR/error.txt"
  exit 1
fi

for cmd in gcloud; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "$cmd not found" | tee "$RUN_DIR/error.txt"; exit 1; }
done

gcloud config list > "$RUN_DIR/gcloud_config.txt" 2>&1
gcloud auth list > "$RUN_DIR/gcloud_auth_list.txt" 2>&1
gcloud organizations describe "$ORG_ID" > "$RUN_DIR/org_describe.json" 2>&1
gcloud resource-manager folders list --organization="$ORG_ID" > "$RUN_DIR/folders_list.txt" 2>&1

create_project() {
  local project_id="$1"
  local folder_id="$2"
  if gcloud projects describe "$project_id" >/dev/null 2>&1; then
    echo "EXISTS $project_id" | tee -a "$RUN_DIR/project_actions.txt"
  else
    gcloud projects create "$project_id" --folder="$folder_id" --name="$project_id" >> "$RUN_DIR/project_actions.txt" 2>&1
    echo "CREATED $project_id" | tee -a "$RUN_DIR/project_actions.txt"
  fi
  gcloud beta billing projects link "$project_id" --billing-account="$BILLING_ACCOUNT_ID" >> "$RUN_DIR/project_actions.txt" 2>&1
}

create_project "$PRJ_NET_PROD" "$FOLDER_PROD"
create_project "$PRJ_NET_NONPROD" "$FOLDER_NONPROD"
create_project "$PRJ_DNS" "$FOLDER_SHARED"
create_project "$PRJ_OBS" "$FOLDER_SHARED"
create_project "$PRJ_KMS" "$FOLDER_PLATFORM"
create_project "$PRJ_SANDBOX" "$FOLDER_SANDBOX"

enable_services() {
  local project_id="$1"
  shift
  gcloud services enable "$@" --project="$project_id" >> "$RUN_DIR/service_enable_${project_id}.txt" 2>&1
}

COMMON_SERVICES=(
  cloudresourcemanager.googleapis.com
  iam.googleapis.com
  compute.googleapis.com
  logging.googleapis.com
  monitoring.googleapis.com
  cloudkms.googleapis.com
  secretmanager.googleapis.com
  artifactregistry.googleapis.com
)

enable_services "$PRJ_NET_PROD" "${COMMON_SERVICES[@]}"
enable_services "$PRJ_NET_NONPROD" "${COMMON_SERVICES[@]}"
enable_services "$PRJ_DNS" dns.googleapis.com
enable_services "$PRJ_OBS" logging.googleapis.com monitoring.googleapis.com
enable_services "$PRJ_KMS" cloudkms.googleapis.com secretmanager.googleapis.com
enable_services "$PRJ_SANDBOX" "${COMMON_SERVICES[@]}"

delete_default_network() {
  local project_id="$1"
  if gcloud compute networks describe default --project="$project_id" >/dev/null 2>&1; then
    gcloud compute firewall-rules list --project="$project_id" --filter='network:default' --format='value(name)' > "$RUN_DIR/default_fw_${project_id}.txt" 2>/dev/null || true
    if [ -s "$RUN_DIR/default_fw_${project_id}.txt" ]; then
      while read -r fw; do
        [ -n "$fw" ] && gcloud compute firewall-rules delete "$fw" --project="$project_id" --quiet >> "$RUN_DIR/default_network_delete_${project_id}.txt" 2>&1 || true
      done < "$RUN_DIR/default_fw_${project_id}.txt"
    fi
    gcloud compute networks delete default --project="$project_id" --quiet >> "$RUN_DIR/default_network_delete_${project_id}.txt" 2>&1 || true
  fi
}

delete_default_network "$PRJ_NET_PROD"
delete_default_network "$PRJ_NET_NONPROD"
delete_default_network "$PRJ_SANDBOX"

create_vpc_and_subnet() {
  local project_id="$1"
  local vpc_name="$2"
  local subnet_name="$3"
  local subnet_range="$4"

  if ! gcloud compute networks describe "$vpc_name" --project="$project_id" >/dev/null 2>&1; then
    gcloud compute networks create "$vpc_name" --project="$project_id" --subnet-mode=custom --bgp-routing-mode=regional >> "$RUN_DIR/network_create_${project_id}.txt" 2>&1
  fi

  if ! gcloud compute networks subnets describe "$subnet_name" --project="$project_id" --region="$REGION_PRIMARY" >/dev/null 2>&1; then
    gcloud compute networks subnets create "$subnet_name" \
      --project="$project_id" \
      --network="$vpc_name" \
      --region="$REGION_PRIMARY" \
      --range="$subnet_range" \
      --enable-private-ip-google-access \
      --enable-flow-logs \
      --logging-aggregation-interval=interval-5-sec \
      --logging-flow-sampling=0.5 \
      --logging-metadata=include-all >> "$RUN_DIR/network_create_${project_id}.txt" 2>&1
  fi
}

create_vpc_and_subnet "$PRJ_NET_PROD" "vpc-petcare-prod" "snet-petcare-prod-mec2" "10.10.0.0/20"
create_vpc_and_subnet "$PRJ_NET_NONPROD" "vpc-petcare-nonprod" "snet-petcare-nonprod-mec2" "10.20.0.0/20"
create_vpc_and_subnet "$PRJ_SANDBOX" "vpc-petcare-sandbox" "snet-petcare-sandbox-mec2" "10.30.0.0/20"

create_firewall_baseline() {
  local project_id="$1"
  local vpc_name="$2"
  local rule_name="$3"
  if ! gcloud compute firewall-rules describe "$rule_name" --project="$project_id" >/dev/null 2>&1; then
    gcloud compute firewall-rules create "$rule_name" \
      --project="$project_id" \
      --network="$vpc_name" \
      --direction=EGRESS \
      --priority=1000 \
      --action=ALLOW \
      --rules=tcp,udp,icmp \
      --destination-ranges=0.0.0.0/0 \
      --enable-logging >> "$RUN_DIR/firewall_create_${project_id}.txt" 2>&1
  fi
}

create_firewall_baseline "$PRJ_NET_PROD" "vpc-petcare-prod" "fw-petcare-prod-egress-allow"
create_firewall_baseline "$PRJ_NET_NONPROD" "vpc-petcare-nonprod" "fw-petcare-nonprod-egress-allow"
create_firewall_baseline "$PRJ_SANDBOX" "vpc-petcare-sandbox" "fw-petcare-sandbox-egress-allow"

create_service_account() {
  local project_id="$1"
  local sa_name="$2"
  local sa_desc="$3"
  if ! gcloud iam service-accounts describe "${sa_name}@${project_id}.iam.gserviceaccount.com" --project="$project_id" >/dev/null 2>&1; then
    gcloud iam service-accounts create "$sa_name" --project="$project_id" --display-name="$sa_name" --description="$sa_desc" >> "$RUN_DIR/service_accounts_${project_id}.txt" 2>&1
  fi
}

create_service_account "$PRJ_NET_PROD" "sa-petcare-net-prod" "PetCare prod network service account"
create_service_account "$PRJ_NET_NONPROD" "sa-petcare-net-nonprod" "PetCare nonprod network service account"
create_service_account "$PRJ_DNS" "sa-petcare-dns" "PetCare shared DNS service account"
create_service_account "$PRJ_OBS" "sa-petcare-obs" "PetCare observability service account"
create_service_account "$PRJ_KMS" "sa-petcare-kms" "PetCare KMS service account"

apply_group_role() {
  local resource_type="$1"
  local resource_id="$2"
  local member="$3"
  local role="$4"
  gcloud "$resource_type" add-iam-policy-binding "$resource_id" --member="$member" --role="$role" >> "$RUN_DIR/iam_bindings.txt" 2>&1 || true
}

if [ -n "${GCP_PETCARE_PLATFORM_ADMINS_GROUP:-}" ]; then
  apply_group_role projects "$PRJ_OBS" "group:${GCP_PETCARE_PLATFORM_ADMINS_GROUP}" "roles/viewer"
fi

if [ -n "${GCP_PETCARE_NETWORK_ADMINS_GROUP:-}" ]; then
  apply_group_role projects "$PRJ_NET_PROD" "group:${GCP_PETCARE_NETWORK_ADMINS_GROUP}" "roles/compute.networkAdmin"
  apply_group_role projects "$PRJ_NET_NONPROD" "group:${GCP_PETCARE_NETWORK_ADMINS_GROUP}" "roles/compute.networkAdmin"
  apply_group_role projects "$PRJ_SANDBOX" "group:${GCP_PETCARE_NETWORK_ADMINS_GROUP}" "roles/compute.networkAdmin"
fi

if [ -n "${GCP_PETCARE_SECURITY_ADMINS_GROUP:-}" ]; then
  apply_group_role projects "$PRJ_KMS" "group:${GCP_PETCARE_SECURITY_ADMINS_GROUP}" "roles/cloudkms.admin"
  apply_group_role projects "$PRJ_KMS" "group:${GCP_PETCARE_SECURITY_ADMINS_GROUP}" "roles/secretmanager.admin"
fi

if ! gcloud kms keyrings describe "kr-petcare-mec2" --location="$REGION_PRIMARY" --project="$PRJ_KMS" >/dev/null 2>&1; then
  gcloud kms keyrings create "kr-petcare-mec2" --location="$REGION_PRIMARY" --project="$PRJ_KMS" >> "$RUN_DIR/kms_actions.txt" 2>&1
fi

create_kms_key() {
  local key_name="$1"
  if ! gcloud kms keys describe "$key_name" --location="$REGION_PRIMARY" --keyring="kr-petcare-mec2" --project="$PRJ_KMS" >/dev/null 2>&1; then
    gcloud kms keys create "$key_name" --location="$REGION_PRIMARY" --keyring="kr-petcare-mec2" --purpose=encryption --rotation-period="90d" --next-rotation-time="$(python3 - <<PY
from datetime import datetime, timedelta, timezone
print((datetime.now(timezone.utc)+timedelta(days=90)).replace(microsecond=0).isoformat().replace('+00:00','Z'))
PY
)" --project="$PRJ_KMS" >> "$RUN_DIR/kms_actions.txt" 2>&1
  fi
}

create_kms_key "key-petcare-storage"
create_kms_key "key-petcare-db"
create_kms_key "key-petcare-secrets"
create_kms_key "key-petcare-artifacts"

gcloud projects describe "$PRJ_NET_PROD" > "$RUN_DIR/project_${PRJ_NET_PROD}.json" 2>&1
gcloud projects describe "$PRJ_NET_NONPROD" > "$RUN_DIR/project_${PRJ_NET_NONPROD}.json" 2>&1
gcloud projects describe "$PRJ_DNS" > "$RUN_DIR/project_${PRJ_DNS}.json" 2>&1
gcloud projects describe "$PRJ_OBS" > "$RUN_DIR/project_${PRJ_OBS}.json" 2>&1
gcloud projects describe "$PRJ_KMS" > "$RUN_DIR/project_${PRJ_KMS}.json" 2>&1
gcloud projects describe "$PRJ_SANDBOX" > "$RUN_DIR/project_${PRJ_SANDBOX}.json" 2>&1

gcloud compute networks list --project="$PRJ_NET_PROD" > "$RUN_DIR/networks_${PRJ_NET_PROD}.txt" 2>&1
gcloud compute networks list --project="$PRJ_NET_NONPROD" > "$RUN_DIR/networks_${PRJ_NET_NONPROD}.txt" 2>&1
gcloud compute networks list --project="$PRJ_SANDBOX" > "$RUN_DIR/networks_${PRJ_SANDBOX}.txt" 2>&1

gcloud kms keyrings list --location="$REGION_PRIMARY" --project="$PRJ_KMS" > "$RUN_DIR/kms_keyrings.txt" 2>&1
gcloud kms keys list --location="$REGION_PRIMARY" --keyring="kr-petcare-mec2" --project="$PRJ_KMS" > "$RUN_DIR/kms_keys.txt" 2>&1

find "$PACK_ROOT" -maxdepth 1 -type f | sort > "$RUN_DIR/file_listing.txt"
git -C "$REPO_ROOT" status --short > "$RUN_DIR/post_execution_git_status.txt"
