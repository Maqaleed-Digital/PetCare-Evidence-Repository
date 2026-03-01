#!/usr/bin/env bash
set -euo pipefail

# repo_root/petcare_execution/scripts/this_file.sh -> repo root is ../..
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"
cd "${REPO_ROOT}" || exit 1

PROD_ZIP_SHA256="${1:-}"
INDEX_ARG="${2:-petcare_execution/FND/VERIFICATION_INDEX.json}"

if [ -z "${PROD_ZIP_SHA256}" ]; then
  echo "ERROR: missing arg1 PROD_ZIP_SHA256"
  echo "USAGE: petcare_execution/scripts/petcare_verification_policy_check_sha.sh <PROD_ZIP_SHA256> [INDEX_JSON]"
  exit 2
fi

# Resolve index path absolute
if [[ "${INDEX_ARG}" = /* ]]; then
  INDEX_PATH="${INDEX_ARG}"
else
  INDEX_PATH="${REPO_ROOT}/${INDEX_ARG}"
fi

# Normalize
INDEX_PATH="$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "${INDEX_PATH}")"

if [ ! -f "${INDEX_PATH}" ]; then
  echo "ERROR: index not found: ${INDEX_PATH}"
  exit 3
fi

# NOTE: argv MUST be before the heredoc redirection
python3 - "${INDEX_PATH}" "${PROD_ZIP_SHA256}" <<'PY'
import json, sys
idx_path=sys.argv[1]
want=sys.argv[2]

idx=json.load(open(idx_path,"r",encoding="utf-8"))
entries=idx.get("entries") or []

hits=[]
for e in entries:
    if e.get("verified_zip_sha256") != want:
        continue
    op=e.get("overall_pass")
    if op is True or (isinstance(op,str) and op.strip().lower()=="true"):
        hits.append(e)

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
