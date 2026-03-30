#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}" || exit 1

PACK_ID="PETCARE-PH13-CLOSURE"
ts="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_ROOT="evidence_output/${PACK_ID}"
OUT="${OUT_ROOT}/${ts}"
mkdir -p "${OUT}"

echo "=============================================="
echo "PetCare PH13 CLOSURE PACK"
echo "pack=${PACK_ID}"
echo "timestamp_utc=${ts}"
echo "repo_root=${REPO_ROOT}"
echo "out=${REPO_ROOT}/${OUT}"
echo "=============================================="

echo "=== CAPTURE GIT CONTEXT ==="
git rev-parse --show-toplevel > "${OUT}/git_toplevel.txt" 2>/dev/null || true
git status -sb > "${OUT}/git_status.txt" 2>/dev/null || true
git log -1 --oneline > "${OUT}/git_head.txt" 2>/dev/null || true

echo "=== RUN TESTS (DETERMINISTIC LOG) ==="
TEST_LOG="${OUT}/pytest.txt"
set +e
python3 -m pytest -q > "${TEST_LOG}" 2>&1
PYTEST_RC=$?
set -e

echo "pytest_rc=${PYTEST_RC}" > "${OUT}/pytest_rc.txt"

echo "=== BUILD CLOSURE FILE LIST ==="
CLOSURE_LIST="${OUT}/closure_files.txt"
: > "${CLOSURE_LIST}"

add_file() {
  local f="$1"
  if [ -f "${f}" ]; then
    echo "${f}" >> "${CLOSURE_LIST}"
  fi
}

add_dir_files() {
  local d="$1"
  if [ -d "${d}" ]; then
    find "${d}" -type f -print | LC_ALL=C sort >> "${CLOSURE_LIST}"
  fi
}

add_file "README.md"
add_file "app.py"
add_dir_files "FND"
add_dir_files "UI6"
add_dir_files "docs"
add_dir_files "scripts"
add_dir_files "tests"

add_dir_files "${OUT}"

LC_ALL=C sort -u "${CLOSURE_LIST}" -o "${CLOSURE_LIST}"

echo "=== SNAPSHOT FILES (COPY) ==="
SNAP="${OUT}/snapshots"
mkdir -p "${SNAP}"

MISSING_TXT="${OUT}/missing_files.txt"
: > "${MISSING_TXT}"

while IFS= read -r f; do
  if [ -f "${f}" ]; then
    mkdir -p "${SNAP}/$(dirname "${f}")"
    cp -p "${f}" "${SNAP}/${f}"
  else
    echo "MISSING_FILE=${f}" >> "${MISSING_TXT}"
  fi
done < "${CLOSURE_LIST}"

echo "=== HASH SNAPSHOT TREE ==="
find "${OUT}" -type f -print0 \
| LC_ALL=C sort -z \
| xargs -0 shasum -a 256 \
> "${OUT}/closure_sha256.txt"

echo "=== BUILD ZIP (DETERMINISTIC INPUT ORDER VIA ZIP ITSELF) ==="
cd "${OUT_ROOT}" || exit 1
BASE="$(basename "${OUT}")"
ZIP="${PACK_ID}_${BASE}.zip"
rm -f "${ZIP}" "${ZIP}.sha256"
zip -r "${ZIP}" "${BASE}" >/dev/null
shasum -a 256 "${ZIP}" > "${ZIP}.sha256"
cd "${REPO_ROOT}" || exit 1

echo "=== GENERATE MANIFEST.json ==="
python3 - <<PY
import json, os, re, hashlib
repo_root = ${REPO_ROOT!r}
out = os.path.join(repo_root, ${OUT!r})
pack_id = ${PACK_ID!r}
ts = ${ts!r}

def read_text(p):
  try:
    with open(p, "r", encoding="utf-8", errors="replace") as f:
      return f.read()
  except FileNotFoundError:
    return ""

pytest_txt = read_text(os.path.join(out, "pytest.txt"))
pytest_rc_txt = read_text(os.path.join(out, "pytest_rc.txt")).strip()

tests_summary = {"rc": None, "raw_tail": None}
m = re.search(r"^(\\d+) passed", pytest_txt, flags=re.M)
if m:
  tests_summary["passed"] = int(m.group(1))
else:
  tests_summary["passed"] = None

tests_summary["rc"] = int(pytest_rc_txt.split("=")[-1]) if "pytest_rc=" in pytest_rc_txt else None
tests_summary["raw_tail"] = "\\n".join(pytest_txt.strip().splitlines()[-20:]) if pytest_txt.strip() else ""

hashes = []
sha_path = os.path.join(out, "closure_sha256.txt")
if os.path.exists(sha_path):
  with open(sha_path, "r", encoding="utf-8") as f:
    for line in f:
      line=line.strip()
      if not line:
        continue
      parts=line.split()
      if len(parts) >= 2:
        h=parts[0]
        fp=" ".join(parts[1:]).strip()
        hashes.append({"sha256": h, "path": fp})

zip_name = f"{pack_id}_{os.path.basename(out)}.zip"
zip_path = os.path.join(repo_root, "evidence_output", pack_id, zip_name)
zip_sha = ""
if os.path.exists(zip_path):
  with open(zip_path, "rb") as f:
    zip_sha = hashlib.sha256(f.read()).hexdigest()

manifest = {
  "pack_id": pack_id,
  "phase": "PH13",
  "name": "Operational Governance Hardening Closure Pack",
  "status": "PASS" if tests_summary.get("rc", 1) == 0 else "FAIL",
  "timestamp_utc": ts,
  "repo_root": repo_root,
  "out_dir": out,
  "git": {
    "head": read_text(os.path.join(out, "git_head.txt")).strip(),
    "status": read_text(os.path.join(out, "git_status.txt")).strip()
  },
  "tests": tests_summary,
  "artifacts": {
    "closure_sha256_txt": "closure_sha256.txt",
    "pytest_log": "pytest.txt",
    "zip": os.path.join("..", zip_name),
    "zip_sha256": zip_sha
  },
  "hashes": hashes
}

with open(os.path.join(out, "MANIFEST.json"), "w", encoding="utf-8") as f:
  json.dump(manifest, f, indent=2, sort_keys=True)
  f.write("\\n")
PY

echo "=== FINAL HASH TREE (INCLUDES MANIFEST.json) ==="
find "${OUT}" -type f -print0 \
| LC_ALL=C sort -z \
| xargs -0 shasum -a 256 \
> "${OUT}/closure_sha256_final.txt"

echo "=== SUMMARY ==="
echo "OUT=${OUT}"
echo "ZIP=${OUT_ROOT}/${PACK_ID}_${ts}.zip"
echo "ZIP_SHA256=${OUT_ROOT}/${PACK_ID}_${ts}.zip.sha256"
echo "MANIFEST=${OUT}/MANIFEST.json"
echo "STATUS=$(python3 - <<'PY'
import json
p="'"${OUT}"'/MANIFEST.json"
m=json.load(open(p,"r",encoding="utf-8"))
print(m.get("status"))
PY
)"
