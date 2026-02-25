#!/usr/bin/env bash
set -euo pipefail

PHASE="PETCARE-PH01-CLOSURE"
TS_UTC="$(date -u +%Y%m%dT%H%M%SZ)"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_ROOT="${REPO_ROOT}/evidence_output/${PHASE}"
OUT="${OUT_ROOT}/${TS_UTC}"

PY="${REPO_ROOT}/.venv/bin/python"
if [ ! -x "${PY}" ]; then PY="python3"; fi

REG="${REPO_ROOT}/REGISTRY.json"
REG_PIN="${REPO_ROOT}/REGISTRY.sha256"
POL="${REPO_ROOT}/POLICY.md"
POL_PIN="${REPO_ROOT}/POLICY.sha256"

echo "=============================================="
echo "PetCare PH01 CLOSURE PACK"
echo "pack=${PHASE}"
echo "timestamp_utc=${TS_UTC}"
echo "repo_root=${REPO_ROOT}"
echo "out=${OUT}"
echo "python_bin=${PY}"
echo "=============================================="

mkdir -p "${OUT}"

echo ""
echo "=== PRE-FLIGHT: REQUIRED FILES ==="
REQ_FAIL=0
for f in "${REG}" "${REG_PIN}" "${POL}" "${POL_PIN}"; do
  if [ ! -f "${f}" ]; then
    echo "MISSING_FILE=${f}"
    REQ_FAIL=1
  fi
done
if [ "${REQ_FAIL}" -ne 0 ]; then
  echo "FAIL: missing required files"
  exit 2
fi
echo "OK required files present"

echo ""
echo "=== DRIFT CHECKS ==="
bash "${REPO_ROOT}/scripts/petcare_policy_drift_check.sh" | tee "${OUT}/policy_drift.txt"
bash "${REPO_ROOT}/scripts/petcare_registry_drift_check.sh" | tee "${OUT}/registry_drift.txt"

echo ""
echo "=== CI GATES (IF PRESENT) ==="
if [ -f "${REPO_ROOT}/scripts/petcare_ci_gates.sh" ]; then
  bash "${REPO_ROOT}/scripts/petcare_ci_gates.sh" | tee "${OUT}/ci_gates.txt"
else
  echo "SKIP: scripts/petcare_ci_gates.sh not present" | tee "${OUT}/ci_gates.txt"
fi

echo ""
echo "=== PYTEST (FULL SUITE) ==="
"${PY}" -m pytest -q | tee "${OUT}/pytest.txt"

echo ""
echo "=== SNAPSHOT: KEY FILES ==="
mkdir -p "${OUT}/snapshots"
cp -p "REGISTRY.json" "${OUT}/snapshots/REGISTRY.before.json"
cp -p "REGISTRY.sha256" "${OUT}/snapshots/REGISTRY.before.sha256"
cp -p "POLICY.md" "${OUT}/snapshots/POLICY.md"
cp -p "POLICY.sha256" "${OUT}/snapshots/POLICY.sha256"
echo "OK snapshots copied"

echo ""
echo "=== UPDATE REGISTRY: PH01 -> Closed ==="
"${PY}" - << 'PY'
import json,os

reg_path="REGISTRY.json"
data=json.load(open(reg_path,"r",encoding="utf-8"))

found=False
for p in data.get("phases",[]):
  if p.get("phase")=="PH01":
    p["status"]="Closed"
    found=True

if not found:
  raise SystemExit("FAIL: PH01 not found in REGISTRY.json")

tmp=reg_path+".tmp"
with open(tmp,"w",encoding="utf-8",newline="\n") as f:
  json.dump(data,f,indent=2,ensure_ascii=False)
  f.write("\n")
os.replace(tmp,reg_path)

print("OK PH01 marked Closed in REGISTRY.json")
PY

echo ""
echo "=== RE-PIN REGISTRY.sha256 ==="
(
  cd "${REPO_ROOT}" || exit 1
  shasum -a 256 "REGISTRY.json" > "REGISTRY.sha256"
  cat "REGISTRY.sha256"
) | tee "${OUT}/registry_pin.txt"
echo "OK wrote REGISTRY.sha256"

echo ""
echo "=== SNAPSHOT: REGISTRY AFTER ==="
cp -p "REGISTRY.json" "${OUT}/snapshots/REGISTRY.after.json"
cp -p "REGISTRY.sha256" "${OUT}/snapshots/REGISTRY.after.sha256"
echo "OK snapshot after"

echo ""
echo "=== SHA256 (SNAPSHOT TREE) ==="
(
  cd "${OUT}" || exit 1
  find . -type f -print0 \
  | LC_ALL=C sort -z \
  | xargs -0 shasum -a 256 \
  > "closure_sha256.txt"
)
echo "OK wrote closure_sha256.txt"

echo ""
echo "=== MANIFEST.json ==="
OUT="${OUT}" "${PY}" - << 'PY'
import json,os

out=os.environ["OUT"]
phase=os.path.basename(os.path.dirname(out))
ts=os.path.basename(out)

files=[]
for root,dirs,fs in os.walk(out):
  dirs.sort()
  for fn in sorted(fs):
    p=os.path.join(root,fn)
    rel=os.path.relpath(p,out).replace("\\","/")
    files.append(rel)

files.sort()

manifest={
  "pack": phase,
  "timestamp_utc": ts,
  "file_count": len(files),
  "files": files,
}

with open(os.path.join(out,"MANIFEST.json"),"w",encoding="utf-8",newline="\n") as f:
  json.dump(manifest,f,indent=2,ensure_ascii=False)
  f.write("\n")

print("OK wrote MANIFEST.json")
PY

echo ""
echo "=== ZIP + ZIP.SHA256 ==="
mkdir -p "${OUT_ROOT}"
ZIP="${OUT_ROOT}/${PHASE}_${TS_UTC}.zip"
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
