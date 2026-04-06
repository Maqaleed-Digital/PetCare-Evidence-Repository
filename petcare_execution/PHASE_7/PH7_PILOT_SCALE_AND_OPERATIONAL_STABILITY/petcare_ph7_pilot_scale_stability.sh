#!/bin/bash
set -euo pipefail

TIMESTAMP="$(date -u +"%Y%m%dT%H%M%SZ")"
ROOT_DIR="/Users/waheebmahmoud/dev/petcare-evidence-repository"
RUN_DIR="$ROOT_DIR/petcare_execution/EVIDENCE/PETCARE-PH7-PILOT-SCALE-AND-OPERATIONAL-STABILITY/$TIMESTAMP"

mkdir -p "$RUN_DIR"

echo "PETCARE PH7 PILOT SCALE AND OPERATIONAL STABILITY" > "$RUN_DIR/summary.txt"
echo "TIMESTAMP=$TIMESTAMP" >> "$RUN_DIR/summary.txt"
echo "SOURCE_OF_TRUTH_COMMIT=$(git -C "$ROOT_DIR" rev-parse --short HEAD)" >> "$RUN_DIR/summary.txt"
echo "DOMAIN=https://myveticare.com" >> "$RUN_DIR/summary.txt"
echo "PILOT_CAP=5_CLINICS_MAX" >> "$RUN_DIR/summary.txt"
echo "" >> "$RUN_DIR/summary.txt"

cat > "$RUN_DIR/pilot_cohort_template.txt" <<'EOT'
cohort_entry_id=
created_at_utc=
clinic_id=
clinic_name=
clinic_city=
clinic_status=
vet_id=
vet_name=
vet_status=
owner_account_email=
pilot_wave=
workflow_count=
last_workflow_at_utc=
issues_observed=
notes=
EOT

cat > "$RUN_DIR/incident_register_template.txt" <<'EOT'
incident_id=
detected_at_utc=
clinic_id=
role_impacted=
journey_or_workflow_step=
severity=
description=
owner=
mitigation_action=
resolved_at_utc=
status=
evidence_reference=
notes=
EOT

cat > "$RUN_DIR/sla_register_template.txt" <<'EOT'
service_check_id=
checked_at_utc=
route_or_workflow=
expected_behavior=
observed_behavior=
status=
follow_up_required=
notes=
EOT

cat > "$RUN_DIR/workflow_stability_template.txt" <<'EOT'
S-01 PUBLIC_AVAILABILITY
home=
signin=
onboarding=
unauthorized=
notes=

S-02 PROTECTED_ACCESS_INTEGRITY
protected_routes_preserved=
raw_json_403_absent=
route_leakage=
notes=

S-03 PILOT_WORKFLOW_REPETITION
multiple_workflows_completed=
owner_access_preserved=
vet_access_preserved=
admin_oversight_available=
notes=

S-04 CLINICAL_CONTROL
human_signoff_preserved=
signoff_bypass=
wrong_role_clinical_action=
notes=

S-05 INCIDENT_VISIBILITY
incidents_logged=
severity_assigned=
owner_assigned=
mitigation_recorded=
notes=

S-06 OPERATIONAL_STABILITY
repeated_workflow_evidence=
pilot_cap_respected=
instability_notes_recorded=
notes=
EOT

curl -sS -D "$RUN_DIR/home.headers.txt" -o "$RUN_DIR/home.body.html" "https://myveticare.com/" || true
curl -sS -D "$RUN_DIR/signin.headers.txt" -o "$RUN_DIR/signin.body.html" "https://myveticare.com/signin" || true
curl -sS -D "$RUN_DIR/onboarding.headers.txt" -o "$RUN_DIR/onboarding.body.html" "https://myveticare.com/onboarding" || true
curl -sS -D "$RUN_DIR/unauthorized.headers.txt" -o "$RUN_DIR/unauthorized.body.html" "https://myveticare.com/unauthorized" || true
curl -sS -D "$RUN_DIR/vet.headers.txt" -o "$RUN_DIR/vet.body.html" "https://myveticare.com/vet" || true
curl -sS -D "$RUN_DIR/admin.headers.txt" -o "$RUN_DIR/admin.body.html" "https://myveticare.com/admin" || true

{
  echo "MANUAL LIVE FOLLOW-UP REQUIRED"
  echo "Use real controlled pilot identities only"
  echo "Track up to 5 clinics maximum"
  echo "Record repeated workflows, incidents, SLA observations, and stability outcomes"
  echo "Do not use prototype or demo accounts as governed evidence"
} > "$RUN_DIR/manual_follow_up.txt"

find "$RUN_DIR" -type f -exec shasum -a 256 {} \; | sort > "$RUN_DIR/MANIFEST.sha256"

echo "RUN COMPLETE" >> "$RUN_DIR/summary.txt"
echo "EVIDENCE_RUN_DIR=$RUN_DIR" >> "$RUN_DIR/summary.txt"

printf '%s\n' "$RUN_DIR"
