#!/bin/bash
set -euo pipefail

TIMESTAMP="$(date -u +"%Y%m%dT%H%M%SZ")"
ROOT_DIR="/Users/waheebmahmoud/dev/petcare-evidence-repository"
RUN_DIR="$ROOT_DIR/petcare_execution/EVIDENCE/PETCARE-PH6-3-CONTROLLED-PILOT-CREDENTIAL-ISSUANCE/$TIMESTAMP"

mkdir -p "$RUN_DIR"

echo "PETCARE PH6.3 CONTROLLED PILOT CREDENTIAL ISSUANCE + AUTHENTICATED ROLE JOURNEY VALIDATION" > "$RUN_DIR/summary.txt"
echo "TIMESTAMP=$TIMESTAMP" >> "$RUN_DIR/summary.txt"
echo "SOURCE_OF_TRUTH_COMMIT=$(git -C "$ROOT_DIR" rev-parse --short HEAD)" >> "$RUN_DIR/summary.txt"
echo "DOMAIN=https://myveticare.com" >> "$RUN_DIR/summary.txt"
echo "" >> "$RUN_DIR/summary.txt"

cat > "$RUN_DIR/issuance_register_template.txt" <<'EOT'
issuance_id=
issued_at_utc=
issued_by=
participant_real_name=
participant_role=
participant_email=
participant_entity=
clinic_id_or_platform_scope=
approval_reference=
credential_delivery_method=
first_login_required=
password_reset_required=
mfa_status=
account_status=
validation_status=
notes=
EOT

cat > "$RUN_DIR/authenticated_validation_template.txt" <<'EOT'
A-01 OWNER
credential_issued=
first_login_completed=
resolved_route=
wrong_role_access=
notes=

A-02 VET
credential_issued=
first_login_completed=
resolved_route=
wrong_role_access=
notes=

A-03 ADMIN
credential_issued=
first_login_completed=
resolved_route=
wrong_role_access=
notes=
EOT

curl -sS -D "$RUN_DIR/signin.headers.txt" -o "$RUN_DIR/signin.body.html" "https://myveticare.com/signin" || true
curl -sS -D "$RUN_DIR/unauthorized.headers.txt" -o "$RUN_DIR/unauthorized.body.html" "https://myveticare.com/unauthorized" || true

{
  echo "MANUAL LIVE FOLLOW-UP REQUIRED"
  echo "Issue controlled real credentials only"
  echo "Complete owner, vet, and admin first-login validation"
  echo "Record resolved routes and wrong-role outcomes"
  echo "Do not use prototype/demo accounts as governed pilot evidence"
} > "$RUN_DIR/manual_follow_up.txt"

find "$RUN_DIR" -type f -exec shasum -a 256 {} \; | sort > "$RUN_DIR/MANIFEST.sha256"

echo "RUN COMPLETE" >> "$RUN_DIR/summary.txt"
echo "EVIDENCE_RUN_DIR=$RUN_DIR" >> "$RUN_DIR/summary.txt"

printf '%s\n' "$RUN_DIR"
