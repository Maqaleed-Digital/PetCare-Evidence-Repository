#!/bin/bash
set -euo pipefail

TIMESTAMP="$(date -u +"%Y%m%dT%H%M%SZ")"
ROOT_DIR="/Users/waheebmahmoud/dev/petcare-evidence-repository"
RUN_DIR="$ROOT_DIR/petcare_execution/EVIDENCE/PETCARE-PH6-2-FIRST-REAL-USER-JOURNEY-VALIDATION/$TIMESTAMP"

mkdir -p "$RUN_DIR"

echo "PETCARE PH6.2 FIRST REAL USER JOURNEY VALIDATION" > "$RUN_DIR/summary.txt"
echo "TIMESTAMP=$TIMESTAMP" >> "$RUN_DIR/summary.txt"
echo "SOURCE_OF_TRUTH_COMMIT=$(git -C "$ROOT_DIR" rev-parse --short HEAD)" >> "$RUN_DIR/summary.txt"
echo "DOMAIN=https://myveticare.com" >> "$RUN_DIR/summary.txt"
echo "" >> "$RUN_DIR/summary.txt"

check_route() {
  local name="$1"
  local path="$2"
  local base="$RUN_DIR/$name"
  curl -sS -D "$base.headers.txt" -o "$base.body.html" "https://myveticare.com$path" || true
  echo "$name $path" >> "$RUN_DIR/routes_checked.txt"
}

check_route "home" "/"
check_route "signin" "/signin"
check_route "onboarding" "/onboarding"
check_route "unauthorized" "/unauthorized"
check_route "vet" "/vet"
check_route "owner" "/owner"
check_route "pharmacy" "/pharmacy"
check_route "admin" "/admin"

{
  echo "EXPECTED RESULTS"
  echo "home public"
  echo "signin public"
  echo "onboarding public"
  echo "unauthorized public branded"
  echo "vet protected"
  echo "owner protected or role-resolved entry"
  echo "pharmacy protected"
  echo "admin protected"
} > "$RUN_DIR/expectations.txt"

{
  echo "MANUAL FOLLOW-UP REQUIRED FOR AUTHENTICATED JOURNEYS"
  echo "J-06 Authenticated Owner Resolution"
  echo "J-07 Authenticated Vet Resolution"
  echo "J-08 Authenticated Admin Resolution"
  echo "Record actual role-based browser outcomes in this run directory after live validation."
} > "$RUN_DIR/manual_follow_up.txt"

find "$RUN_DIR" -type f -exec shasum -a 256 {} \; | sort > "$RUN_DIR/MANIFEST.sha256"

echo "RUN COMPLETE" >> "$RUN_DIR/summary.txt"
echo "EVIDENCE_RUN_DIR=$RUN_DIR" >> "$RUN_DIR/summary.txt"

printf '%s\n' "$RUN_DIR"
