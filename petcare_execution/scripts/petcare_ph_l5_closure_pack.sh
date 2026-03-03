#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# PH-L5 — Controlled Pilot Activation (Control Plane)
# Canonical executor: Claude Code (same block OK in Terminal).
# No guessing. Atomic writes. Evidence ZIP + SHA. Commit + push.
# ============================================================

REPO_ROOT="/Users/waheebmahmoud/dev/petcare-evidence-repository/petcare_execution"
cd "${REPO_ROOT}" || { echo "FATAL: missing REPO_ROOT=${REPO_ROOT}"; exit 2; }

PHASE="PETCARE-PH-L5-CLOSURE"
TS_UTC="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_ROOT="${REPO_ROOT}/evidence_output/${PHASE}"
OUT="${OUT_ROOT}/${TS_UTC}"
mkdir -p "${OUT}/logs" "${OUT}/snapshots"

echo "=============================================="
echo "PetCare PH-L5 CLOSURE PACK"
echo "timestamp_utc=${TS_UTC}"
echo "repo_root=${REPO_ROOT}"
echo "out=${OUT}"
echo "=============================================="

echo ""
echo "=== STEP 0: BASELINE CHECK (NO GUESSING) ==="
need=(
  "scripts/petcare_ci_gates.sh"
  "scripts/petcare_release_integrity_check.sh"
)
missing=0
for f in "${need[@]}"; do
  if [ ! -f "${f}" ]; then echo "MISSING_REQUIRED_FILE=${f}"; missing=1; fi
done
if [ "${missing}" -ne 0 ]; then
  echo "FATAL: missing required files. Stop (no guessing)."
  exit 3
fi

echo ""
echo "=== STEP 1: WRITE PILOT CONTROL ARTIFACT (tmp→mv) ==="
mkdir -p "FND" "docs" "scripts"

TMP="$(mktemp)"
cat > "${TMP}" <<'JSON'
{
  "schema": "petcare.pilot_control.v1",
  "schema_version": 1,
  "pilot_enabled": false,
  "pilot_name": "Pilot-1",
  "pilot_region": "KSA",
  "pilot_scope": "Governed pilot activation control plane (repo-level). Mirror into runtime systems before external launch.",
  "activation_requires_ceo_declaration": true,
  "ceo_declaration_path": "docs/CEO_GO_LIVE_DECLARATION.md",
  "notes": "PH-L5 baseline: pilot disabled by default. Enable only after CEO go/no-go sign-off is completed."
}
JSON
chmod 0644 "${TMP}"
mv -f "${TMP}" "FND/PILOT_CONTROL.json"

echo ""
echo "=== STEP 2: WRITE CEO GO/NO-GO DECLARATION TEMPLATE (tmp→mv) ==="
TMP="$(mktemp)"
cat > "${TMP}" <<'MD'
# CEO Go/No-Go Declaration — PetCare (Pilot / Launch)

**Document ID:** PETCARE-CEO-DECL-v1
**Prepared By:** Platform Ops
**Approval Authority:** CEO
**Date (UTC):** ______________________

## 1) Decision
- [ ] **GO** — Authorize pilot/launch under the scope below
- [ ] **NO-GO** — Do not launch; remediation required

## 2) Scope Authorized
- Pilot/Launch Name: ______________________
- Region(s): ______________________
- Modules Included: ______________________
- Modules Excluded: ______________________
- Start Time (UTC): ______________________
- End Time (UTC) (if pilot): ______________________

## 3) Preconditions Verified (attach evidence paths)
- CI Gates: PASS (evidence/log path: ______________________)
- Release Integrity: PASS (evidence/log path: ______________________)
- Verification Index Integrity: PASS (evidence/log path: ______________________)
- Backup/Restore (PH-L2): VERIFIED (evidence/log path: ______________________)
- Ops Runbook + IR Playbook (PH-L3): VERIFIED (evidence/log path: ______________________)
- PDPL + retention + security baseline (PH-L4): VERIFIED (evidence/log path: ______________________)

## 4) Risk Acceptance
- Known risks accepted by CEO:
  1) ______________________
  2) ______________________
  3) ______________________

## 5) Rollback Plan
- Rollback trigger conditions: ______________________
- Rollback operator: ______________________
- Rollback method:
  - [ ] Revert to last known-good tag/commit
  - [ ] Restore from backup bundle (PH-L2)
  - [ ] Other: ______________________

