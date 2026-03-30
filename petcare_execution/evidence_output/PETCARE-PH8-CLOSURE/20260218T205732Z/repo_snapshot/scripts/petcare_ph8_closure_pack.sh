set -euo pipefail

PACK="PETCARE-PH8-CLOSURE"
ROOT="$(pwd)"
TS="$(python3 - <<'PY'
from datetime import datetime, timezone
print(datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
PY
)"

OUT_ROOT="${ROOT}/evidence_output/${PACK}"
OUT="${OUT_ROOT}/${TS}"
ZIP="${OUT_ROOT}/${PACK}_${TS}.zip"

mkdir -p "${OUT}/repo_snapshot" "${OUT}/ops"

echo "=============================================="
echo "PetCare PH8 CLOSURE PACK"
echo "pack=${PACK}"
echo "timestamp_utc=${TS}"
echo "repo_root=${ROOT}"
echo "out=${OUT}"
echo "zip=${ZIP}"
echo "=============================================="

echo "=== REPO CONTEXT ==="
{
  echo "pwd=${ROOT}"
  git status -sb || true
  git log -1 --oneline || true
} > "${OUT}/ops/repo_context.txt"

echo "=== SNAPSHOT (PH8-RELEVANT FILES) ==="
REQ_FILES="
FND/security/actor_id.py
FND/security/auth_stub.py
FND/audit/immutable_audit.py
FND/CODE_SCAFFOLD/storage/sqlite_lifecycle.py
TESTS/test_ph8_security_and_audit.py
scripts/petcare_ph8_closure_pack.sh
"

MISSING=0
for f in ${REQ_FILES}; do
  if [ -f "${ROOT}/${f}" ]; then
    mkdir -p "${OUT}/repo_snapshot/$(dirname "${f}")"
    cp -p "${ROOT}/${f}" "${OUT}/repo_snapshot/${f}"
  else
    echo "MISSING_FILE=${f}" | tee -a "${OUT}/ops/missing_files.txt"
    MISSING=1
  fi
done

echo "=== RUN UNITTEST (STOP CONDITION PREREQ) ==="
python3 -m unittest -q 2>&1 | tee "${OUT}/ops/unittest.txt"

echo "=== CREATE MANIFEST.json (DETERMINISTIC) ==="
python3 - <<'PY'
import hashlib, json, os
out = os.environ["OUT"]
records = []
for root, dirs, files in os.walk(out):
    dirs.sort()
    files.sort()
    for fn in files:
        path = os.path.join(root, fn)
        rel = os.path.relpath(path, out).replace("\\","/")
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024*1024), b""):
                h.update(chunk)
        records.append({"path": rel, "sha256": h.hexdigest()})
manifest = {
    "pack_id": "PETCARE-PH8-CLOSURE",
    "generated_utc": os.path.basename(out),
    "file_count": len(records),
    "files": records,
}
p = os.path.join(out, "MANIFEST.json")
with open(p, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
print(p)
PY

echo "=== ZIP + SHA256 ==="
rm -f "${ZIP}" "${ZIP}.sha256"
cd "${OUT_ROOT}" || exit 1
zip -rq "${ZIP}" "${TS}"
shasum -a 256 "${ZIP}" | tee "${ZIP}.sha256"

echo "=== STOP CONDITION CHECK ==="
[ -f "${OUT}/MANIFEST.json" ] || { echo "FAIL: missing MANIFEST.json"; exit 2; }
[ -f "${ZIP}" ] || { echo "FAIL: missing zip"; exit 2; }
[ -f "${ZIP}.sha256" ] || { echo "FAIL: missing zip sha256"; exit 2; }
if [ "${MISSING}" -ne 0 ]; then
  echo "FAIL: missing required files (see ops/missing_files.txt)"
  exit 2
fi

echo "PASS: ${PACK} ${TS}"
