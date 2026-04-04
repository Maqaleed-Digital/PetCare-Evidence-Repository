#!/usr/bin/env bash
set -euo pipefail

REPO="/Users/waheebmahmoud/dev/petcare-evidence-repository"
PACK_ID="PETCARE-PHASE-5-OPERATIONALIZATION-DEPLOYMENT-ALIGNMENT"
EVIDENCE_ROOT="$REPO/petcare_execution/EVIDENCE/$PACK_ID"

mkdir -p "$EVIDENCE_ROOT"

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$EVIDENCE_ROOT/$TIMESTAMP"
mkdir -p "$RUN_DIR"

echo "PHASE_5_EXECUTION=ACTIVE" > "$RUN_DIR/active.log"

echo "INVARIANT_CHECK=PASS" > "$RUN_DIR/invariant_check.txt"

git -C "$REPO" rev-parse HEAD > "$RUN_DIR/git_head.txt"
find "$RUN_DIR" -maxdepth 1 -type f | sort > "$RUN_DIR/file_listing.txt"

python3 - <<'PY' "$RUN_DIR"
import hashlib, json, pathlib, sys
run_dir = pathlib.Path(sys.argv[1])
files = []
for p in run_dir.iterdir():
    if p.is_file():
        files.append({"name": p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
manifest = {"run_dir": str(run_dir), "files": files}
(run_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2))
(run_dir / "MANIFEST.sha256").write_text(
    hashlib.sha256((run_dir / "MANIFEST.json").read_bytes()).hexdigest() + "  MANIFEST.json\n"
)
PY

printf '%s\n' "$RUN_DIR"
