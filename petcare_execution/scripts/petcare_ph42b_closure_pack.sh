#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}" || exit 1

PHASE="PETCARE-PH42B-CLOSURE"
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
echo "PetCare PH42-B CLOSURE PACK"
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
  "FND/PROD_AUDIT_APPEND_ONLY_SPEC.md"
  "FND/AUDIT_HASH_CHAIN_MODEL.md"
  "FND/CODE_SCAFFOLD/audit_prod_append_only.py"
  "FND/CODE_SCAFFOLD/audit_hash_chain_verify.py"
  "TESTS/PROD_AUDIT_TAMPER_NEGATIVE_TESTS.md"
  "TESTS/test_audit_hash_chain_verify.py"
  "EVIDENCE/PH42B_AUDIT_LEDGER_VALIDATION_REPORT.md"
  "scripts/petcare_ph42b_closure_pack.sh"
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
echo "=== CI GATES (IF PRESENT) ==="
if [ -x "${ROOT}/scripts/petcare_ci_gates.sh" ]; then
  bash "${ROOT}/scripts/petcare_ci_gates.sh"
fi

echo ""
echo "=== PH42-B UNIT TESTS ==="
echo "PYTEST_SELECTOR=-k audit_hash_chain_verify"
"${PY}" -m pytest -q -k "audit_hash_chain_verify" | tee "${OUT}/ph42b_pytest.txt"

echo ""
echo "=== SNAPSHOTS ==="
snap=(
  "POLICY.md"
  "POLICY.sha256"
  "REGISTRY.json"
  "REGISTRY.sha256"
  "scripts/petcare_progress_report.sh"
  "scripts/petcare_ph42b_closure_pack.sh"
  "FND/PROD_AUDIT_APPEND_ONLY_SPEC.md"
  "FND/AUDIT_HASH_CHAIN_MODEL.md"
  "FND/CODE_SCAFFOLD/audit_prod_append_only.py"
  "FND/CODE_SCAFFOLD/audit_hash_chain_verify.py"
  "TESTS/PROD_AUDIT_TAMPER_NEGATIVE_TESTS.md"
  "TESTS/test_audit_hash_chain_verify.py"
  "EVIDENCE/PH42B_AUDIT_LEDGER_VALIDATION_REPORT.md"
)
for f in "${snap[@]}"; do
  mkdir -p "${OUT}/snapshots/$(dirname "${f}")"
  cp -p "${ROOT}/${f}" "${OUT}/snapshots/${f}"
done

echo ""
echo "=== SHA256 (SNAPSHOT TREE) ==="
(
  cd "${OUT}/snapshots" || exit 1
  find . -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256 > "${OUT}/closure_sha256.txt"
)

echo ""
echo "=== MANIFEST.json ==="
"${PY}" - << 'PY' "${OUT}" "${PHASE}" "${TS_UTC}"
import json,os,sys,hashlib
out=sys.argv[1]; phase=sys.argv[2]; ts=sys.argv[3]
def sha256_file(p):
  h=hashlib.sha256()
  with open(p,"rb") as f:
    for b in iter(lambda: f.read(1024*1024), b""):
      h.update(b)
  return h.hexdigest()
snap_root=os.path.join(out,"snapshots")
records=[]
for r,ds,fs in os.walk(snap_root):
  for fn in fs:
    ap=os.path.join(r,fn)
    rel=os.path.relpath(ap,out).replace("\\","/")
    records.append((rel,sha256_file(ap)))
records.sort(key=lambda x:x[0])
manifest={
  "pack": phase,
  "timestamp_utc": ts,
  "out_dir": out.replace("\\","/"),
  "snapshot_count": len(records),
  "snapshots": [{"path":p,"sha256":h} for p,h in records],
  "notes": ["PH42-B: append-only audit ledger spec + hash-chain verifier + tamper tests"]
}
with open(os.path.join(out,"MANIFEST.json"),"w",encoding="utf-8",newline="\n") as f:
  json.dump(manifest,f,indent=2,ensure_ascii=False); f.write("\n")
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

echo ""
echo "=== SUMMARY ==="
echo "OUT=${OUT}"
echo "ZIP=${ZIP}"
echo "ZIP_SHA=${ZIP}.sha256"
echo "DONE"
