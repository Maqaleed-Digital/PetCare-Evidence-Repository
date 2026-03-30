set -euo pipefail

PACK="PETCARE-PH10.1-CLOSURE"
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
echo "PetCare PH10.1 CLOSURE PACK"
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

echo "=== SNAPSHOT (PH10.1-RELEVANT FILES) ==="
REQ_FILES="
FND/CODE_SCAFFOLD/app.py
FND/security/policy_guard.py
FND/security/actor_id.py
TESTS/test_ph10_1_runtime_enforcement.py
ops/ph10_1_gate_registry.json
scripts/petcare_ph10_1_enforce_gates.py
scripts/petcare_ph10_1_closure_pack.sh
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

echo "=== RUN UNITTEST ==="
python3 -m unittest -q 2>&1 | tee "${OUT}/ops/unittest.txt"

echo "=== ENFORCE GATES ==="
python3 "scripts/petcare_ph10_1_enforce_gates.py" "ops/ph10_1_gate_registry.json" 2>&1 | tee "${OUT}/ops/gate_enforce.txt"

echo "=== CREATE MANIFEST.json (DETERMINISTIC) ==="
OUT="${OUT}" PACK="${PACK}" python3 - <<'PY'
import hashlib, json, os
out = os.environ["OUT"]
pack = os.environ.get("PACK", "PETCARE-PH10.1-CLOSURE")
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
    "pack_id": pack,
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

grep -q '"ok": true' "${OUT}/ops/gate_enforce.txt" || { echo "FAIL: gate enforcement did not pass"; exit 3; }

echo "PASS: ${PACK} ${TS}"
