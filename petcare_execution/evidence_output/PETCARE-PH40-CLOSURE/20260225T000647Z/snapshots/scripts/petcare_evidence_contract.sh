#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== EVIDENCE CONTRACT (PH39) ==="
echo "repo=${REPO}"

# Contract scope: PH31 evidence publication outputs
PACK="PETCARE-PH31-CLOSURE"
OUT_ROOT="${REPO}/evidence_output/${PACK}"

if [ ! -d "${OUT_ROOT}" ]; then
  echo "FAIL: evidence root missing: ${OUT_ROOT}"
  echo "HINT: run scripts/petcare_ph31_closure_pack.sh first"
  exit 10
fi

ZIP="$(ls -1t "${OUT_ROOT}/${PACK}_"*.zip 2>/dev/null | head -n 1 || true)"
SHA="${ZIP}.sha256"

if [ -z "${ZIP}" ] || [ ! -f "${ZIP}" ]; then
  echo "FAIL: no PH31 ZIP found in ${OUT_ROOT}"
  exit 11
fi
if [ ! -f "${SHA}" ]; then
  echo "FAIL: missing ZIP sha file: ${SHA}"
  exit 12
fi

echo "zip=${ZIP}"
echo "sha=${SHA}"

echo ""
echo "=== ZIP SHA VERIFY ==="
( cd "${OUT_ROOT}" && shasum -a 256 -c "$(basename "${SHA}")" )
echo "ZIP_SHA_VERIFY=PASS"

# Derive newest OUT_DIR by parsing ZIP basename: PETCARE-PH31-CLOSURE_<TS>.zip
BASE="$(basename "${ZIP}")"
TS_DIR="${BASE#${PACK}_}"
TS_DIR="${TS_DIR%.zip}"
OUT_DIR="${OUT_ROOT}/${TS_DIR}"

if [ ! -d "${OUT_DIR}" ]; then
  echo "FAIL: derived out dir missing: ${OUT_DIR}"
  exit 13
fi

MANIFEST="${OUT_DIR}/MANIFEST.json"
if [ ! -f "${MANIFEST}" ]; then
  echo "FAIL: MANIFEST.json missing: ${MANIFEST}"
  exit 14
fi
if [ ! -s "${MANIFEST}" ]; then
  echo "FAIL: MANIFEST.json empty: ${MANIFEST}"
  exit 15
fi

echo ""
echo "=== MANIFEST CHECKS ==="
echo "out_dir=${OUT_DIR}"
echo "manifest=${MANIFEST}"

# Validate JSON + enforce snapshot files exist for each manifest entry
"${REPO}/.venv/bin/python" - <<'PY'
import json, os, sys

repo = os.getcwd()
# script runs from repo root (enforced by caller), but be explicit:
repo = os.path.abspath(repo)

# Recompute OUT_DIR and MANIFEST from environment-like derivation done in bash:
pack = "PETCARE-PH31-CLOSURE"
out_root = os.path.join(repo, "evidence_output", pack)

# Find newest zip
zips = []
for name in os.listdir(out_root):
    if name.startswith(pack + "_") and name.endswith(".zip"):
        zips.append(name)
zips.sort(reverse=True)
if not zips:
    print("FAIL: no zip found")
    sys.exit(20)

zip_name = zips[0]
ts_dir = zip_name[len(pack)+1:-4]
out_dir = os.path.join(out_root, ts_dir)
manifest_path = os.path.join(out_dir, "MANIFEST.json")

try:
    m = json.load(open(manifest_path, "r", encoding="utf-8"))
except Exception as e:
    print("FAIL: MANIFEST.json invalid JSON")
    print("ERROR=%s" % e)
    sys.exit(21)

files = m.get("files", [])
if not isinstance(files, list) or len(files) == 0:
    print("FAIL: manifest files[] missing or empty")
    sys.exit(22)

bad = 0
for ent in files:
    p = ent.get("path")
    h = ent.get("sha256")
    if not p or not isinstance(p, str):
        print("FAIL: manifest entry missing path")
        bad += 1
        continue
    if not h or not isinstance(h, str) or len(h) < 10:
        print("FAIL: manifest entry missing sha256 for path=%s" % p)
        bad += 1
        continue

    abs_p = os.path.join(out_dir, p)
    if not os.path.isfile(abs_p):
        print("FAIL: missing manifest referenced file: %s" % p)
        bad += 1

print("MANIFEST_FILES=%d" % len(files))
print("MANIFEST_REFERENCES=PASS" if bad == 0 else "MANIFEST_REFERENCES=FAIL")
sys.exit(0 if bad == 0 else 23)
PY

echo ""
echo "RESULT=PASS"
exit 0
