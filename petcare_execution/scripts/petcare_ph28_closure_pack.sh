#!/usr/bin/env bash
set -euo pipefail

PHASE="PETCARE-PH28-CLOSURE"
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

VERIFIER="${REPO_ROOT}/FND/CODE_SCAFFOLD/storage/audit_bundle_verifier.py"

echo "=============================================="
echo "PetCare PH28 CLOSURE PACK"
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
for f in "${REG}" "${REG_PIN}" "${POL}" "${POL_PIN}" "${VERIFIER}"; do
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
bash "${REPO_ROOT}/scripts/petcare_policy_drift_check.sh"
bash "${REPO_ROOT}/scripts/petcare_registry_drift_check.sh"

echo ""
echo "=== CI GATES (IF PRESENT) ==="
if [ -f "${REPO_ROOT}/scripts/petcare_ci_gates.sh" ]; then
  bash "${REPO_ROOT}/scripts/petcare_ci_gates.sh" | tee "${OUT}/ci_gates.txt"
else
  echo "SKIP: scripts/petcare_ci_gates.sh not present"
fi

echo ""
echo "=== PYTEST (FULL SUITE) ==="
"${PY}" -m pytest -q | tee "${OUT}/pytest.txt"

echo ""
echo "=== GENERATE DETERMINISTIC AUDIT BUNDLE (RUN A) ==="
"${PY}" - << 'PY' > "${OUT}/bundle_a.json"
import json
from FND.CODE_SCAFFOLD.storage.audit_bundle_verifier import _fallback_bundle_checksum

bundle = {
  "tenant_id": "tenant_001",
  "export_id": "exp-001",
  "exported_at_utc": "2026-01-01T00:00:00Z",
  "events": [
    {"tenant_id":"tenant_001","sequence":1,"event":"CREATE","entity":"invoice","id":"INV-001"},
    {"tenant_id":"tenant_001","sequence":2,"event":"UPDATE","entity":"invoice","id":"INV-001"},
    {"tenant_id":"tenant_001","sequence":3,"event":"APPROVE","entity":"invoice","id":"INV-001"},
  ],
}

bundle["bundle_checksum"] = _fallback_bundle_checksum(bundle)
print(json.dumps(bundle, indent=2, ensure_ascii=False))
PY
echo "OK wrote ${OUT}/bundle_a.json"

echo ""
echo "=== GENERATE DETERMINISTIC AUDIT BUNDLE (RUN B) ==="
"${PY}" - << 'PY' > "${OUT}/bundle_b.json"
import json
from FND.CODE_SCAFFOLD.storage.audit_bundle_verifier import _fallback_bundle_checksum

bundle = {
  "tenant_id": "tenant_001",
  "export_id": "exp-001",
  "exported_at_utc": "2026-01-01T00:00:00Z",
  "events": [
    {"tenant_id":"tenant_001","sequence":1,"event":"CREATE","entity":"invoice","id":"INV-001"},
    {"tenant_id":"tenant_001","sequence":2,"event":"UPDATE","entity":"invoice","id":"INV-001"},
    {"tenant_id":"tenant_001","sequence":3,"event":"APPROVE","entity":"invoice","id":"INV-001"},
  ],
}

bundle["bundle_checksum"] = _fallback_bundle_checksum(bundle)
print(json.dumps(bundle, indent=2, ensure_ascii=False))
PY
echo "OK wrote ${OUT}/bundle_b.json"

echo ""
echo "=== ASSERT DETERMINISM (A == B) ==="
SHA_A="$(shasum -a 256 "${OUT}/bundle_a.json" | awk '{print $1}')"
SHA_B="$(shasum -a 256 "${OUT}/bundle_b.json" | awk '{print $1}')"
echo "sha_a=${SHA_A}"
echo "sha_b=${SHA_B}"
if [ "${SHA_A}" != "${SHA_B}" ]; then
  echo "FAIL: nondeterministic bundle output (A != B)"
  exit 3
fi
echo "OK determinism confirmed"

echo ""
echo "=== VERIFY VALID BUNDLE (MUST PASS) ==="
set +e
"${PY}" "${VERIFIER}" "${OUT}/bundle_a.json" | tee "${OUT}/verify_valid.txt"
RC_VALID="${PIPESTATUS[0]}"
set -e
echo "RC_VALID=${RC_VALID}"
if [ "${RC_VALID}" -ne 0 ]; then
  echo "FAIL: valid bundle did not verify"
  exit 4
fi
echo "OK valid bundle verification PASS"

echo ""
echo "=== GENERATE TAMPERED BUNDLE (CHECKSUM NOT UPDATED) ==="
SRC_BUNDLE="${OUT}/bundle_a.json" "${PY}" - << 'PY' > "${OUT}/bundle_tampered.json"
import json, os

src = os.environ["SRC_BUNDLE"]
b = json.load(open(src, "r", encoding="utf-8"))
b["events"][0]["id"] = "INV-TAMPERED"
print(json.dumps(b, indent=2, ensure_ascii=False))
PY
echo "OK wrote ${OUT}/bundle_tampered.json"

echo ""
echo "=== VERIFY TAMPERED BUNDLE (MUST FAIL) ==="
set +e
"${PY}" "${VERIFIER}" "${OUT}/bundle_tampered.json" | tee "${OUT}/verify_tampered.txt"
RC_TAMPER="${PIPESTATUS[0]}"
set -e
echo "RC_TAMPER=${RC_TAMPER}"
if [ "${RC_TAMPER}" -eq 0 ]; then
  echo "FAIL: tampered bundle unexpectedly verified"
  exit 5
fi
echo "OK tampered bundle verification FAIL (expected)"

echo ""
echo "=== UPDATE REGISTRY: PH28 -> Closed ==="
"${PY}" - << 'PY'
import json,os

reg_path="REGISTRY.json"
with open(reg_path,"r",encoding="utf-8") as f:
  data=json.load(f)

phases=data.get("phases",[])
found=False
for p in phases:
  if p.get("phase")=="PH28":
    p["status"]="Closed"
    found=True

if not found:
  raise SystemExit("FAIL: PH28 not found in REGISTRY.json")

tmp=reg_path+".tmp"
with open(tmp,"w",encoding="utf-8",newline="\n") as f:
  json.dump(data,f,indent=2,ensure_ascii=False)
  f.write("\n")
os.replace(tmp,reg_path)

print("OK PH28 marked Closed in REGISTRY.json")
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
echo "=== SNAPSHOTS (KEY FILES) ==="
mkdir -p "${OUT}/snapshots"
cp -p "REGISTRY.json" "${OUT}/snapshots/REGISTRY.json"
cp -p "REGISTRY.sha256" "${OUT}/snapshots/REGISTRY.sha256"
cp -p "POLICY.md" "${OUT}/snapshots/POLICY.md"
cp -p "POLICY.sha256" "${OUT}/snapshots/POLICY.sha256"
cp -p "scripts/petcare_ph28_closure_pack.sh" "${OUT}/snapshots/scripts_petcare_ph28_closure_pack.sh"
cp -p "FND/CODE_SCAFFOLD/storage/audit_bundle_verifier.py" "${OUT}/snapshots/audit_bundle_verifier.py"
echo "OK snapshots copied"

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