## 6) Communications Plan
- Internal comms owner: ______________________
- External comms owner (if applicable): ______________________
- Status update cadence: ______________________

## 7) CEO Signature
Name: Waheeb Ghassan Mahmoud
Signature: ______________________
Date (UTC): ______________________
MD
chmod 0644 "${TMP}"
mv -f "${TMP}" "docs/CEO_GO_LIVE_DECLARATION.md"

echo ""
echo "=== STEP 3: WRITE PILOT ACCEPTANCE + MONITORING DOCS (tmp→mv) ==="
TMP="$(mktemp)"
cat > "${TMP}" <<'MD'
# Pilot Acceptance Criteria — PetCare

**Document ID:** PETCARE-PILOT-ACCEPT-v1
**Owner:** Platform Ops
**Last Updated (UTC):** 2026-03-03

## Acceptance Criteria (minimum)

### A) Governance
- CI gates PASS on main
- Release integrity PASS
- Verification index quorum satisfied

### B) Operational
- On-call escalation active
- Incident playbook reviewed
- Rollback drill completed (PH-L3)

### C) Data & Privacy
- PDPL posture documented (PH-L4)
- Retention policy documented (PH-L4)

### D) Pilot Success Metrics (fill before GO)
- Daily active users target: __________
- Appointment conversion target: __________
- Error budget (max Sev-2/week): __________
- Response time target: __________

MD
chmod 0644 "${TMP}"
mv -f "${TMP}" "docs/PILOT_ACCEPTANCE_CRITERIA.md"

TMP="$(mktemp)"
cat > "${TMP}" <<'MD'
# Pilot Monitoring Checklist — PetCare

**Document ID:** PETCARE-PILOT-MONITOR-v1
**Owner:** Platform Ops
**Last Updated (UTC):** 2026-03-03

## Daily Checks
- CI gates status (repo health)
- Verification index quorum + sidecar status
- Evidence size growth within budget
- Open incidents / Sev counts

## During Pilot Activation Window
- Confirm CEO Declaration completed
- Confirm rollback operator online
- Confirm comms channel active
- Run integrity checks:
  - release integrity
  - CI gates

## Post-Activation (T+60 mins)
- Confirm no Sev-1
- Confirm error budget within target
- Prepare pilot status update

MD
chmod 0644 "${TMP}"
mv -f "${TMP}" "docs/PILOT_MONITORING_CHECKLIST.md"

echo ""
echo "=== STEP 4: WRITE PILOT CONTROL GUARD (tmp→mv) ==="
TMP="$(mktemp)"
cat > "${TMP}" <<'BASH'
#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CTL="${REPO_ROOT}/FND/PILOT_CONTROL.json"

if [ ! -f "${CTL}" ]; then
  echo "FATAL: missing FND/PILOT_CONTROL.json"
  exit 50
fi

python3 - <<PY
import json,sys,os
p="${CTL}"
o=json.load(open(p,"r",encoding="utf-8"))
if o.get("schema")!="petcare.pilot_control.v1": raise SystemExit("FATAL: bad schema")
if o.get("schema_version")!=1: raise SystemExit("FATAL: bad schema_version")
pe=o.get("pilot_enabled")
if pe not in (True,False): raise SystemExit("FATAL: pilot_enabled must be boolean")
req=o.get("activation_requires_ceo_declaration")
if req not in (True,False): raise SystemExit("FATAL: activation_requires_ceo_declaration must be boolean")
decl=o.get("ceo_declaration_path")
if not isinstance(decl,str) or not decl: raise SystemExit("FATAL: ceo_declaration_path missing")
print("pilot_enabled="+str(pe).lower())
print("activation_requires_ceo_declaration="+str(req).lower())
print("ceo_declaration_path="+decl)
PY

PILOT_ENABLED="$(python3 - <<PY
import json
o=json.load(open("${CTL}","r",encoding="utf-8"))
print("true" if o["pilot_enabled"] else "false")
PY
)"

REQ_DECL="$(python3 - <<PY
import json
o=json.load(open("${CTL}","r",encoding="utf-8"))
print("true" if o["activation_requires_ceo_declaration"] else "false")
PY
)"

DECL_PATH="$(python3 - <<PY
import json
o=json.load(open("${CTL}","r",encoding="utf-8"))
print(o["ceo_declaration_path"])
PY
)"

