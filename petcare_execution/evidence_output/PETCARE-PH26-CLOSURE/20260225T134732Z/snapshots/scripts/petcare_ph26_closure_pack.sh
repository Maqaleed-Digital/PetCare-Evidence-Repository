#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}" || exit 1

PHASE="PETCARE-PH26-CLOSURE"
TS_UTC="$(date -u +"%Y%m%dT%H%M%SZ")"
OUT_ROOT="${ROOT}/evidence_output/${PHASE}"
OUT="${OUT_ROOT}/${TS_UTC}"
ZIP="${OUT_ROOT}/${PHASE}_${TS_UTC}.zip"

PY="${ROOT}/.venv/bin/python"
if [ ! -x "${PY}" ]; then PY="python3"; fi

echo "=============================================="
echo "PetCare PH26 CLOSURE PACK"
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
  "REGISTRY.json"
  "REGISTRY.sha256"
  "POLICY.md"
  "POLICY.sha256"
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
echo "=== DRIFT CHECKS (PINNED) ==="
if [ -x "${ROOT}/scripts/petcare_policy_drift_check.sh" ]; then
  bash "${ROOT}/scripts/petcare_policy_drift_check.sh" | tee "${OUT}/policy_drift_check.txt"
else
  echo "WARN missing scripts/petcare_policy_drift_check.sh (skipping)" | tee "${OUT}/policy_drift_check.txt"
fi
if [ -x "${ROOT}/scripts/petcare_registry_drift_check.sh" ]; then
  bash "${ROOT}/scripts/petcare_registry_drift_check.sh" | tee "${OUT}/registry_drift_check.txt"
else
  echo "WARN missing scripts/petcare_registry_drift_check.sh (skipping)" | tee "${OUT}/registry_drift_check.txt"
fi

echo ""
echo "=== UNIT TESTS ==="
"${PY}" -m pytest -q | tee "${OUT}/pytest.txt"

echo ""
echo "=== OPTIONAL: VERIFY AUDIT BUNDLE (IF VERIFIER PRESENT) ==="
VERIFIER="${ROOT}/FND/CODE_SCAFFOLD/storage/audit_bundle_verifier.py"
SAMPLE="${OUT}/sample_audit_bundle.json"
if [ -f "${VERIFIER}" ]; then
  "${PY}" - << 'PY' "${SAMPLE}"
import json,datetime,hashlib,sys
path=sys.argv[1]
bundle={
  "tenant_id":"tenant_001",
  "events":[
    {"event":"CREATE","entity":"invoice","id":"INV-001"},
    {"event":"UPDATE","entity":"invoice","id":"INV-001"}
  ],
  "generated_utc":datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
}
payload=json.dumps(bundle,sort_keys=True).encode("utf-8")
bundle["bundle_checksum"]=hashlib.sha256(payload).hexdigest()
with open(path,"w",encoding="utf-8",newline="\n") as f:
  json.dump(bundle,f,indent=2,ensure_ascii=False)
  f.write("\n")
print("OK wrote sample bundle",path)
PY

  set +e
  "${PY}" "${VERIFIER}" "${SAMPLE}" > "${OUT}/audit_bundle_verify.txt" 2>&1
  RC=$?
  set -e
  echo "VERIFIER_RC=${RC}" | tee -a "${OUT}/audit_bundle_verify.txt"
  if [ "${RC}" -ne 0 ]; then
    echo "FAIL: audit bundle verifier returned non-zero (see ${OUT}/audit_bundle_verify.txt)"
    exit 1
  fi
  echo "OK audit bundle verification PASS" | tee -a "${OUT}/audit_bundle_verify.txt"
else
  echo "SKIP: verifier not present at ${VERIFIER}" | tee "${OUT}/audit_bundle_verify.txt"
fi

echo ""
echo "=== PROGRESS REPORT (SNAPSHOT) ==="
bash "${ROOT}/scripts/petcare_progress_report.sh" "." | tee "${OUT}/progress_report.txt"

echo ""
echo "=== SNAPSHOTS (CANONICAL INPUTS) ==="
snap=(
  "REGISTRY.json"
  "REGISTRY.sha256"
  "POLICY.md"
  "POLICY.sha256"
  "scripts/petcare_progress_report.sh"
  "scripts/petcare_ph26_closure_pack.sh"
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
snap=os.path.join(out,"snapshots")

def sha256_file(p):
  h=hashlib.sha256()
  with open(p,"rb") as f:
    for b in iter(lambda: f.read(1024*1024), b""):
      h.update(b)
  return h.hexdigest()

items=[]
for root,dirs,files in os.walk(snap):
  for fn in files:
    ap=os.path.join(root,fn)
    rel=os.path.relpath(ap,out).replace("\\","/")
    items.append({"path":rel,"sha256":sha256_file(ap)})

items.sort(key=lambda x:x["path"])

m={
  "pack": phase,
  "timestamp_utc": ts,
  "out_dir": out.replace("\\","/"),
  "snapshot_count": len(items),
  "snapshots": items,
  "notes": [
    "PH26 closure pack: pytest + drift checks + (optional) audit bundle verification if verifier exists.",
    "Deterministic snapshot tree hashed and zipped."
  ]
}

with open(os.path.join(out,"MANIFEST.json"),"w",encoding="utf-8",newline="\n") as f:
  json.dump(m,f,indent=2,ensure_ascii=False)
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
