#!/bin/bash
set -euo pipefail

TIMESTAMP="$(date -u +"%Y%m%dT%H%M%SZ")"
ROOT_DIR="/Users/waheebmahmoud/dev/petcare-evidence-repository"
RUN_DIR="$ROOT_DIR/petcare_execution/EVIDENCE/PETCARE-PH6-4-FIRST-CONTROLLED-PILOT-WORKFLOW-EXECUTION/$TIMESTAMP"

mkdir -p "$RUN_DIR"

echo "PETCARE PH6.4 FIRST CONTROLLED PILOT WORKFLOW EXECUTION" > "$RUN_DIR/summary.txt"
echo "TIMESTAMP=$TIMESTAMP" >> "$RUN_DIR/summary.txt"
echo "SOURCE_OF_TRUTH_COMMIT=$(git -C "$ROOT_DIR" rev-parse --short HEAD)" >> "$RUN_DIR/summary.txt"
echo "DOMAIN=https://myveticare.com" >> "$RUN_DIR/summary.txt"
echo "WORKFLOW=appointment->consultation->sign-off->prescription_or_controlled_outcome" >> "$RUN_DIR/summary.txt"
echo "" >> "$RUN_DIR/summary.txt"

cat > "$RUN_DIR/role_participation_template.txt" <<'EOT'
workflow_run_id=
executed_at_utc=
owner_account_email=
owner_entity_reference=
vet_account_email=
vet_entity_reference=
admin_account_email=
admin_scope_reference=
appointment_reference=
consultation_reference=
signoff_reference=
prescription_or_outcome_reference=
audit_reference=
validation_status=
notes=
EOT

cat > "$RUN_DIR/workflow_validation_template.txt" <<'EOT'
W-01 APPOINTMENT
owner_authenticated=
route_verified=
appointment_completed=
audit_captured=
notes=

W-02 CONSULTATION
vet_authenticated=
route_verified=
consultation_completed=
audit_captured=
notes=

W-03 SIGN-OFF
vet_authenticated=
signoff_completed=
human_control_preserved=
audit_captured=
notes=

W-04 PRESCRIPTION_OR_CONTROLLED_OUTCOME
completed=
audit_captured=
notes=

W-05 GOVERNANCE_OVERSIGHT
admin_available=
wrong_role_access=
exception_recorded=
notes=
EOT

curl -sS -D "$RUN_DIR/signin.headers.txt" -o "$RUN_DIR/signin.body.html" "https://myveticare.com/signin" || true
curl -sS -D "$RUN_DIR/onboarding.headers.txt" -o "$RUN_DIR/onboarding.body.html" "https://myveticare.com/onboarding" || true
curl -sS -D "$RUN_DIR/unauthorized.headers.txt" -o "$RUN_DIR/unauthorized.body.html" "https://myveticare.com/unauthorized" || true

{
  echo "MANUAL LIVE FOLLOW-UP REQUIRED"
  echo "Use real issued owner, vet, and admin credentials only"
  echo "Execute appointment -> consultation -> sign-off -> prescription or controlled outcome through UI"
  echo "Record actual workflow references and audit references"
  echo "Do not use prototype or demo accounts as governed evidence"
} > "$RUN_DIR/manual_follow_up.txt"

find "$RUN_DIR" -type f -exec shasum -a 256 {} \; | sort > "$RUN_DIR/MANIFEST.sha256"

echo "RUN COMPLETE" >> "$RUN_DIR/summary.txt"
echo "EVIDENCE_RUN_DIR=$RUN_DIR" >> "$RUN_DIR/summary.txt"

printf '%s\n' "$RUN_DIR"