# If pilot is enabled, require CEO declaration file to exist AND be filled (not template-only).
if [ "${PILOT_ENABLED}" = "true" ] && [ "${REQ_DECL}" = "true" ]; then
  if [ ! -f "${REPO_ROOT}/${DECL_PATH}" ]; then
    echo "FATAL: pilot_enabled=true but missing CEO declaration at ${DECL_PATH}"
    exit 51
  fi
  # Require at least one checkbox selection and signature date filled.
  if ! grep -qE '^\- \[x\] \*\*GO\*\*|^\- \[x\] \*\*NO-GO\*\*' "${REPO_ROOT}/${DECL_PATH}"; then
    echo "FATAL: CEO declaration not completed (GO/NO-GO not selected)"
    exit 52
  fi
  if grep -qE 'Date \(UTC\):[[:space:]]*_+' "${REPO_ROOT}/${DECL_PATH}"; then
    echo "FATAL: CEO declaration date appears unfilled"
    exit 53
  fi
  if grep -qE 'Signature:[[:space:]]*_+' "${REPO_ROOT}/${DECL_PATH}"; then
    echo "FATAL: CEO declaration signature appears unfilled"
    exit 54
  fi
  echo "OK: pilot enabled and CEO declaration appears completed"
  exit 0
fi

echo "OK: pilot control guard PASS (pilot not enabled, or CEO declaration not required)"
BASH
chmod +x "${TMP}"
mv -f "${TMP}" "scripts/petcare_pilot_control_guard.sh"

echo ""
echo "=== STEP 5: RUN PILOT CONTROL GUARDS ==="
bash "scripts/petcare_pilot_control_guard.sh" | tee "${OUT}/logs/pilot_control_guard.log"

echo ""
echo "=== STEP 6: RELEASE INTEGRITY + CI GATES (MUST PASS) ==="
bash "scripts/petcare_release_integrity_check.sh" | tee "${OUT}/logs/release_integrity.log"
bash "scripts/petcare_ci_gates.sh" | tee "${OUT}/logs/ci_gates.log"

echo ""
echo "=== STEP 7: SNAPSHOT CONTROL FILES ==="
snap=(
  "FND/PILOT_CONTROL.json"
  "docs/CEO_GO_LIVE_DECLARATION.md"
  "docs/PILOT_ACCEPTANCE_CRITERIA.md"
  "docs/PILOT_MONITORING_CHECKLIST.md"
  "scripts/petcare_pilot_control_guard.sh"
)
for f in "${snap[@]}"; do
  mkdir -p "${OUT}/snapshots/$(dirname "${f}")"
  cp -p "${REPO_ROOT}/${f}" "${OUT}/snapshots/${f}"
done

echo ""
echo "=== STEP 8: MANIFEST + SHA ==="
python3 - <<PY
import json
from pathlib import Path
out=Path("${OUT}")
files=[str(p.relative_to(out)) for p in sorted(out.rglob("*")) if p.is_file()]
m={"phase":"${PHASE}","timestamp_utc":"${TS_UTC}","file_count":len(files),"files":files}
(out/"MANIFEST.json").write_text(json.dumps(m, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
print("OK wrote MANIFEST.json")
PY

(
  cd "${OUT}" || exit 1
  find . -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256 > "closure_sha256.txt"
)

echo ""
echo "=== STEP 9: ZIP + ZIP.SHA256 ==="
mkdir -p "${OUT_ROOT}"
ZIP="${OUT_ROOT}/${PHASE}_${TS_UTC}.zip"
rm -f "${ZIP}" "${ZIP}.sha256"
(
  cd "${OUT_ROOT}" || exit 1
  zip -r "${PHASE}_${TS_UTC}.zip" "${TS_UTC}" >/dev/null
  shasum -a 256 "${PHASE}_${TS_UTC}.zip" > "${PHASE}_${TS_UTC}.zip.sha256"
)

echo ""
echo "=== STEP 10: COMMIT / PUSH ==="
git status -sb | tee "${OUT}/logs/git_status.log"

git add \
  "FND/PILOT_CONTROL.json" \
  "docs/CEO_GO_LIVE_DECLARATION.md" \
  "docs/PILOT_ACCEPTANCE_CRITERIA.md" \
  "docs/PILOT_MONITORING_CHECKLIST.md" \
  "scripts/petcare_pilot_control_guard.sh"

git commit -m "PH-L5: controlled pilot activation control plane"
git push origin main

echo ""
echo "DONE"
echo "ZIP=${ZIP}"
echo "ZIP_SHA=${ZIP}.sha256"
echo "COMMIT=$(git rev-parse HEAD)"
