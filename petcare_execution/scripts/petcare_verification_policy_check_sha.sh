#!/usr/bin/env bash
set -euo pipefail

# === PATH NORMALIZATION (repo-root anchored) ===
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"
INDEX_ARG="${2:-}"
if [ -z "${INDEX_ARG}" ]; then
  echo "ERROR: index path arg missing"
  exit 3
fi
# If caller provided relative path, resolve it against repo root
case "${INDEX_ARG}" in
  /*) INDEX_PATH="${INDEX_ARG}" ;;
  *)  INDEX_PATH="${REPO_ROOT}/${INDEX_ARG}" ;;
esac
# Normalize any /./ or /../ segments (python is guaranteed)
INDEX_PATH="$(python3 - <<PY
import os,sys
print(os.path.realpath(sys.argv[1]))
PY
"${INDEX_PATH}")"
# === END PATH NORMALIZATION ===


REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}" || exit 1

PROD_ZIP_SHA256="${1:-}"
INDEX="${2:-FND/VERIFICATION_INDEX.json}"

if [ -z "${PROD_ZIP_SHA256}" ]; then
  echo "ERROR: missing arg1 PROD_ZIP_SHA256"
  echo "USAGE: scripts/petcare_verification_policy_check_sha.sh <PROD_ZIP_SHA256> [INDEX_JSON]"
  exit 2
fi

if [ ! -f "${INDEX}" ]; then
  echo "ERROR: index not found: ${INDEX}"
  exit 3
fi

python3 - <<'PY' "${INDEX}" "${PROD_ZIP_SHA256}"
import json, sys
idx_path=sys.argv[1]
want=sys.argv[2]
idx=json.load(open(idx_path,"r",encoding="utf-8"))
entries=idx.get("entries") or []
hits=[e for e in entries if e.get("verified_zip_sha256")==want and e.get("overall_pass")=="true"]
if not hits:
    print("POLICY_FAIL")
    print("verified_zip_sha256=" + want)
    raise SystemExit(10)
e=hits[-1]
print("POLICY_PASS")
print("verified_zip_sha256=" + want)
print("entry_hash=" + (e.get("entry_hash") or ""))
print("verifier_pack=" + (e.get("verifier_pack") or ""))
print("verifier_zip_sha256=" + (e.get("verifier_zip_sha256") or ""))
PY
