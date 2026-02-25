#!/usr/bin/env bash
set -euo pipefail

PHASE="PETCARE-PH27-CLOSURE"
TS_UTC="$(date -u +%Y%m%dT%H%M%SZ)"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_ROOT="${REPO_ROOT}/evidence_output/${PHASE}"
OUT="${OUT_ROOT}/${TS_UTC}"

PY="${REPO_ROOT}/.venv/bin/python"
if [ ! -x "${PY}" ]; then PY="python3"; fi

VERIFIER="${REPO_ROOT}/FND/CODE_SCAFFOLD/storage/audit_bundle_verifier.py"

echo "=============================================="
echo "PetCare PH27 CLOSURE PACK"
echo "pack=${PHASE}"
echo "timestamp_utc=${TS_UTC}"
echo "repo_root=${REPO_ROOT}"
echo "out=${OUT}"
echo "python_bin=${PY}"
echo "=============================================="

mkdir -p "${OUT}"

echo ""
echo "=== PRE-FLIGHT ==="
if [ ! -f "${VERIFIER}" ]; then
  echo "FAIL: verifier missing at ${VERIFIER}"
  exit 2
fi
echo "OK verifier present"

echo ""
echo "=== UNIT TESTS ==="
"${PY}" -m pytest -q | tee "${OUT}/pytest.txt"

echo ""
echo "=== GENERATE VALID AUDIT BUNDLE (USING VERIFIER CHECKSUM) ==="
VALID="${OUT}/valid_bundle.json"
"${PY}" - << 'PY' > "${VALID}"
import json,datetime
from FND.CODE_SCAFFOLD.storage.audit_bundle_verifier import _fallback_bundle_checksum

bundle={
  "tenant_id":"tenant_001",
  "events":[
    {"tenant_id":"tenant_001","sequence":1,"event":"CREATE","entity":"invoice","id":"INV-001","prev_checksum":""},
    {"tenant_id":"tenant_001","sequence":2,"event":"UPDATE","entity":"invoice","id":"INV-001","prev_checksum":""},
  ],
  "generated_utc":datetime.datetime.utcnow().replace(microsecond=0).isoformat()+"Z"
}

bundle["bundle_checksum"]=_fallback_bundle_checksum(bundle)
print(json.dumps(bundle,indent=2,ensure_ascii=False))
PY
echo "OK wrote valid bundle ${VALID}"

echo ""
echo "=== VERIFY VALID BUNDLE ==="
set +e
"${PY}" "${VERIFIER}" "${VALID}" | tee "${OUT}/verify_valid.txt"
RC_VALID="${PIPESTATUS[0]}"
set -e
echo "RC_VALID=${RC_VALID}"
if [ "${RC_VALID}" -ne 0 ]; then
  echo "FAIL: valid bundle did not verify"
  exit 3
fi
echo "OK valid bundle verification PASS"

echo ""
echo "=== GENERATE TAMPERED BUNDLE (CHECKSUM NOT UPDATED) ==="
TAMPER="${OUT}/tampered_bundle.json"
"${PY}" - "${VALID}" "${TAMPER}" << 'PY' > "${OUT}/tamper_path.txt"
import json,sys
src=sys.argv[1]
dst=sys.argv[2]
b=json.load(open(src,"r",encoding="utf-8"))
b["events"][0]["id"]="INV-TAMPERED"
json.dump(b,open(dst,"w",encoding="utf-8",newline="\n"),indent=2,ensure_ascii=False)
print(dst)
PY
echo "OK tampered bundle written ${TAMPER}"

echo ""
echo "=== VERIFY TAMPERED BUNDLE (MUST FAIL) ==="
set +e
"${PY}" "${VERIFIER}" "${TAMPER}" | tee "${OUT}/verify_tampered.txt"
RC_TAMPER="${PIPESTATUS[0]}"
set -e
echo "RC_TAMPER=${RC_TAMPER}"
if [ "${RC_TAMPER}" -eq 0 ]; then
  echo "FAIL: tampered bundle unexpectedly passed verification"
  exit 4
fi
echo "OK tampered bundle verification FAIL (expected)"

echo ""
echo "=== UPDATE REGISTRY: PH27 -> Closed ==="
"${PY}" - << 'PY'
import json,os
reg_path="REGISTRY.json"
data=json.load(open(reg_path,"r",encoding="utf-8"))
found=False
for p in data.get("phases",[]):
  if p.get("phase")=="PH27":
    p["status"]="Closed"
    found=True
if not found:
  raise SystemExit("FAIL: PH27 not found in REGISTRY.json")
tmp=reg_path+".tmp"
with open(tmp,"w",encoding="utf-8",newline="\n") as f:
  json.dump(data,f,indent=2,ensure_ascii=False)
  f.write("\n")
os.replace(tmp,reg_path)
print("OK PH27 marked Closed in REGISTRY.json")
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
echo "=== SNAPSHOT: KEY FILES ==="
mkdir -p "${OUT}/snapshots"
cp -p "FND/CODE_SCAFFOLD/storage/audit_bundle_verifier.py" "${OUT}/snapshots/audit_bundle_verifier.py"
cp -p "REGISTRY.json" "${OUT}/snapshots/REGISTRY.json"
cp -p "REGISTRY.sha256" "${OUT}/snapshots/REGISTRY.sha256"
echo "OK snapshots copied"

echo ""
echo "=== SHA256 TREE ==="
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
