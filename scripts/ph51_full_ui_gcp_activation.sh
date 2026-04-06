#!/usr/bin/env bash
set -euo pipefail

: "${REPO_ROOT:?Missing REPO_ROOT}"
: "${SCRIPT_ROOT:?Missing SCRIPT_ROOT}"
: "${WEB_ROOT:?Missing WEB_ROOT}"
: "${EVIDENCE_DIR:?Missing EVIDENCE_DIR}"
: "${DOMAIN_NAME:?Missing DOMAIN_NAME}"

mkdir -p "$EVIDENCE_DIR"

"$SCRIPT_ROOT/validate_ui_contract.sh" > "$EVIDENCE_DIR/01_contract_validation.log" 2>&1

SERVICE_URL="$("$SCRIPT_ROOT/deploy_ui_gcp.sh" 2> "$EVIDENCE_DIR/02_deploy.stderr.log" | tee "$EVIDENCE_DIR/02_deploy.stdout.log" | tail -n 1)"
export SERVICE_URL

"$SCRIPT_ROOT/verify_web_gates.sh" > "$EVIDENCE_DIR/03_verify_gates.log" 2>&1

"$SCRIPT_ROOT/domain_go_live.sh" > "$EVIDENCE_DIR/04_domain_go_live.log" 2>&1

printf "PH5.1 FULL UI BUILD + GCP WEB ACTIVATION\n" > "$EVIDENCE_DIR/decision_log.txt"
printf "DOMAIN=%s\n" "$DOMAIN_NAME" >> "$EVIDENCE_DIR/decision_log.txt"
printf "SERVICE_URL=%s\n" "$SERVICE_URL" >> "$EVIDENCE_DIR/decision_log.txt"

find "$REPO_ROOT/petcare_web" -type f | sort > "$EVIDENCE_DIR/file_listing.txt"

python3 - << 'PY'
import hashlib, json, os, pathlib
repo_root = pathlib.Path(os.environ["REPO_ROOT"])
evidence_dir = pathlib.Path(os.environ["EVIDENCE_DIR"])
web_root = repo_root / "petcare_web"
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()
files = []
for path in sorted(web_root.rglob("*")):
    if path.is_file():
        files.append({
            "path": str(path.relative_to(repo_root)),
            "sha256": sha256(path)
        })
manifest = {
    "phase": "PH5.1",
    "status": "full_ui_built_deployed_and_domain_gated",
    "service_url": os.environ["SERVICE_URL"],
    "files": files
}
print(json.dumps(manifest, indent=2))
PY > "$EVIDENCE_DIR/MANIFEST.json"

cd "$REPO_ROOT"
git add "petcare_web" "scripts" "petcare_execution"
git commit -m "PH5.1 — Full UI build + GCP web activation (governed, fail-closed, domain-gated)"
git push origin main

printf "NEW_SOURCE_OF_TRUTH_COMMIT=%s\n" "$(git rev-parse HEAD)"
printf "EVIDENCE_RUN_DIR=%s\n" "$EVIDENCE_DIR"
printf "SERVICE_URL=%s\n" "$SERVICE_URL"
