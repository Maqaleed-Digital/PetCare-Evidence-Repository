#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}" || exit 1

PH43B_ZIP="${1:-}"
OUT_DIR="${2:-}"

if [ -z "${PH43B_ZIP}" ] || [ -z "${OUT_DIR}" ]; then
  echo "ERROR: missing args"
  echo "USAGE: scripts/petcare_ph44_verify_ph43b_zip.sh <PH43B_ZIP_PATH> <OUT_DIR>"
  exit 2
fi

if [ ! -f "${PH43B_ZIP}" ]; then
  echo "ERROR: input zip not found: ${PH43B_ZIP}"
  exit 3
fi

mkdir -p "${OUT_DIR}/logs" "${OUT_DIR}/work" "${OUT_DIR}/results"

LOG_TXT="${OUT_DIR}/logs/ph44_verify_log.txt"
RESULT_JSON="${OUT_DIR}/results/PH44_VERIFY_RESULT.json"
REPORT_MD="${OUT_DIR}/results/PH44_VERIFY_REPORT.md"

exec > >(tee -a "${LOG_TXT}") 2>&1

echo "=== PH44 VERIFY (PH43-B ZIP) ==="
echo "repo_root=${REPO_ROOT}"
echo "input_zip=${PH43B_ZIP}"
echo "out_dir=${OUT_DIR}"

ZIP_SHA256="$(shasum -a 256 "${PH43B_ZIP}" | awk '{print $1}')"
echo "zip_sha256=${ZIP_SHA256}"

SIDE_SHA="${PH43B_ZIP}.sha256"
ZIP_SHA256_MATCH="(no_sidecar)"
if [ -f "${SIDE_SHA}" ]; then
  WANT="$(cat "${SIDE_SHA}" | awk '{print $1}')"
  ZIP_SHA256_MATCH="false"
  if [ "${WANT}" = "${ZIP_SHA256}" ]; then ZIP_SHA256_MATCH="true"; fi
  echo "sidecar_sha256=${WANT}"
  echo "sidecar_match=${ZIP_SHA256_MATCH}"
else
  echo "sidecar_sha256=(missing)"
fi

WORK="${OUT_DIR}/work/extracted"
rm -rf "${WORK}"
mkdir -p "${WORK}"

echo "=== EXTRACT ==="
export PH44_ZIP_PATH="${PH43B_ZIP}"
export PH44_WORK_DIR="${WORK}"
python3 - <<'PY'
import os, zipfile, sys
zip_path = os.environ["PH44_ZIP_PATH"]
work = os.environ["PH44_WORK_DIR"]

with zipfile.ZipFile(zip_path, "r") as z:
    for m in z.infolist():
        name = m.filename
        if name.startswith("/") or ".." in name.split("/"):
            print("ERROR: unsafe zip path traversal:", name)
            sys.exit(10)
    z.extractall(work)

print("EXTRACT_OK")
PY

BASE_DIR="$(find "${WORK}" -maxdepth 3 -type f -name 'MANIFEST.json' -print | head -1 | sed 's#/MANIFEST.json##')"
if [ -z "${BASE_DIR}" ]; then
  echo "ERROR: could not locate MANIFEST.json after extraction"
  exit 5
fi

echo "base_dir=${BASE_DIR}"

MANIFEST="${BASE_DIR}/MANIFEST.json"
CLOSURE_SHA="${BASE_DIR}/closure_sha256.txt"
ATTEST="${BASE_DIR}/attestation/ARTIFACT_BOUND_ATTESTATION.json"

if [ ! -f "${MANIFEST}" ]; then echo "ERROR: missing MANIFEST.json"; exit 6; fi
if [ ! -f "${CLOSURE_SHA}" ]; then echo "ERROR: missing closure_sha256.txt"; exit 7; fi
if [ ! -f "${ATTEST}" ]; then echo "ERROR: missing attestation record"; exit 8; fi

echo "=== MANIFEST JSON ==="
export PH44_MANIFEST_PATH="${MANIFEST}"
python3 - <<'PY'
import json, os
json.load(open(os.environ["PH44_MANIFEST_PATH"], "r", encoding="utf-8"))
print("MANIFEST_JSON_OK")
PY

echo "=== VERIFY closure_sha256.txt ==="
VERIFY_HASH_OK="true"
export PH44_BASE_DIR="${BASE_DIR}"
export PH44_CLOSURE_SHA="${CLOSURE_SHA}"

python3 - <<'PY' || VERIFY_HASH_OK="false"
import os, sys, hashlib

base = os.environ["PH44_BASE_DIR"]
sha_list = os.environ["PH44_CLOSURE_SHA"]

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

