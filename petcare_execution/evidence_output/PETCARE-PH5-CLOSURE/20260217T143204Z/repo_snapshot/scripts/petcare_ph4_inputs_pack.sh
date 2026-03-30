#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1

TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUTDIR="evidence_output/PETCARE-PH4-INPUTS/${TS}"
SNAP="${OUTDIR}/snapshots"
mkdir -p "$SNAP"

REPORT="${OUTDIR}/PH4_INPUTS_REPORT.md"
: > "$REPORT"

emit() { printf "%s\n" "$*" | tee -a "$REPORT" >/dev/null; }

copy_if_exists() {
  local p="$1"
  if [ -f "$p" ]; then
    mkdir -p "$(dirname "${SNAP}/${p}")"
    cp -p "$p" "${SNAP}/${p}"
    emit "- INCLUDED: ${p}"
  else
    emit "- MISSING: ${p}"
  fi
}

emit "# PETCARE PH4 INPUTS PACK"
emit ""
emit "- timestamp_utc: ${TS}"
emit "- root: ${ROOT}"
emit ""

emit "## Git status"
emit "\`\`\`"
git status -sb || true
emit "\`\`\`"
emit ""

emit "## Untracked (porcelain)"
emit "\`\`\`"
git status --porcelain=v1 -uall | sed -n '1,220p' || true
emit "\`\`\`"
emit ""

emit "## Target files snapshot"
emit ""

copy_if_exists "requirements.txt"

copy_if_exists "scripts/run_api.sh"
copy_if_exists "scripts/petcare_land_pack.sh"
copy_if_exists "scripts/_manifest_gen.py"

copy_if_exists "FND/CODE_SCAFFOLD/app.py"
copy_if_exists "FND/CODE_SCAFFOLD/tenant_isolation_guard.py"

copy_if_exists "FND/CODE_SCAFFOLD/storage/__init__.py"
copy_if_exists "FND/CODE_SCAFFOLD/storage/memory_store.py"
copy_if_exists "FND/CODE_SCAFFOLD/storage/export_bundle.py"

copy_if_exists "FND/CODE_SCAFFOLD/interfaces/storage_interface.py"

copy_if_exists "TESTS/test_tenant_isolation.py"

emit ""
emit "## File list (snapshots)"
emit "\`\`\`"
find "$SNAP" -type f -print | sed "s#^${SNAP}/##" | LC_ALL=C sort
emit "\`\`\`"
emit ""

emit "## Full contents (snapshotted) — concatenated"
BODIES="${OUTDIR}/SNAPSHOT_BODIES.txt"
: > "$BODIES"
for f in $(find "$SNAP" -type f -print | sed "s#^${SNAP}/##" | LC_ALL=C sort); do
  printf "\n===== FILE: %s =====\n" "$f" >> "$BODIES"
  cat "${SNAP}/${f}" >> "$BODIES"
  printf "\n" >> "$BODIES"
done
emit "- SNAPSHOT_BODIES: ${OUTDIR}/SNAPSHOT_BODIES.txt"
emit ""

emit "## Manifest + ZIP + SHA256"
python3 "scripts/_manifest_gen.py" "$OUTDIR" "PETCARE-PH4-INPUTS" >/dev/null

ZIPBASE="evidence_output/PETCARE-PH4-INPUTS/PETCARE-PH4-INPUTS_${TS}"
( cd "evidence_output/PETCARE-PH4-INPUTS" && zip -r "$(basename "$ZIPBASE").zip" "${TS}" >/dev/null )
shasum -a 256 "${ZIPBASE}.zip" | awk '{print $1 "  " FILENAME}' FILENAME="$(basename "${ZIPBASE}.zip")" > "${ZIPBASE}.zip.sha256"

emit "- ZIP: ${ZIPBASE}.zip"
emit "- SHA256_FILE: ${ZIPBASE}.zip.sha256"
emit "- MANIFEST: ${OUTDIR}/MANIFEST.json"
