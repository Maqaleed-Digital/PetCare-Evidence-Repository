#!/usr/bin/env bash
set -euo pipefail

# Resolve production ZIP SHA256 from a GitHub Release event payload deterministically (no guessing).
# Preference order:
#  1) Exactly one asset matching *.zip.sha256  -> download and parse first token as sha
#  2) Else exactly one asset matching *.zip    -> download and compute sha256
# Otherwise: fail and list candidates.

EVENT_JSON="${1:-}"
OUT_SHA_FILE="${2:-}"

if [ -z "${EVENT_JSON}" ] || [ ! -f "${EVENT_JSON}" ]; then
  echo "ERROR: missing/invalid arg1 EVENT_JSON (GitHub event payload path)" >&2
  echo "USAGE: petcare_release_asset_sha_resolve.sh <GITHUB_EVENT_JSON_PATH> [OUT_SHA_FILE]" >&2
  exit 2
fi

# GitHub Actions provides this; required for private asset downloads.
GITHUB_TOKEN="${GITHUB_TOKEN:-}"
if [ -z "${GITHUB_TOKEN}" ]; then
  echo "ERROR: GITHUB_TOKEN is required for release asset download" >&2
  exit 3
fi

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "${WORK_DIR}"' EXIT

# Extract assets (name + browser_download_url) from event JSON.
python3 - <<'PY' "${EVENT_JSON}" "${WORK_DIR}/assets.tsv"
import json, sys
p=sys.argv[1]
out=sys.argv[2]
j=json.load(open(p,"r",encoding="utf-8"))

rel = j.get("release") or {}
assets = rel.get("assets") or []
rows=[]
for a in assets:
    name=a.get("name")
    url=a.get("browser_download_url")
    if isinstance(name,str) and name and isinstance(url,str) and url:
        rows.append((name,url))

rows.sort(key=lambda x: x[0])
with open(out,"w",encoding="utf-8",newline="\n") as f:
    for name,url in rows:
        f.write(name + "\t" + url + "\n")

print("ASSETS_COUNT=" + str(len(rows)))
PY

ASSETS_TSV="${WORK_DIR}/assets.tsv"
if [ ! -s "${ASSETS_TSV}" ]; then
  echo "ERROR: no release assets found in event payload" >&2
  exit 4
fi

# Build candidate lists deterministically (sorted by name because TSV sorted).
ZIP_SHA_CAND="${WORK_DIR}/zip_sha_candidates.tsv"
ZIP_CAND="${WORK_DIR}/zip_candidates.tsv"
: > "${ZIP_SHA_CAND}"
: > "${ZIP_CAND}"

while IFS=$'\t' read -r name url; do
  case "${name}" in
    *.zip.sha256) printf "%s\t%s\n" "${name}" "${url}" >> "${ZIP_SHA_CAND}" ;;
    *.zip)        printf "%s\t%s\n" "${name}" "${url}" >> "${ZIP_CAND}" ;;
    *) : ;;
  esac
done < "${ASSETS_TSV}"

count_sha="$(wc -l < "${ZIP_SHA_CAND}" | tr -d '[:space:]')"
count_zip="$(wc -l < "${ZIP_CAND}" | tr -d '[:space:]')"

echo "CANDIDATES_zip_sha256=${count_sha}"
echo "CANDIDATES_zip=${count_zip}"

choose_kind=""
choose_name=""
choose_url=""

if [ "${count_sha}" = "1" ]; then
  choose_kind="zip.sha256"
  choose_name="$(awk -F'\t' '{print $1}' < "${ZIP_SHA_CAND}")"
  choose_url="$(awk -F'\t' '{print $2}' < "${ZIP_SHA_CAND}")"
elif [ "${count_sha}" = "0" ] && [ "${count_zip}" = "1" ]; then
  choose_kind="zip"
  choose_name="$(awk -F'\t' '{print $1}' < "${ZIP_CAND}")"
  choose_url="$(awk -F'\t' '{print $2}' < "${ZIP_CAND}")"
else
  echo "ERROR: ambiguous or missing release assets; refusing to guess." >&2
  echo "--- ALL_ASSETS (sorted by name) ---" >&2
  cat "${ASSETS_TSV}" >&2
  echo "--- ZIP_SHA256_CANDIDATES ---" >&2
  cat "${ZIP_SHA_CAND}" >&2 || true
  echo "--- ZIP_CANDIDATES ---" >&2
  cat "${ZIP_CAND}" >&2 || true
  exit 5
fi

echo "SELECTED_kind=${choose_kind}"
echo "SELECTED_name=${choose_name}"

DL_PATH="${WORK_DIR}/${choose_name}"

echo "=== DOWNLOAD (AUTH) ==="
# Use browser_download_url with Authorization for private repos.
curl -fsSL -L \
  -H "Authorization: Bearer ${GITHUB_TOKEN}" \
  -H "Accept: application/octet-stream" \
  "${choose_url}" \
  -o "${DL_PATH}"

if [ ! -s "${DL_PATH}" ]; then
  echo "ERROR: downloaded asset is empty: ${DL_PATH}" >&2
  exit 6
fi

RESOLVED_SHA=""
if [ "${choose_kind}" = "zip.sha256" ]; then
  # Take first token as sha.
  RESOLVED_SHA="$(awk '{print $1}' < "${DL_PATH}" | head -n 1 | tr -d '[:space:]')"
else
  RESOLVED_SHA="$(shasum -a 256 "${DL_PATH}" | awk '{print $1}')"
fi

if [ -z "${RESOLVED_SHA}" ]; then
  echo "ERROR: failed to resolve sha256" >&2
  exit 7
fi

echo "RESOLVED_prod_zip_sha256=${RESOLVED_SHA}"

if [ -n "${OUT_SHA_FILE}" ]; then
  mkdir -p "$(dirname "${OUT_SHA_FILE}")"
  printf "%s\n" "${RESOLVED_SHA}" > "${OUT_SHA_FILE}"
  echo "WROTE_sha_file=${OUT_SHA_FILE}"
fi

# Print sha on stdout as the final line for easy capture
printf "%s\n" "${RESOLVED_SHA}"
