#!/usr/bin/env bash
set -euo pipefail

# Deterministic GitHub Release publisher for PetCare evidence closure zips.
# No guessing:
# - requires TAG (local tag must exist)
# - requires ZIP exists
# - requires ZIP.sha256 exists and matches computed SHA256
#
# Pre-push safe:
# - GitHub may not have the tag yet (hook runs before push completes).
# - gh release create requires the tag to exist remotely OR you must specify --target.
# - We deterministically derive --target from the local tag commit SHA.

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

# Hard gate: tag must exist locally
if ! git rev-parse -q --verify "refs/tags/${TAG}" >/dev/null 2>&1; then
  echo "ERROR: local tag does not exist: ${TAG}" >&2
  exit 3
fi

# Deterministic: derive commit SHA behind the tag
TARGET_SHA="$(git rev-list -n 1 "${TAG}" 2>/dev/null || true)"
if [ -z "${TARGET_SHA}" ]; then
  echo "ERROR: could not derive TARGET_SHA for tag: ${TAG}" >&2
  exit 4
fi

if [ ! -f "${ZIP_PATH}" ]; then
  echo "ERROR: ZIP not found: ${ZIP_PATH}" >&2
  exit 5
fi

SIDECAR="${ZIP_PATH}.sha256"
if [ ! -f "${SIDECAR}" ]; then
  echo "ERROR: sidecar missing: ${SIDECAR}" >&2
  exit 6
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: gh CLI not installed." >&2
  exit 7
fi

echo "=== GH AUTH STATUS ==="
if ! gh auth status >/dev/null 2>&1; then
  echo "ERROR: gh not authenticated. Run: gh auth login" >&2
  exit 8
fi

ZIP_SHA="$(shasum -a 256 "${ZIP_PATH}" | awk '{print $1}')"
WANT_SHA="$(awk '{print $1}' < "${SIDECAR}" | head -n 1 | tr -d '[:space:]')"

if [ -z "${WANT_SHA}" ]; then
  echo "ERROR: sidecar empty/invalid: ${SIDECAR}" >&2
  exit 9
fi

if [ "${ZIP_SHA}" != "${WANT_SHA}" ]; then
  echo "ERROR: sidecar SHA mismatch" >&2
  echo "zip_sha256=${ZIP_SHA}" >&2
  echo "sidecar_sha256=${WANT_SHA}" >&2
  exit 10
fi

if [ -z "${TITLE}" ]; then
  TITLE="${TAG}"
fi

echo "=== RELEASE PUBLISH ==="
echo "tag=${TAG}"
echo "title=${TITLE}"
echo "target_sha=${TARGET_SHA}"
echo "zip=${ZIP_PATH}"
echo "zip_sha256=${ZIP_SHA}"
echo "sidecar=${SIDECAR}"

NOTES_FILE="$(mktemp)"
cat > "${NOTES_FILE}" <<EON
PetCare Release

tag: ${TAG}
target_sha: ${TARGET_SHA}
zip_asset: $(basename "${ZIP_PATH}")
zip_sha256: ${ZIP_SHA}
sidecar_asset: $(basename "${SIDECAR}")
EON

set +e
gh release view "${TAG}" >/dev/null 2>&1
EXISTS_RC=$?
set -e

if [ "${EXISTS_RC}" -ne 0 ]; then
  echo "=== CREATE RELEASE (PRE-PUSH SAFE via --target) ==="
  gh release create "${TAG}" \
    --target "${TARGET_SHA}" \
    --title "${TITLE}" \
    --notes-file "${NOTES_FILE}"
else
  echo "=== RELEASE EXISTS (EDIT NOTES/TITLE) ==="
  gh release edit "${TAG}" \
    --title "${TITLE}" \
    --notes-file "${NOTES_FILE}"
fi

echo "=== UPLOAD ASSETS (CLOBBER) ==="
gh release upload "${TAG}" "${ZIP_PATH}" "${SIDECAR}" --clobber

echo "OK published release assets"
echo "tag=${TAG}"
echo "zip_sha256=${ZIP_SHA}"
