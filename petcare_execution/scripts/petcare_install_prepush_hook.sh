#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${REPO_ROOT}" || exit 1

HOOK_DIR="${REPO_ROOT}/.git/hooks"
HOOK_PATH="${HOOK_DIR}/pre-push"

mkdir -p "${HOOK_DIR}"

TMP_HOOK="$(mktemp)"
cat > "${TMP_HOOK}" <<'EOM'
#!/usr/bin/env bash
set -euo pipefail

# PetCare pre-push hook: publish GitHub Release assets automatically on production tag push.
# No guessing:
# - only runs on tag refs
# - only allows tags matching petcare-prod-*
# - requires PETCARE_RELEASE_ZIP env var pointing to the closure zip to upload

REMOTE_NAME="${1:-}"
REMOTE_URL="${2:-}"

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "${REPO_ROOT}" || exit 1

PUBLISHER="petcare_execution/scripts/petcare_release_publish.sh"

if [ ! -x "${PUBLISHER}" ]; then
  echo "ERROR: missing publisher script: ${PUBLISHER}" >&2
  exit 10
fi

# Read refs from stdin: <local ref> <local sha> <remote ref> <remote sha>
while read -r LOCAL_REF LOCAL_SHA REMOTE_REF REMOTE_SHA; do
  case "${LOCAL_REF}" in
    refs/tags/*)
      TAG="${LOCAL_REF#refs/tags/}"

      # Enforce prod tag pattern (hard gate, no guessing)
      if ! printf "%s" "${TAG}" | grep -qE '^petcare-prod-'; then
        echo "ERROR: tag push detected but tag does not match required pattern ^petcare-prod- : ${TAG}" >&2
        exit 11
      fi

      ZIP="${PETCARE_RELEASE_ZIP:-}"
      if [ -z "${ZIP}" ]; then
        echo "ERROR: PETCARE_RELEASE_ZIP is required when pushing prod tags." >&2
        echo "Example:" >&2
        echo "  PETCARE_RELEASE_ZIP=evidence_output/PETCARE-PH45-CLOSURE/PETCARE-PH45-CLOSURE_YYYYMMDDTHHMMSSZ.zip git push origin ${TAG}" >&2
        exit 12
      fi

      # Publish (will fail-fast if sidecar missing or sha mismatch)
      echo "=== PH48: auto publish release assets for tag ${TAG} ==="
      bash "${PUBLISHER}" "${TAG}" "${ZIP}" "${TAG}"

      ;;
    *)
      : ;;
  esac
done

exit 0
EOM

chmod +x "${TMP_HOOK}"
mv -f "${TMP_HOOK}" "${HOOK_PATH}"
chmod +x "${HOOK_PATH}"

echo "OK installed pre-push hook at ${HOOK_PATH}"
