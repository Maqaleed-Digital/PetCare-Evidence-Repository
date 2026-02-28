#!/usr/bin/env bash
set -euo pipefail

PACK="PETCARE-PH45-CLOSURE"
TS_UTC="$(date -u +"%Y%m%dT%H%M%SZ")"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}" || exit 1

OUT_ROOT="${REPO_ROOT}/evidence_output/${PACK}"
OUT="${OUT_ROOT}/${TS_UTC}"

ZIP_IN="${1:-}"
if [ -z "${ZIP_IN}" ]; then
  ZIP_IN="$(ls -1t "${REPO_ROOT}/evidence_output/PETCARE-PH44B-CLOSURE"/PETCARE-PH44B-CLOSURE_*.zip 2>/dev/null | head -1 || true)"
fi

if [ -z "${ZIP_IN}" ] || [ ! -f "${ZIP_IN}" ]; then
  echo "ERROR: PH44B input zip missing. Provide arg1 or ensure a PH44B zip exists."
  exit 2
fi

echo "=============================================="
echo "PetCare PH45 CLOSURE PACK"
echo "pack=${PACK}"
echo "timestamp_utc=${TS_UTC}"
echo "repo_root=${REPO_ROOT}"
echo "out=${OUT}"
echo "ph44b_zip_in=${ZIP_IN}"
echo "=============================================="

echo "=== PRECHECK: CLEAN TREE REQUIRED ==="
if [ -n "$(git status --porcelain)" ]; then
  echo "ERROR: repo is dirty"
  git status -sb
  exit 3
fi

mkdir -p "${OUT}/input" "${OUT}/verify" "${OUT}/EVIDENCE" "${OUT}/snapshots" "${OUT}/work"

echo "=== COPY INPUT ZIP (+ sidecar if present) ==="
cp -p "${ZIP_IN}" "${OUT}/input/PH44B.zip"
if [ -f "${ZIP_IN}.sha256" ]; then
  cp -p "${ZIP_IN}.sha256" "${OUT}/input/PH44B.zip.sha256"
fi

echo "=== VERIFY PH44B ZIP (MUST PASS) ==="
VERIFY_OUT="${OUT}/verify/ph44b_zip_verify"
mkdir -p "${VERIFY_OUT}"
bash "${REPO_ROOT}/scripts/petcare_verify_closure_zip.sh" "${OUT}/input/PH44B.zip" "${VERIFY_OUT}"
PH44B_PASS="$(python3 - <<'PY' "${VERIFY_OUT}/results/VERIFY_RESULT.json"
import json, sys
j=json.load(open(sys.argv[1],"r",encoding="utf-8"))
print(j.get("overall_pass","false"))
PY
)"
if [ "${PH44B_PASS}" != "true" ]; then
  echo "ERROR: PH44B zip did not verify PASS"
  cat "${VERIFY_OUT}/results/VERIFY_RESULT.json" || true
  exit 4
fi

echo "=== EXTRACT PH44B MANIFEST.json (SAFE, NO FULL EXTRACT) ==="
PH44B_MANIFEST="${OUT}/work/PH44B_MANIFEST.json"
export PC_ZIP="${OUT}/input/PH44B.zip"
export PC_OUT="${PH44B_MANIFEST}"
python3 - <<'PY'
import os, zipfile, sys
zpath=os.environ["PC_ZIP"]
out=os.environ["PC_OUT"]
with zipfile.ZipFile(zpath,"r") as z:
    # Find first MANIFEST.json inside the zip
    cand=[n for n in z.namelist() if n.endswith("/MANIFEST.json") or n=="MANIFEST.json"]
    if not cand:
        print("ERROR: no MANIFEST.json in PH44B zip")
        sys.exit(10)
    name=sorted(cand)[0]
    data=z.read(name)
open(out,"wb").write(data)
print("OK wrote", out, "from", name)
PY

echo "=== DERIVE INDEX APPEND FIELDS (DETERMINISTIC) ==="
PH44B_ZIP_SHA="$(shasum -a 256 "${OUT}/input/PH44B.zip" | awk '{print $1}')"
PH44B_SIDECAR_SHA="(missing)"
if [ -f "${OUT}/input/PH44B.zip.sha256" ]; then
  PH44B_SIDECAR_SHA="$(awk '{print $1}' < "${OUT}/input/PH44B.zip.sha256")"
fi

VERIFIER_PACK="PETCARE-PH44B-CLOSURE"
VERIFIER_GIT_HEAD="$(git rev-parse HEAD)"
VERIFIER_GIT_DESCRIBE="$(git describe --tags --dirty --always)"

VERIFIED_ZIP_SHA="$(python3 - <<'PY' "${PH44B_MANIFEST}"
import json, sys
m=json.load(open(sys.argv[1],"r",encoding="utf-8"))
print(((m.get("input_zip") or {}).get("sha256")) or "")
PY
)"
if [ -z "${VERIFIED_ZIP_SHA}" ]; then
  echo "ERROR: could not read input_zip.sha256 from PH44B MANIFEST.json"
  exit 5
fi

# Best-effort pack id inference: from PH44B manifest input_zip.path_provided basename
VERIFIED_PACK="$(python3 - <<'PY' "${PH44B_MANIFEST}"
import json, sys, os, re
m=json.load(open(sys.argv[1],"r",encoding="utf-8"))
p=((m.get("input_zip") or {}).get("path_provided")) or ""
b=os.path.basename(p)
# Pattern: PETCARE-PH43B-CLOSURE_YYYY...Z.zip -> extract PETCARE-PH43B-CLOSURE
m2=re.match(r'^(PETCARE-[A-Z0-9]+-CLOSURE)_\d{8}T\d{6}Z\.zip$', b)
if m2:
    print(m2.group(1))
