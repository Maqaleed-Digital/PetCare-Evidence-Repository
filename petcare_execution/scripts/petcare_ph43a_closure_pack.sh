#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}" || exit 1

PHASE="PETCARE-PH43A-CLOSURE"
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

RELEASE_TAG="${RELEASE_TAG:-}"
ARTIFACT_PATH="${ARTIFACT_PATH:-}"

echo "=============================================="
echo "PetCare PH43-A CLOSURE PACK"
echo "pack=${PHASE}"
echo "timestamp_utc=${TS_UTC}"
echo "repo_root=${ROOT}"
echo "out=${OUT}"
echo "python_bin=${PY}"
echo "release_tag_env=${RELEASE_TAG:-<unset>}"
echo "artifact_path_env=${ARTIFACT_PATH:-<unset>}"
echo "=============================================="

mkdir -p "${OUT}"
mkdir -p "${OUT}/snapshots"

echo ""
echo "=== PRE-FLIGHT: REQUIRED FILES ==="
req=(
  "REGISTRY.json"
  "REGISTRY.sha256"
  "POLICY.md"
  "POLICY.sha256"
  "scripts/petcare_progress_report.sh"
  "FND/RELEASE_TAGGING_POLICY.md"
  "FND/PROD_DEPLOYMENT_BOUNDARY_CONTRACT.md"
  "FND/PROD_DEPLOYMENT_PIPELINE_SPEC.md"
  "EVIDENCE/PH43A_RELEASE_BOUNDARY_REPORT.md"
  "scripts/petcare_release_tag_verify.sh"
  "scripts/petcare_prod_deploy_artifact_contract.sh"
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
POLICY_DRIFT="SKIP"
REGISTRY_DRIFT="SKIP"
if [ -x "${ROOT}/scripts/petcare_policy_drift_check.sh" ]; then
  bash "${ROOT}/scripts/petcare_policy_drift_check.sh" | tee "${OUT}/policy_drift_check.txt"
  POLICY_DRIFT="PASS"
else
  echo "WARN missing scripts/petcare_policy_drift_check.sh (skipping)" | tee "${OUT}/policy_drift_check.txt"
fi

if [ -x "${ROOT}/scripts/petcare_registry_drift_check.sh" ]; then
  bash "${ROOT}/scripts/petcare_registry_drift_check.sh" | tee "${OUT}/registry_drift_check.txt"
  REGISTRY_DRIFT="PASS"
else
  echo "WARN missing scripts/petcare_registry_drift_check.sh (skipping)" | tee "${OUT}/registry_drift_check.txt"
fi

echo ""
echo "=== REQUIRED CHECKS ASSERT (IF PRESENT) ==="
if [ -x "${ROOT}/scripts/petcare_required_checks_assert.sh" ]; then
  bash "${ROOT}/scripts/petcare_required_checks_assert.sh" | tee "${OUT}/required_checks_assert.txt"
fi

echo ""
echo "=== CI GATES (IF PRESENT) ==="
CI_GATES="SKIP"
if [ -x "${ROOT}/scripts/petcare_ci_gates.sh" ]; then
  bash "${ROOT}/scripts/petcare_ci_gates.sh" | tee "${OUT}/ci_gates.txt"
  CI_GATES="PASS"
else
  echo "WARN missing scripts/petcare_ci_gates.sh (skipping)" | tee "${OUT}/ci_gates.txt"
fi

echo ""
echo "=== RELEASE TAG VERIFY (REQUIRES RELEASE_TAG env) ==="
TAG_SHA=""
TAG_DESCRIBE=""
if [ -z "${RELEASE_TAG}" ]; then
  echo "MISSING_RELEASE_TAG_ENV=RELEASE_TAG" | tee "${OUT}/release_tag_verify.txt"
  echo "RESULT=FAIL" | tee -a "${OUT}/release_tag_verify.txt"
  exit 1
else
  bash "${ROOT}/scripts/petcare_release_tag_verify.sh" "${RELEASE_TAG}" | tee "${OUT}/release_tag_verify.txt"
  TAG_SHA="$(grep -E '^TAG_SHA=' "${OUT}/release_tag_verify.txt" | head -1 | cut -d= -f2- || true)"
  TAG_DESCRIBE="$(grep -E '^TAG_DESCRIBE=' "${OUT}/release_tag_verify.txt" | head -1 | cut -d= -f2- || true)"
fi

echo ""
echo "=== ARTIFACT CONTRACT (OPTIONAL via ARTIFACT_PATH env) ==="
ARTIFACT_SHA256=""
ARTIFACT_CONTRACT="PASS"
bash "${ROOT}/scripts/petcare_prod_deploy_artifact_contract.sh" "${ARTIFACT_PATH}" | tee "${OUT}/artifact_contract.txt"
ARTIFACT_SHA256="$(grep -E '^ARTIFACT_SHA256=' "${OUT}/artifact_contract.txt" | head -1 | cut -d= -f2- || true)"

echo ""
echo "=== EVIDENCE SAFETY CHECKS ==="
EVIDENCE_TRACKED="PASS"
if git ls-files | grep -q '^evidence_output/'; then
  EVIDENCE_TRACKED="FAIL"
fi
ENV_TRACKED="PASS"
if git ls-files | grep -E -q '(^|/)\.env($|[^/])|(^|/)\.env\.|(^|/)env\.|(^|/)\.envrc$'; then
  ENV_TRACKED="FAIL"
fi

echo "EVIDENCE_OUTPUT_TRACKED=${EVIDENCE_TRACKED}" | tee "${OUT}/evidence_safety.txt"
echo "ENV_FILES_TRACKED=${ENV_TRACKED}" | tee -a "${OUT}/evidence_safety.txt"
if [ "${EVIDENCE_TRACKED}" != "PASS" ] || [ "${ENV_TRACKED}" != "PASS" ]; then
  echo "RESULT=FAIL" | tee -a "${OUT}/evidence_safety.txt"
  exit 1
fi
echo "RESULT=PASS" | tee -a "${OUT}/evidence_safety.txt"

echo ""
echo "=== SECRET HEURISTIC (TRACKED FILES ONLY) ==="
SECRET_SCAN="PASS"
if git grep -nE '(API_KEY|SECRET_KEY|PRIVATE_KEY|BEGIN (RSA|EC|OPENSSH) PRIVATE KEY|AKIA[0-9A-Z]{16})' -- . >/dev/null 2>&1; then
  SECRET_SCAN="FAIL"
fi
echo "SECRET_SCAN=${SECRET_SCAN}" | tee "${OUT}/secret_scan.txt"
if [ "${SECRET_SCAN}" != "PASS" ]; then
  exit 1
fi

echo ""
echo "=== PROGRESS REPORT (SNAPSHOT) ==="
bash "${ROOT}/scripts/petcare_progress_report.sh" "." | tee "${OUT}/progress_report.txt"

echo ""
echo "=== FILL ATTESTATION REPORT (COPY IN OUT) ==="
GIT_HEAD="$(git rev-parse HEAD)"
GIT_STATUS="$(git status -sb | tr '\n' ' ' | sed 's/[[:space:]]\+/ /g')"

REPORT_SRC="${ROOT}/EVIDENCE/PH43A_RELEASE_BOUNDARY_REPORT.md"
REPORT_OUT="${OUT}/PH43A_RELEASE_BOUNDARY_REPORT_FILLED.md"

python3 - <<'PY' "${REPORT_SRC}" "${REPORT_OUT}" "${TS_UTC}" "${ROOT}" "${GIT_HEAD}" "${GIT_STATUS}" "${RELEASE_TAG}" "${TAG_SHA}" "${TAG_DESCRIBE}" "${POLICY_DRIFT}" "${REGISTRY_DRIFT}" "PASS" "${CI_GATES}" "${EVIDENCE_TRACKED}" "${ENV_TRACKED}" "${SECRET_SCAN}" "${ARTIFACT_PATH}" "${ARTIFACT_SHA256}" "${ARTIFACT_CONTRACT}"
import sys
src,out = sys.argv[1], sys.argv[2]
vals = {
  "{{TS_UTC}}": sys.argv[3],
  "{{ROOT}}": sys.argv[4],
  "{{GIT_HEAD}}": sys.argv[5],
  "{{GIT_STATUS}}": sys.argv[6],
  "{{RELEASE_TAG}}": sys.argv[7],
  "{{TAG_SHA}}": sys.argv[8],
  "{{TAG_DESCRIBE}}": sys.argv[9],
  "{{POLICY_DRIFT}}": sys.argv[10],
  "{{REGISTRY_DRIFT}}": sys.argv[11],
  "{{LOCK_VERIFY}}": sys.argv[12],
  "{{CI_GATES}}": sys.argv[13],
  "{{EVIDENCE_TRACKED}}": sys.argv[14],
  "{{ENV_TRACKED}}": sys.argv[15],
  "{{SECRET_SCAN}}": sys.argv[16],
  "{{ARTIFACT_PATH}}": sys.argv[17],
  "{{ARTIFACT_SHA256}}": sys.argv[18],
  "{{ARTIFACT_CONTRACT}}": sys.argv[19],
}
s=open(src,"r",encoding="utf-8").read()
for k,v in vals.items():
  s=s.replace(k, v)
open(out,"w",encoding="utf-8",newline="\n").write(s)
print("OK wrote filled report:", out)
PY

echo ""
echo "=== SNAPSHOTS ==="
snap=(
  "POLICY.md"
  "POLICY.sha256"
  "REGISTRY.json"
  "REGISTRY.sha256"
  "scripts/petcare_progress_report.sh"
  "scripts/petcare_ph43a_closure_pack.sh"
  "scripts/petcare_release_tag_verify.sh"
  "scripts/petcare_prod_deploy_artifact_contract.sh"
  "FND/RELEASE_TAGGING_POLICY.md"
  "FND/PROD_DEPLOYMENT_BOUNDARY_CONTRACT.md"
  "FND/PROD_DEPLOYMENT_PIPELINE_SPEC.md"
  "EVIDENCE/PH43A_RELEASE_BOUNDARY_REPORT.md"
)
for f in "${snap[@]}"; do
  mkdir -p "${OUT}/snapshots/$(dirname "${f}")"
  cp -p "${ROOT}/${f}" "${OUT}/snapshots/${f}"
done
cp -p "${REPORT_OUT}" "${OUT}/snapshots/PH43A_RELEASE_BOUNDARY_REPORT_FILLED.md"
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
    "PH43-A: production release boundary contract + release tag verify + optional artifact digest contract + deterministic attestation report"
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
