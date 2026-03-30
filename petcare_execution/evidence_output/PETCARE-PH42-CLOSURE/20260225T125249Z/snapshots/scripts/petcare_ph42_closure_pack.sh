#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}" || exit 1

PHASE="PETCARE-PH42-CLOSURE"
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

NOTION_CSV="${ROOT}/notion_exports/PETCARE_PHASE_REGISTRY_EXPORT.csv"

echo "=============================================="
echo "PetCare PH42 CLOSURE PACK"
echo "pack=${PHASE}"
echo "timestamp_utc=${TS_UTC}"
echo "repo_root=${ROOT}"
echo "out=${OUT}"
echo "python_bin=${PY}"
echo "notion_csv=${NOTION_CSV}"
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
  "scripts/petcare_registry_drift_check.sh"
  "scripts/petcare_notion_phase_registry_reconcile.py"
)
for f in "${req[@]}"; do
  if [ ! -f "${ROOT}/${f}" ]; then
    echo "MISSING_FILE=${f}"
    exit 1
  fi
done

if [ ! -f "${NOTION_CSV}" ]; then
  echo "MISSING_NOTION_EXPORT=${NOTION_CSV}"
  echo "ACTION: Export your Notion Phase Registry to CSV and save it exactly at notion_exports/PETCARE_PHASE_REGISTRY_EXPORT.csv"
  exit 1
fi

echo "OK required files present"

echo ""
echo "=== DRIFT CHECKS ==="
if [ -x "${ROOT}/scripts/petcare_policy_drift_check.sh" ]; then
  bash "${ROOT}/scripts/petcare_policy_drift_check.sh"
else
  echo "WARN missing scripts/petcare_policy_drift_check.sh (skipping)"
fi

bash "${ROOT}/scripts/petcare_registry_drift_check.sh"

echo ""
echo "=== CI GATES (IF PRESENT) ==="
if [ -x "${ROOT}/scripts/petcare_ci_gates.sh" ]; then
  bash "${ROOT}/scripts/petcare_ci_gates.sh"
else
  echo "WARN missing scripts/petcare_ci_gates.sh (skipping)"
fi

echo ""
echo "=== PROGRESS REPORT (SNAPSHOT) ==="
bash "${ROOT}/scripts/petcare_progress_report.sh" "." | tee "${OUT}/progress_report.txt"

echo ""
echo "=== NOTION RECONCILIATION ==="
set +e
"${PY}" "${ROOT}/scripts/petcare_notion_phase_registry_reconcile.py" \
  "${ROOT}/REGISTRY.json" \
  "${NOTION_CSV}" \
  "${OUT}/notion_reconciliation_report.txt"
RC=$?
set -e
if [ "${RC}" -ne 0 ]; then
  echo "FAIL: Notion reconciliation failed (see ${OUT}/notion_reconciliation_report.txt)"
  exit 1
fi
echo "OK Notion reconciliation PASS"

echo ""
echo "=== SNAPSHOTS ==="
snap=(
  "REGISTRY.json"
  "REGISTRY.sha256"
  "POLICY.md"
  "POLICY.sha256"
  "scripts/petcare_progress_report.sh"
  "scripts/petcare_registry_drift_check.sh"
  "scripts/petcare_notion_phase_registry_reconcile.py"
  "scripts/petcare_ph42_closure_pack.sh"
  "notion_exports/PETCARE_PHASE_REGISTRY_EXPORT.csv"
)

for f in "${snap[@]}"; do
  if [ ! -f "${ROOT}/${f}" ]; then
    echo "MISSING_SNAPSHOT_FILE=${f}"
    exit 1
  fi
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
    "PH42: Deterministic reconciliation between REGISTRY.json and Notion Phase Registry CSV export",
    "Closure requires: policy drift PASS (if present), registry drift PASS, ci gates PASS (if present), reconcile PASS"
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
