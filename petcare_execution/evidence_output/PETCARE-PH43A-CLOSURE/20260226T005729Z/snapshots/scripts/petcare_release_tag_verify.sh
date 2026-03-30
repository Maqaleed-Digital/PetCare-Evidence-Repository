#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}" || exit 1

TAG="${1:-}"
if [ -z "${TAG}" ]; then
  echo "USAGE: bash scripts/petcare_release_tag_verify.sh <RELEASE_TAG>"
  exit 2
fi

echo "=== RELEASE TAG VERIFY ==="
echo "repo=${ROOT}"
echo "tag=${TAG}"

if ! git rev-parse -q --verify "${TAG}^{commit}" >/dev/null; then
  echo "RESULT=FAIL"
  echo "TAG_INVALID_OR_NOT_COMMIT=${TAG}"
  exit 1
fi

SHA="$(git rev-parse "${TAG}^{commit}")"
DESC="$(git describe --tags --always --dirty 2>/dev/null || true)"

echo "TAG_SHA=${SHA}"
echo "TAG_DESCRIBE=${DESC}"
echo "RESULT=PASS"
