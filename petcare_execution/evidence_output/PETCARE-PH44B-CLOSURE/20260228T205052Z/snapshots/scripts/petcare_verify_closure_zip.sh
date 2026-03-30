#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}" || exit 1

ZIP_PATH="${1:-}"
OUT_DIR="${2:-}"

if [ -z "${ZIP_PATH}" ] || [ -z "${OUT_DIR}" ]; then
  echo "ERROR: missing args"
  echo "USAGE: scripts/petcare_verify_closure_zip.sh <CLOSURE_ZIP_PATH> <OUT_DIR>"
  exit 2
fi

if [ ! -f "${ZIP_PATH}" ]; then
  echo "ERROR: zip not found: ${ZIP_PATH}"
  exit 3
fi

mkdir -p "${OUT_DIR}/logs" "${OUT_DIR}/work" "${OUT_DIR}/results"
LOG_TXT="${OUT_DIR}/logs/verify_log.txt"
RESULT_JSON="${OUT_DIR}/results/VERIFY_RESULT.json"
REPORT_MD="${OUT_DIR}/results/VERIFY_REPORT.md"

if [ -z "${RESULT_JSON}" ] || [ -z "${REPORT_MD}" ]; then
  echo "ERROR: internal paths empty (RESULT_JSON/REPORT_MD)"
  echo "OUT_DIR=${OUT_DIR}"
  exit 4
fi

mkdir -p "$(dirname "${RESULT_JSON}")" "$(dirname "${REPORT_MD}")"

exec > >(tee -a "${LOG_TXT}") 2>&1

echo "=== VERIFY CLOSURE ZIP ==="
echo "repo_root=${REPO_ROOT}"
echo "zip_path=${ZIP_PATH}"
echo "out_dir=${OUT_DIR}"

ZIP_SHA256="$(shasum -a 256 "${ZIP_PATH}" | awk "{print \$1}")"
echo "zip_sha256=${ZIP_SHA256}"

SIDE_SHA="${ZIP_PATH}.sha256"
SIDECAR_PRESENT="false"
SIDECAR_MATCH="(no_sidecar)"
if [ -f "${SIDE_SHA}" ]; then
  SIDECAR_PRESENT="true"
  WANT="$(awk "{print \$1}" < "${SIDE_SHA}")"
  SIDECAR_MATCH="false"
  if [ "${WANT}" = "${ZIP_SHA256}" ]; then SIDECAR_MATCH="true"; fi
  echo "sidecar_sha256=${WANT}"
  echo "sidecar_match=${SIDECAR_MATCH}"
else
  echo "sidecar_sha256=(missing)"
fi

WORK="${OUT_DIR}/work/extracted"
rm -rf "${WORK}"
mkdir -p "${WORK}"

echo "=== EXTRACT (SAFE) ==="
export PC_ZIP_PATH="${ZIP_PATH}"
export PC_WORK_DIR="${WORK}"
python3 - <<'PY'
import os, zipfile, sys
zip_path = os.environ["PC_ZIP_PATH"]
work = os.environ["PC_WORK_DIR"]

with zipfile.ZipFile(zip_path, "r") as z:
    for m in z.infolist():
        name = m.filename
        if name.startswith("/") or ".." in name.split("/"):
            print("ERROR: unsafe zip path traversal:", name)
            sys.exit(10)
    z.extractall(work)

print("EXTRACT_OK")
PY

BASE_DIR="$(find "${WORK}" -maxdepth 3 -type f -name MANIFEST.json -print | head -1 | sed s#/MANIFEST.json##)"
if [ -z "${BASE_DIR}" ]; then
  echo "ERROR: could not locate MANIFEST.json after extraction"
  exit 5
fi
echo "base_dir=${BASE_DIR}"

MANIFEST="${BASE_DIR}/MANIFEST.json"
CLOSURE_SHA="${BASE_DIR}/closure_sha256.txt"

if [ ! -f "${MANIFEST}" ]; then echo "ERROR: missing MANIFEST.json"; exit 6; fi
if [ ! -f "${CLOSURE_SHA}" ]; then echo "ERROR: missing closure_sha256.txt"; exit 7; fi

echo "=== MANIFEST JSON PARSE ==="
export PC_MANIFEST_PATH="${MANIFEST}"
python3 - <<'PY'
import json, os
json.load(open(os.environ["PC_MANIFEST_PATH"], "r", encoding="utf-8"))
print("MANIFEST_JSON_OK")
PY

echo "=== VERIFY closure_sha256.txt ==="
VERIFY_HASH_OK="true"
python3 - <<'PY' "${BASE_DIR}" "${CLOSURE_SHA}" || VERIFY_HASH_OK="false"
import sys, os, hashlib
base = sys.argv[1]
sha_list = sys.argv[2]

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

echo "=== VERIFY MANIFEST FILE REFERENCES (files.* must exist) ==="
FILES_OK="true"
python3 - <<'PY' "${BASE_DIR}" "${MANIFEST}" || FILES_OK="false"
import json, sys, os
base = sys.argv[1]
m = json.load(open(sys.argv[2], "r", encoding="utf-8"))
files = m.get("files") or {}
missing = []
for k, rel in files.items():
    if not isinstance(rel, str) or not rel:
        missing.append((k, "(invalid)"))
        continue
    p = os.path.join(base, rel)
    if not os.path.isfile(p):
        missing.append((k, rel))
if missing:
    for k, rel in missing:
        print("MANIFEST_FILE_MISSING:", k, rel)
    raise SystemExit(41)
print("MANIFEST_FILES_OK count=", len(files))
PY
echo "manifest_files_ok=${FILES_OK}"

OVERALL_PASS="true"
if [ "${SIDECAR_MATCH}" = "false" ]; then OVERALL_PASS="false"; fi
if [ "${VERIFY_HASH_OK}" != "true" ]; then OVERALL_PASS="false"; fi
if [ "${FILES_OK}" != "true" ]; then OVERALL_PASS="false"; fi

echo "result_json_path=${RESULT_JSON}"
echo "report_md_path=${REPORT_MD}"
cat > "${RESULT_JSON}" <<EOF
{
  "schema": "petcare.verify_closure_zip.v1",
  "zip_path": "${ZIP_PATH}",
  "zip_sha256": "${ZIP_SHA256}",
  "sidecar_present": "${SIDECAR_PRESENT}",
  "sidecar_match": "${SIDECAR_MATCH}",
  "base_dir": "${BASE_DIR}",
  "manifest_json_ok": true,
  "closure_sha256_verify_ok": "${VERIFY_HASH_OK}",
  "manifest_files_ok": "${FILES_OK}",
  "overall_pass": "${OVERALL_PASS}"
}
