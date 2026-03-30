#!/usr/bin/env bash
set -euo pipefail

PACK="PETCARE-PH12-CLOSURE"
TS="$(python3 - <<'PY'
from datetime import datetime, timezone
print(datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
PY
)"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_ROOT="${REPO_ROOT}/evidence_output/${PACK}"
OUT="${OUT_ROOT}/${TS}"
ZIP="${OUT_ROOT}/${PACK}_${TS}.zip"

echo "=============================================="
echo "PetCare PH12 CLOSURE PACK"
echo "pack=${PACK}"
echo "timestamp_utc=${TS}"
echo "repo_root=${REPO_ROOT}"
echo "out=${OUT}"
echo "zip=${ZIP}"
echo "=============================================="

cd "${REPO_ROOT}" || exit 1
mkdir -p "${OUT}/repo_snapshot"

echo "=== REPO CONTEXT ===" | tee "${OUT}/00_context.txt"
pwd | tee -a "${OUT}/00_context.txt"
echo "" | tee -a "${OUT}/00_context.txt"
git status -sb | tee -a "${OUT}/00_context.txt" || true
echo "" | tee -a "${OUT}/00_context.txt"
git log -1 --oneline | tee -a "${OUT}/00_context.txt" || true

echo "=== SNAPSHOT (PH12-RELEVANT FILES) ==="
SNAP_LIST="${OUT}/snapshot_list.txt"
: > "${SNAP_LIST}"

find . -maxdepth 6 -type f \( \
  -path "./FND/security/*" -o \
  -path "./FND/CODE_SCAFFOLD/storage/export_bundle.py" -o \
  -path "./ops/ph12*" -o \
  -path "./TESTS/test_ph12*" -o \
  -path "./TESTS/test_tenant_isolation.py" -o \
  -path "./scripts/petcare_ph12_closure_pack.sh" \
\) | sed 's|^\./||' | LC_ALL=C sort > "${SNAP_LIST}"

mkdir -p "${OUT}/snapshots"
while IFS= read -r f; do
  if [ -f "${f}" ]; then
    mkdir -p "${OUT}/snapshots/$(dirname "${f}")"
    cp -p "${f}" "${OUT}/snapshots/${f}"
  fi
done < "${SNAP_LIST}"

echo "=== RUN UNITTEST ==="
python3 -m unittest -q | tee "${OUT}/unittest.txt"

echo "=== CREATE MANIFEST.json (DETERMINISTIC) ==="
OUT="${OUT}" \
PACK="${PACK}" \
TS="${TS}" \
REPO_ROOT="${REPO_ROOT}" \
python3 - <<'PY'
import hashlib, json, os
from datetime import datetime, timezone

out = os.environ["OUT"]
pack = os.environ["PACK"]
ts = os.environ["TS"]
repo_root = os.environ["REPO_ROOT"]

records = []
for root, dirs, files in os.walk(out):
    dirs.sort()
    files.sort()
    for fn in files:
        path = os.path.join(root, fn)
        rel = os.path.relpath(path, out).replace("\\","/")
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        records.append({"path": rel, "sha256": h.hexdigest()})

manifest = {
    "manifest_version": "1.0",
    "pack_id": pack,
    "generated_utc": ts,
    "repo_root": repo_root,
    "file_count": len(records),
    "files": records,
    "unittest_log": "unittest.txt",
    "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
}

p = os.path.join(out, "MANIFEST.json")
with open(p, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False, sort_keys=True)
print(p)
PY

echo "=== ZIP + SHA256 ==="
rm -f "${ZIP}" "${ZIP}.sha256"
(
  cd "${OUT_ROOT}" || exit 1
  zip -rq "${ZIP}" "${TS}"
)
shasum -a 256 "${ZIP}" | tee "${ZIP}.sha256"

echo "=== STOP CONDITION CHECK ==="
OUT_ROOT="${OUT_ROOT}" \
OUT="${OUT}" \
ZIP="${ZIP}" \
python3 - <<'PY'
import os
out_root = os.environ["OUT_ROOT"]
out = os.environ["OUT"]
zip_path = os.environ["ZIP"]

need = [
    os.path.join(out, "MANIFEST.json"),
    zip_path,
    zip_path + ".sha256"
]
missing = [p for p in need if not os.path.exists(p)]
if missing:
    raise SystemExit("FAIL missing: " + ", ".join(missing))
print("PASS stop condition")
PY

echo "PASS: ${PACK} ${TS}"
