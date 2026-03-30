#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1

TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUTDIR="evidence_output/PETCARE-PH4-DISCOVERY/${TS}"
mkdir -p "$OUTDIR"

REPORT="${OUTDIR}/DISCOVERY_REPORT.md"
LOGS="${OUTDIR}/LOGS.txt"

: > "$REPORT"
: > "$LOGS"

emit() {
  printf "%s\n" "$*" | tee -a "$REPORT" >/dev/null
}

run() {
  printf "\n%s\n" "$*" | tee -a "$LOGS" >/dev/null
  bash -lc "$*" >>"$LOGS" 2>&1 || {
    printf "\nCOMMAND_FAILED: %s\n" "$*" | tee -a "$LOGS" >/dev/null
    return 1
  }
}

emit "# PETCARE PH4 DISCOVERY PACK"
emit ""
emit "- timestamp_utc: ${TS}"
emit "- root: ${ROOT}"
emit ""

emit "## Git"
run "git status -sb"
run "git log -1 --oneline"
emit ""
emit "\`\`\`"
sed -n '1,120p' "$LOGS" >> "$REPORT"
emit "\`\`\`"
: > "$LOGS"

emit "## Repo shape"
run "ls -la"
run "find scripts -maxdepth 2 -type f -print | sort"
run "find . -maxdepth 3 -type f \\( -name '*.py' -o -name '*.md' -o -name '*.json' \\) -print | wc -l | tr -d ' ' | awk '{print \"tracked_like_filecount=\"\$1}'"
emit ""
emit "\`\`\`"
sed -n '1,220p' "$LOGS" >> "$REPORT"
emit "\`\`\`"
: > "$LOGS"

emit "## Evidence outputs present"
run "ls -la evidence_output || true"
run "find evidence_output -maxdepth 3 \\( -type f -name '*.zip' -o -type f -name 'MANIFEST.json' -o -type f -name '*.md' \\) 2>/dev/null | sort | sed -n '1,260p' || true"
emit ""
emit "\`\`\`"
sed -n '1,320p' "$LOGS" >> "$REPORT"
emit "\`\`\`"
: > "$LOGS"

emit "## Phase-2 / Phase-3 / Export keywords scan"
run "grep -R --line-number --fixed-string 'PHASE-2' . 2>/dev/null | sed -n '1,240p' || true"
run "grep -R --line-number --fixed-string 'PHASE-3' . 2>/dev/null | sed -n '1,240p' || true"
run "grep -R --line-number --ignore-case -E 'evidence export|export bundle|deterministic export|exporter|MANIFEST.json|tenant isolation|tenant_id|x-tenant|uuid' . 2>/dev/null | sed -n '1,320p' || true"
emit ""
emit "\`\`\`"
sed -n '1,420p' "$LOGS" >> "$REPORT"
emit "\`\`\`"
: > "$LOGS"

emit "## Tests + smoke + land pack detection"
run "find . -maxdepth 3 -type f \\( -name '*smoke*.sh' -o -name '*land_pack*.sh' -o -name '*unittest*.sh' -o -name 'petcare_*pack*.sh' \\) 2>/dev/null | sort || true"
emit ""
emit "\`\`\`"
sed -n '1,200p' "$LOGS" >> "$REPORT"
emit "\`\`\`"
: > "$LOGS"

emit "## Run validations (best-effort, no guessing)"
if [ -f "scripts/petcare_unittest.sh" ]; then
  run "bash scripts/petcare_unittest.sh"
elif [ -f "scripts/unittest.sh" ]; then
  run "bash scripts/unittest.sh"
else
  run "python3 -m unittest -q || true"
fi

if [ -f "scripts/petcare_smoke.sh" ]; then
  run "bash scripts/petcare_smoke.sh"
elif [ -f "scripts/smoke.sh" ]; then
  run "bash scripts/smoke.sh"
else
  run "echo 'SMOKE_SCRIPT_NOT_FOUND'"
fi

if [ -f "scripts/petcare_land_pack.sh" ]; then
  run "bash scripts/petcare_land_pack.sh"
else
  run "echo 'LAND_PACK_SCRIPT_NOT_FOUND'"
fi

emit ""
emit "\`\`\`"
sed -n '1,520p' "$LOGS" >> "$REPORT"
emit "\`\`\`"
: > "$LOGS"

emit "## Manifest generation (python3/python preferred, shasum fallback)"
PYBIN=""
if command -v python3 >/dev/null 2>&1; then
  PYBIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYBIN="python"
fi

if [ -n "$PYBIN" ]; then
  "$PYBIN" - <<PY
import hashlib, json, pathlib
root = pathlib.Path("${OUTDIR}")
items = []
for p in sorted(root.rglob("*")):
    if p.is_file():
        b = p.read_bytes()
        h = hashlib.sha256(b).hexdigest()
        items.append({"path": str(p.relative_to(root)), "sha256": h, "bytes": len(b)})
manifest = {
    "pack_id": "PETCARE-PH4-DISCOVERY",
    "timestamp_utc": "${TS}",
    "root": str(root),
    "artifacts": items
}
(root / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
print("manifest_written", root / "MANIFEST.json")
PY
else
  MF="${OUTDIR}/MANIFEST.json"
  {
    printf "{\n"
    printf "  \"pack_id\": \"PETCARE-PH4-DISCOVERY\",\n"
    printf "  \"timestamp_utc\": \"%s\",\n" "$TS"
    printf "  \"root\": \"%s\",\n" "$OUTDIR"
    printf "  \"artifacts\": [\n"
    first=1
    while IFS= read -r -d '' f; do
      rel="${f#${OUTDIR}/}"
      sha="$(shasum -a 256 "$f" | awk '{print $1}')"
      bytes="$(wc -c < "$f" | tr -d ' ')"
      if [ "$first" -eq 0 ]; then
        printf ",\n"
      fi
      first=0
      printf "    {\"path\": \"%s\", \"sha256\": \"%s\", \"bytes\": %s}" "$rel" "$sha" "$bytes"
    done < <(find "$OUTDIR" -type f -print0 | LC_ALL=C sort -z)
    printf "\n  ]\n"
    printf "}\n"
  } > "$MF"
  echo "manifest_written $MF" >> "${OUTDIR}/LOGS_manifest.txt"
fi

emit ""
emit "## ZIP + SHA256"
ZIPBASE="evidence_output/PETCARE-PH4-DISCOVERY/PETCARE-PH4-DISCOVERY_${TS}"
( cd "evidence_output/PETCARE-PH4-DISCOVERY" && zip -r "$(basename "$ZIPBASE").zip" "${TS}" >/dev/null )
shasum -a 256 "${ZIPBASE}.zip" | awk '{print $1 "  " FILENAME}' FILENAME="$(basename "${ZIPBASE}.zip")" > "${ZIPBASE}.zip.sha256"

emit ""
emit "- ZIP: ${ZIPBASE}.zip"
emit "- SHA256_FILE: ${ZIPBASE}.zip.sha256"
emit "- REPORT: ${REPORT}"
emit "- MANIFEST: ${OUTDIR}/MANIFEST.json"