else:
    print("UNKNOWN_PACK_ID")
PY
)"

echo "verified_pack=${VERIFIED_PACK}"
echo "verified_zip_sha256=${VERIFIED_ZIP_SHA}"
echo "verifier_pack=${VERIFIER_PACK}"
echo "verifier_zip_sha256=${PH44B_ZIP_SHA}"

echo "=== APPEND VERIFICATION INDEX (HASH-LINKED) ==="
INDEX_PATH="${REPO_ROOT}/FND/VERIFICATION_INDEX.json"
python3 "${REPO_ROOT}/scripts/petcare_verification_index_append.py" \
  --index "${INDEX_PATH}" \
  --verified_pack "${VERIFIED_PACK}" \
  --verified_zip_sha256 "${VERIFIED_ZIP_SHA}" \
  --verifier_pack "${VERIFIER_PACK}" \
  --verifier_zip_sha256 "${PH44B_ZIP_SHA}" \
  --verifier_git_head "${VERIFIER_GIT_HEAD}" \
  --verifier_git_describe "${VERIFIER_GIT_DESCRIBE}" \
  --overall_pass "true" \
  --ts_utc "${TS_UTC}" \
  | tee "${OUT}/EVIDENCE/index_append_stdout.txt"

echo "=== WRITE INDEX SHA256 (DETERMINISTIC) ==="
shasum -a 256 "${INDEX_PATH}" | awk '{print $1}' > "${REPO_ROOT}/FND/VERIFICATION_INDEX.sha256"

echo "=== POLICY ADDENDUM SNAPSHOT ==="
cp -p "${REPO_ROOT}/POLICY_ADDENDUM_PH45_VERIFICATION_INDEX.md" "${OUT}/EVIDENCE/POLICY_ADDENDUM_PH45_VERIFICATION_INDEX.md"

echo "=== PACK MANIFEST (PH45) ==="
cat > "${OUT}/MANIFEST.json" <<JSON
{
  "pack": "${PACK}",
  "ts_utc": "${TS_UTC}",
  "repo_root": "${REPO_ROOT}",
  "git_head": "${VERIFIER_GIT_HEAD}",
  "git_describe": "${VERIFIER_GIT_DESCRIBE}",
  "inputs": {
    "ph44b_zip_path": "${ZIP_IN}",
    "ph44b_zip_sha256": "${PH44B_ZIP_SHA}",
    "ph44b_zip_sidecar_sha256": "${PH44B_SIDECAR_SHA}"
  },
  "index_append": {
    "verified_pack": "${VERIFIED_PACK}",
    "verified_zip_sha256": "${VERIFIED_ZIP_SHA}",
    "verifier_pack": "${VERIFIER_PACK}",
    "verifier_zip_sha256": "${PH44B_ZIP_SHA}",
    "overall_pass": true
  },
  "files": {
    "ph44b_zip_copy": "input/PH44B.zip",
    "ph44b_verify_result": "verify/ph44b_zip_verify/results/VERIFY_RESULT.json",
    "ph44b_verify_report": "verify/ph44b_zip_verify/results/VERIFY_REPORT.md",
    "index": "snapshots/FND/VERIFICATION_INDEX.json",
    "index_sha256": "snapshots/FND/VERIFICATION_INDEX.sha256",
    "policy_addendum": "EVIDENCE/POLICY_ADDENDUM_PH45_VERIFICATION_INDEX.md",
    "append_stdout": "EVIDENCE/index_append_stdout.txt"
  }
}
JSON

echo "=== SNAPSHOT ARTIFACTS ==="
mkdir -p "${OUT}/snapshots/FND" "${OUT}/snapshots/scripts"
cp -p "${REPO_ROOT}/FND/VERIFICATION_INDEX.json" "${OUT}/snapshots/FND/VERIFICATION_INDEX.json"
cp -p "${REPO_ROOT}/FND/VERIFICATION_INDEX.sha256" "${OUT}/snapshots/FND/VERIFICATION_INDEX.sha256"
cp -p "${REPO_ROOT}/scripts/petcare_verification_index_append.py" "${OUT}/snapshots/scripts/petcare_verification_index_append.py"
cp -p "${REPO_ROOT}/scripts/petcare_verification_policy_check.sh" "${OUT}/snapshots/scripts/petcare_verification_policy_check.sh"
cp -p "${REPO_ROOT}/scripts/petcare_ph45_closure_pack.sh" "${OUT}/snapshots/scripts/petcare_ph45_closure_pack.sh"

echo "=== SHA256 LIST (DETERMINISTIC; NO SELF-REFERENCE) ==="
TMP_SHA="${OUT}/.closure_sha256.tmp"
rm -f "${TMP_SHA}"
find "${OUT}" -type f \
  ! -name "closure_sha256.txt" \
  ! -name ".closure_sha256.tmp" \
  -print0 \
| LC_ALL=C sort -z \
| xargs -0 shasum -a 256 \
> "${TMP_SHA}"
mv -f "${TMP_SHA}" "${OUT}/closure_sha256.txt"

echo "=== ZIP ==="
mkdir -p "${OUT_ROOT}"
cd "${OUT_ROOT}" || exit 1
BASE="$(basename "${OUT}")"
ZIP="${PACK}_${BASE}.zip"
rm -f "${ZIP}" "${ZIP}.sha256"
zip -r "${ZIP}" "${BASE}" >/dev/null
shasum -a 256 "${ZIP}" > "${ZIP}.sha256"

echo "PASS ${PACK}"
echo "out=${OUT}"
echo "zip=${OUT_ROOT}/${ZIP}"
echo "zip_sha256=${OUT_ROOT}/${ZIP}.sha256"