want = {}
with open(sha_list, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            print("ERROR: bad line:", line)
            sys.exit(30)
        digest = parts[0]
        path = " ".join(parts[1:])
        if path.startswith("*"):
            path = path[1:]
        if path.startswith("./"):
            path = path[2:]
        rel = os.path.relpath(path, base) if path.startswith(base + os.sep) else path
        want[rel] = digest

failed = 0
for rel, digest in want.items():
    p = os.path.join(base, rel)
    if not os.path.isfile(p):
        print("MISSING_FILE:", rel)
        failed += 1
        continue
    got = sha256_file(p)
    if got != digest:
        print("HASH_MISMATCH:", rel, "want", digest, "got", got)
        failed += 1

if failed:
    print("CLOSURE_SHA256_VERIFY_FAIL count=", failed)
    sys.exit(31)

print("CLOSURE_SHA256_VERIFY_OK count=", len(want))
PY

echo "closure_sha256_verify_ok=${VERIFY_HASH_OK}"

echo "=== EXTRACT ARTIFACT BINDING VALUES ==="
export PH44_ATTEST_PATH="${ATTEST}"
export PH44_OUT_DIR="${OUT_DIR}"

python3 - <<'PY' > "${OUT_DIR}/results/_ph44_extract_values.txt"
import json, os

base = os.environ["PH44_BASE_DIR"]
manifest = json.load(open(os.environ["PH44_MANIFEST_PATH"], "r", encoding="utf-8"))
att = json.load(open(os.environ["PH44_ATTEST_PATH"], "r", encoding="utf-8"))

m_sha = (manifest.get("artifact") or {}).get("sha256","")
a_sha = (att.get("artifact") or {}).get("sha256","")
name = (manifest.get("artifact") or {}).get("name","") or (att.get("artifact") or {}).get("name","")
copy = os.path.join(base, "artifact", name) if name else ""

print("MANIFEST_ART_SHA256=" + m_sha)
print("ATTEST_ART_SHA256=" + a_sha)
print("ARTIFACT_NAME=" + name)
print("ARTIFACT_COPY_PATH=" + copy)
PY

set -a
. "${OUT_DIR}/results/_ph44_extract_values.txt"
set +a

if [ -z "${ARTIFACT_NAME}" ]; then echo "ERROR: could not determine artifact name"; exit 9; fi
if [ ! -f "${ARTIFACT_COPY_PATH}" ]; then echo "ERROR: missing artifact copy: ${ARTIFACT_COPY_PATH}"; exit 10; fi

ARTIFACT_COPY_SHA="$(shasum -a 256 "${ARTIFACT_COPY_PATH}" | awk '{print $1}')"

ART_SHA_MATCH="true"
if [ -z "${MANIFEST_ART_SHA256}" ] || [ -z "${ATTEST_ART_SHA256}" ]; then ART_SHA_MATCH="false"; fi
if [ "${MANIFEST_ART_SHA256}" != "${ATTEST_ART_SHA256}" ]; then ART_SHA_MATCH="false"; fi
if [ "${ARTIFACT_COPY_SHA}" != "${MANIFEST_ART_SHA256}" ]; then ART_SHA_MATCH="false"; fi

OVERALL_PASS="true"
if [ "${VERIFY_HASH_OK}" != "true" ]; then OVERALL_PASS="false"; fi
if [ "${ART_SHA_MATCH}" != "true" ]; then OVERALL_PASS="false"; fi
if [ "${ZIP_SHA256_MATCH}" = "false" ]; then OVERALL_PASS="false"; fi

cat > "${RESULT_JSON}" <<EOF
{
  "schema": "petcare.ph44.verify_result.v1",
  "input_zip": "${PH43B_ZIP}",
  "zip_sha256": "${ZIP_SHA256}",
  "sidecar_present": "$( [ -f "${SIDE_SHA}" ] && echo true || echo false )",
  "sidecar_match": "${ZIP_SHA256_MATCH}",
  "closure_sha256_verify_ok": "${VERIFY_HASH_OK}",
  "artifact_name": "${ARTIFACT_NAME}",
  "manifest_artifact_sha256": "${MANIFEST_ART_SHA256}",
  "attestation_artifact_sha256": "${ATTEST_ART_SHA256}",
  "artifact_copy_sha256": "${ARTIFACT_COPY_SHA}",
  "artifact_sha_all_match": "${ART_SHA_MATCH}",
  "overall_pass": "${OVERALL_PASS}"
}
EOF

cat > "${REPORT_MD}" <<EOF
# PH44 — Verification Report (PH43-B ZIP)

overall_pass: ${OVERALL_PASS}
EOF

if [ "${OVERALL_PASS}" != "true" ]; then
  echo "FAIL PH44 verify"
  exit 40
fi

echo "PASS PH44 verify"
