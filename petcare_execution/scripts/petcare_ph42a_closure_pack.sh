#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}" || exit 1

PHASE="PETCARE-PH42A-CLOSURE"
TS_UTC="$(date -u +"%Y%m%dT%H%M%SZ")"
OUT_ROOT="${ROOT}/evidence_output/${PHASE}"
OUT="${OUT_ROOT}/${TS_UTC}"
ZIP="${OUT_ROOT}/${PHASE}_${TS_UTC}.zip"

PY_BIN="${ROOT}/.venv/bin/python"
if [ -x "${PY_BIN}" ]; then
  PY="${PY_BIN}"
else
  PY="python3"
fi

echo "=============================================="
echo "PetCare PH42-A CLOSURE PACK"
echo "pack=${PHASE}"
echo "timestamp_utc=${TS_UTC}"
echo "repo_root=${ROOT}"
echo "out=${OUT}"
echo "python_bin=${PY}"
echo "=============================================="

mkdir -p "${OUT}"
mkdir -p "${OUT}/snapshots"

echo ""
echo "=== PRE-FLIGHT: REQUIRED FILES ==="
req=(
  "POLICY.md"
  "POLICY.sha256"
  "REGISTRY.json"
  "REGISTRY.sha256"
  "scripts/petcare_progress_report.sh"
  "scripts/petcare_env_guard_check.sh"
  "scripts/petcare_ph42a_closure_pack.sh"
  "FND/PROD_ENVIRONMENT_POLICY.md"
  "FND/ENVIRONMENT_ISOLATION_MATRIX.md"
  "FND/PROD_SECRET_ROTATION_SOP.md"
  "FND/AI_ENVIRONMENT_LOG_ISOLATION.md"
  "TESTS/ENVIRONMENT_NEGATIVE_CASES.md"
  "EVIDENCE/PH42A_ENVIRONMENT_VALIDATION_REPORT.md"
)
for f in "${req[@]}"; do
  if [ ! -f "${ROOT}/${f}" ]; then
    echo "MISSING_FILE=${f}"
    exit 1
  fi
done
echo "OK required files present"

echo ""
echo "=== DRIFT CHECKS (IF PRESENT) ==="
if [ -x "${ROOT}/scripts/petcare_policy_drift_check.sh" ]; then
  bash "${ROOT}/scripts/petcare_policy_drift_check.sh"
else
  echo "WARN missing scripts/petcare_policy_drift_check.sh (skipping)"
fi

if [ -x "${ROOT}/scripts/petcare_registry_drift_check.sh" ]; then
  bash "${ROOT}/scripts/petcare_registry_drift_check.sh"
else
  echo "WARN missing scripts/petcare_registry_drift_check.sh (skipping)"
fi

echo ""
echo "=== REQUIRED CHECKS ASSERT (IF PRESENT) ==="
if [ -x "${ROOT}/scripts/petcare_required_checks_assert.sh" ]; then
  bash "${ROOT}/scripts/petcare_required_checks_assert.sh"
else
  echo "WARN missing scripts/petcare_required_checks_assert.sh (skipping)"
fi

echo ""
echo "=== CI GATES (IF PRESENT) ==="
if [ -x "${ROOT}/scripts/petcare_ci_gates.sh" ]; then
  bash "${ROOT}/scripts/petcare_ci_gates.sh"
else
  echo "WARN missing scripts/petcare_ci_gates.sh (skipping)"
fi

echo ""
echo "=== PH42-A ENV GUARD CHECK ==="
bash "${ROOT}/scripts/petcare_env_guard_check.sh" | tee "${OUT}/env_guard_check.txt"

echo ""
echo "=== GIT METADATA ==="
GIT_HEAD="$(git rev-parse --short HEAD)"
GIT_STATUS="$(git status -sb | tr '\n' ' ' | sed 's/[[:space:]]\+/ /g')"
echo "git_head=${GIT_HEAD}" | tee "${OUT}/git_head.txt"
echo "git_status=${GIT_STATUS}" | tee "${OUT}/git_status.txt"

echo ""
echo "=== PROGRESS REPORT (SNAPSHOT) ==="
bash "${ROOT}/scripts/petcare_progress_report.sh" "." | tee "${OUT}/progress_report.txt"

