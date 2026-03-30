#!/usr/bin/env bash
set -euo pipefail

# Creates a deterministic backup bundle of governance artifacts + optional data artifacts.
# No guessing: it will NOT assume a DB exists.
# If a DB path exists, it will include it; otherwise logs DB_SKIPPED.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TS_UTC="${TS_UTC:-$(date -u +%Y%m%dT%H%M%SZ)}"
OUT_DIR="${OUT_DIR:-${REPO_ROOT}/evidence_output/PETCARE-PH-L2-BACKUP/${TS_UTC}}"
RTO_MAX_SECONDS="${RTO_MAX_SECONDS:-900}"

mkdir -p "${OUT_DIR}/bundle" "${OUT_DIR}/logs"

echo "repo_root=${REPO_ROOT}" | tee "${OUT_DIR}/logs/context.log"
echo "ts_utc=${TS_UTC}" | tee -a "${OUT_DIR}/logs/context.log"
echo "out_dir=${OUT_DIR}" | tee -a "${OUT_DIR}/logs/context.log"
echo "rto_max_seconds=${RTO_MAX_SECONDS}" | tee -a "${OUT_DIR}/logs/context.log"

t0="$(date +%s)"

# Required governance artifacts (explicit list = deterministic)
req=(
  "FND/VERIFICATION_INDEX.json"
  "FND/VERIFICATION_INDEX.sha256"
  "FND/VERIFICATION_POLICY.json"
  "FND/VERIFICATION_POLICY.sha256"
  "POLICY.md"
  "POLICY.sha256"
  "REGISTRY.json"
  "REGISTRY.sha256"
  "requirements.lock"
)

missing=0
for f in "${req[@]}"; do
  if [ ! -f "${REPO_ROOT}/${f}" ]; then
    echo "MISSING_REQUIRED=${f}" | tee -a "${OUT_DIR}/logs/missing.log"
    missing=1
  fi
done
if [ "${missing}" -ne 0 ]; then
  echo "FATAL: required artifacts missing. Stop (no guessing)." | tee -a "${OUT_DIR}/logs/error.log"
  exit 3
fi

# Optional data artifacts: include only if they exist
opt=()
# Common candidates (keep conservative, deterministic list)
candidates=(
  "database.sqlite"
  "data/database.sqlite"
  "ops/db/database.sqlite"
)
for c in "${candidates[@]}"; do
  if [ -f "${REPO_ROOT}/${c}" ]; then
    opt+=("${c}")
  fi
done
if [ "${#opt[@]}" -eq 0 ]; then
  echo "DB_SKIPPED: no known DB file found (expected in current repo state)." | tee -a "${OUT_DIR}/logs/optional.log"
fi

# Copy required + optional into bundle/
copy_list=("${req[@]}" ${opt[@]+"${opt[@]}"})
for f in "${copy_list[@]}"; do
  mkdir -p "${OUT_DIR}/bundle/$(dirname "${f}")"
  cp -p "${REPO_ROOT}/${f}" "${OUT_DIR}/bundle/${f}"
done

# Deterministic manifest
python3 - <<PY
import json
from pathlib import Path

out=Path("${OUT_DIR}")
bundle=out/"bundle"
files=[str(p.relative_to(bundle)) for p in sorted(bundle.rglob("*")) if p.is_file()]
m={
  "ts_utc":"${TS_UTC}",
  "bundle_file_count":len(files),
  "bundle_files":files,
  "db_included": any(f.endswith("database.sqlite") for f in files)
}
(out/"MANIFEST.json").write_text(json.dumps(m, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
print("OK wrote MANIFEST.json")
PY

# Sorted sha list for bundle files
(
  cd "${OUT_DIR}/bundle" || exit 1
  find . -type f -print0 \
  | LC_ALL=C sort -z \
  | xargs -0 shasum -a 256 \
  > "${OUT_DIR}/bundle_sha256.txt"
)

# Zip backup bundle
ZIP="${OUT_DIR}.zip"
rm -f "${ZIP}" "${ZIP}.sha256"
(
  cd "$(dirname "${OUT_DIR}")" || exit 1
  zip -r "$(basename "${OUT_DIR}").zip" "$(basename "${OUT_DIR}")" >/dev/null
  shasum -a 256 "$(basename "${OUT_DIR}").zip" > "$(basename "${OUT_DIR}").zip.sha256"
)

t1="$(date +%s)"
dt="$((t1 - t0))"

echo "backup_duration_seconds=${dt}" | tee -a "${OUT_DIR}/logs/timing.log"
echo "backup_zip=${ZIP}" | tee -a "${OUT_DIR}/logs/timing.log"
echo "backup_zip_sha=${ZIP}.sha256" | tee -a "${OUT_DIR}/logs/timing.log"

# RTO is enforced by closure pack across backup+restore, not here.
echo "OK backup created"
