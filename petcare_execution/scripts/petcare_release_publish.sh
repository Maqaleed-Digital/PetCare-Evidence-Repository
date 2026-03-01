#!/usr/bin/env bash
set -euo pipefail

# Deterministic GitHub Release publisher for PetCare evidence closure zips.
# No guessing:
# - requires TAG (local tag must exist)
# - requires ZIP path exists
# - requires ZIP.sha256 exists and matches computed SHA256 (sidecar enforcement)
#
# NOTE: This script may run from a pre-push hook before the tag exists remotely.
# Therefore we DO NOT use gh release create --verify-tag (it would fail deterministically).
# Instead we:
#   - verify tag exists locally
#   - create/edit release
#   - upload assets
# GitHub will associate the release with the tag once pushed.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${REPO_ROOT}" || exit 1

TAG="${1:-}"
ZIP_PATH="${2:-}"
TITLE="${3:-}"

if [ -z "${TAG}" ] || [ -z "${ZIP_PATH}" ]; then
  echo "ERROR: missing args" >&2
  echo "USAGE: petcare_release_publish.sh <TAG> <ZIP_PATH> [TITLE]" >&2
  exit 2
fi

# Hard gate: tag must exist locally (deterministic)
if ! git rev-parse -q --verify "refs/tags/${TAG}" >/dev/null 2>&1; then
  echo "ERROR: local tag does not exist: ${TAG}" >&2
  exit 3
fi

if [ ! -f "${ZIP_PATH}" ]; then
  echo "ERROR: ZIP not found: ${ZIP_PATH}" >&2
  exit 4
fi

SIDECAR="${ZIP_PATH}.sha256"
if [ ! -f "${SIDECAR}" ]; then
  echo "ERROR: sidecar missing: ${SIDECAR}" >&2
  exit 5
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: gh CLI not installed. Install GitHub CLI then re-run." >&2
  exit 6
fi

echo "=== GH AUTH STATUS ==="
if ! gh auth status >/dev/null 2>&1; then
  echo "ERROR: gh not authenticated. Run: gh auth login" >&2
  exit 7
fi

# Sidecar enforcement: sidecar must match actual zip sha256.
ZIP_SHA="$(shasum -a 256 "${ZIP_PATH}" | awk '{print $1}')"
WANT_SHA="$(awk '{print $1}' < "${SIDECAR}" | head -n 1 | tr -d '[:space:]')"

if [ -z "${WANT_SHA}" ]; then
  echo "ERROR: sidecar empty/invalid: ${SIDECAR}" >&2
  exit 8
fi

if [ "${ZIP_SHA}" != "${WANT_SHA}" ]; then
  echo "ERROR: sidecar SHA mismatch" >&2
  echo "zip_sha256=${ZIP_SHA}" >&2
  echo "sidecar_sha256=${WANT_SHA}" >&2
  exit 9
fi

if [ -z "${TITLE}" ]; then
  TITLE="${TAG}"
fi

echo "=== RELEASE PUBLISH ==="
echo "tag=${TAG}"
echo "title=${TITLE}"
echo "zip=${ZIP_PATH}"
echo "zip_sha256=${ZIP_SHA}"
echo "sidecar=${SIDECAR}"

# Notes are deterministic minimal metadata.
NOTES_FILE="$(mktemp)"
cat > "${NOTES_FILE}" <<EON
PetCare Release

tag: ${TAG}
zip_asset: $(basename "${ZIP_PATH}")
zip_sha256: ${ZIP_SHA}
sidecar_asset: $(basename "${SIDECAR}")
EON

set +e
gh release view "${TAG}" >/dev/null 2>&1
EXISTS_RC=$?
set -e

if [ "${EXISTS_RC}" -ne 0 ]; then
  echo "=== CREATE RELEASE (NO --verify-tag; pre-push safe) ==="
  gh release create "${TAG}" \
    --title "${TITLE}" \
    --notes-file "${NOTES_FILE}"
else
  echo "=== RELEASE EXISTS (EDIT NOTES/TITLE) ==="
  gh release edit "${TAG}" \
    --title "${TITLE}" \
    --notes-file "${NOTES_FILE}"
fi

# Upload assets (clobber to ensure deterministic update).
echo "=== UPLOAD ASSETS (CLOBBER) ==="
gh release upload "${TAG}" "${ZIP_PATH}" "${SIDECAR}" --clobber

echo "OK published release assets"
echo "tag=${TAG}"
echo "zip_sha256=${ZIP_SHA}"