echo ""
echo "=== SNAPSHOTS ==="
snap=(
  "POLICY.md"
  "POLICY.sha256"
  "REGISTRY.json"
  "REGISTRY.sha256"
  "scripts/petcare_progress_report.sh"
  "scripts/petcare_env_guard_check.sh"
  "scripts/petcare_ph42a_closure_pack.sh"
  "FND/PROD_ENVIRONMENT_POLICY.md"
  "FND/ENVIRONMENT_ISOLATION_MATRIX.md"
  "FND/PROD_SECRET_ROTATION_SOP.md"
  "FND/AI_ENVIRONMENT_LOG_ISOLATION.md"
  "TESTS/ENVIRONMENT_NEGATIVE_CASES.md"
  "EVIDENCE/PH42A_ENVIRONMENT_VALIDATION_REPORT.md"
)
for f in "${snap[@]}"; do
  mkdir -p "${OUT}/snapshots/$(dirname "${f}")"
  cp -p "${ROOT}/${f}" "${OUT}/snapshots/${f}"
done
echo "OK snapshots copied"

echo ""
echo "=== PH42-A VALIDATION REPORT (FILLED COPY IN OUT) ==="
REPORT_OUT="${OUT}/PH42A_ENVIRONMENT_VALIDATION_REPORT_FILLED.md"
RUN_ID="$(basename "${OUT}")"
cp -p "${ROOT}/EVIDENCE/PH42A_ENVIRONMENT_VALIDATION_REPORT.md" "${REPORT_OUT}"

"${PY}" - << 'PY' "${REPORT_OUT}" "${RUN_ID}" "${TS_UTC}" "${ROOT}" "${GIT_HEAD}" "${GIT_STATUS}"
import sys
p=sys.argv[1]
run_id=sys.argv[2]
ts=sys.argv[3]
root=sys.argv[4].replace("\\","/")
head=sys.argv[5]
status=sys.argv[6]
with open(p,"r",encoding="utf-8") as f:
  s=f.read()
s=s.replace("run_id:", f"run_id: {run_id}")
s=s.replace("timestamp_utc:", f"timestamp_utc: {ts}")
s=s.replace("repo_root:", f"repo_root: {root}")
s=s.replace("git_head:", f"git_head: {head}")
s=s.replace("git_status:", f"git_status: {status}")
with open(p,"w",encoding="utf-8",newline="\n") as f:
  f.write(s)
print("OK wrote filled report")
PY

echo ""
echo "=== SHA256 (SNAPSHOT TREE) ==="
(
  cd "${OUT}/snapshots" || exit 1
  find . -type f -print0 \
  | LC_ALL=C sort -z \
  | xargs -0 shasum -a 256 \
  > "${OUT}/closure_sha256.txt"
)
echo "OK wrote closure_sha256.txt"

echo ""
echo "=== MANIFEST.json ==="
"${PY}" - << 'PY' "${OUT}" "${PHASE}" "${TS_UTC}"
import json,os,sys,hashlib
out=sys.argv[1]
phase=sys.argv[2]
ts=sys.argv[3]

def sha256_file(p):
  h=hashlib.sha256()
  with open(p,"rb") as f:
    for b in iter(lambda: f.read(1024*1024), b""):
      h.update(b)
  return h.hexdigest()

snap_root=os.path.join(out,"snapshots")
records=[]
for root,dirs,files in os.walk(snap_root):
  for fn in files:
    ap=os.path.join(root,fn)
    rel=os.path.relpath(ap,out).replace("\\","/")
    records.append((rel,sha256_file(ap)))
records.sort(key=lambda x:x[0])

manifest={
  "pack": phase,
  "timestamp_utc": ts,
  "out_dir": out.replace("\\","/"),
  "snapshot_count": len(records),
  "snapshots": [{"path":p,"sha256":h} for p,h in records],
  "notes": [
    "PH42-A: environment isolation policy + matrix + secret rotation SOP + AI log isolation + negative cases + guard check"
  ]
}

with open(os.path.join(out,"MANIFEST.json"),"w",encoding="utf-8",newline="\n") as f:
  json.dump(manifest,f,indent=2,ensure_ascii=False)
  f.write("\n")

print("OK wrote MANIFEST.json")
PY

echo ""
echo "=== ZIP + ZIP.SHA256 ==="
mkdir -p "${OUT_ROOT}"
rm -f "${ZIP}" "${ZIP}.sha256"
(
  cd "${OUT_ROOT}" || exit 1
  zip -r "${PHASE}_${TS_UTC}.zip" "${TS_UTC}" >/dev/null
  shasum -a 256 "${PHASE}_${TS_UTC}.zip" > "${PHASE}_${TS_UTC}.zip.sha256"
)
echo "OK zip created: ${ZIP}"
echo "OK zip sha: ${ZIP}.sha256"

echo ""
echo "=== SUMMARY ==="
echo "OUT=${OUT}"
echo "ZIP=${ZIP}"
echo "ZIP_SHA=${ZIP}.sha256"
echo "DONE"
