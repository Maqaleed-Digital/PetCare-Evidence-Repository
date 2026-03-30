#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}" || exit 1

PHASE="PETCARE-PH42C-CLOSURE"
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
echo "PetCare PH42-C CLOSURE PACK"
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
  "requirements.lock"
  "FND/RELEASE_INTEGRITY_POLICY.md"
  "FND/PROD_RUNTIME_ATTESTATION_SPEC.md"
  "FND/DEPLOYMENT_SEPARATION_MODEL.md"
  "EVIDENCE/PH42C_RELEASE_ATTESTATION_REPORT.md"
  "scripts/petcare_release_integrity_check.sh"
  "scripts/petcare_progress_report.sh"
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
fi
if [ -x "${ROOT}/scripts/petcare_registry_drift_check.sh" ]; then
  bash "${ROOT}/scripts/petcare_registry_drift_check.sh"
fi

echo ""
echo "=== REQUIRED CHECKS ASSERT (IF PRESENT) ==="
if [ -x "${ROOT}/scripts/petcare_required_checks_assert.sh" ]; then
  bash "${ROOT}/scripts/petcare_required_checks_assert.sh" | tee "${OUT}/required_checks_assert.txt"
else
  echo "NA" | tee "${OUT}/required_checks_assert.txt"
fi

echo ""
echo "=== CI GATES (IF PRESENT) ==="
if [ -x "${ROOT}/scripts/petcare_ci_gates.sh" ]; then
  bash "${ROOT}/scripts/petcare_ci_gates.sh" | tee "${OUT}/ci_gates.txt"
else
  echo "NA" | tee "${OUT}/ci_gates.txt"
fi

echo ""
echo "=== RELEASE INTEGRITY CHECK ==="
bash "${ROOT}/scripts/petcare_release_integrity_check.sh" | tee "${OUT}/release_integrity_check.txt"

echo ""
echo "=== PROGRESS REPORT (SNAPSHOT) ==="
bash "${ROOT}/scripts/petcare_progress_report.sh" "." | tee "${OUT}/progress_report.txt"

echo ""
echo "=== FILL ATTESTATION REPORT (COPY IN OUT) ==="
POLICY_SHA="$(cat "${ROOT}/POLICY.sha256" | tr -d '\r\n')"
REGISTRY_SHA="$(cat "${ROOT}/REGISTRY.sha256" | tr -d '\r\n')"
LOCK_SHA="$(shasum -a 256 "${ROOT}/requirements.lock" | awk '{print $1}')"
GIT_HEAD="$(git rev-parse HEAD)"
PY_VER="$("${PY}" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"

REPORT_IN="${ROOT}/EVIDENCE/PH42C_RELEASE_ATTESTATION_REPORT.md"
REPORT_OUT="${OUT}/snapshots/EVIDENCE/PH42C_RELEASE_ATTESTATION_REPORT.md"
mkdir -p "$(dirname "${REPORT_OUT}")"

sed \
  -e "s/__FILL__/${TS_UTC}/" \
  -e "0,/__FILL__/s//${GIT_HEAD}/" \
  -e "0,/__FILL__/s//${PY_VER}/" \
  -e "0,/__FILL__/s//${POLICY_SHA}/" \
  -e "0,/__FILL__/s//${REGISTRY_SHA}/" \
  -e "0,/__FILL__/s//${LOCK_SHA}/" \
  "${REPORT_IN}" > "${REPORT_OUT}"

echo "OK wrote filled report"

echo ""
echo "=== SNAPSHOTS ==="
snap=(
  "POLICY.md"
  "POLICY.sha256"
  "REGISTRY.json"
  "REGISTRY.sha256"
  "requirements.lock"
  "scripts/petcare_progress_report.sh"
  "scripts/petcare_release_integrity_check.sh"
  "scripts/petcare_ph42c_closure_pack.sh"
  "FND/RELEASE_INTEGRITY_POLICY.md"
  "FND/PROD_RUNTIME_ATTESTATION_SPEC.md"
  "FND/DEPLOYMENT_SEPARATION_MODEL.md"
)
for f in "${snap[@]}"; do
  mkdir -p "${OUT}/snapshots/$(dirname "${f}")"
  cp -p "${ROOT}/${f}" "${OUT}/snapshots/${f}"
done
echo "OK snapshots copied"

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
    "PH42-C: release integrity policy + runtime attestation spec + deployment separation model + integrity check + closure pack"
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
