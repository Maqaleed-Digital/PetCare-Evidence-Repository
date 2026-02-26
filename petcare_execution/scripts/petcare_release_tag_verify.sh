#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}" || exit 1

TAG="${1:-}"

if [ -z "${TAG}" ]; then
  echo "ERROR: missing tag argument"
  echo "USAGE: scripts/petcare_release_tag_verify.sh <release_tag>"
  exit 2
fi

echo "=== PETCARE RELEASE TAG VERIFY ==="
echo "repo_root=${REPO_ROOT}"
echo "tag=${TAG}"

if [ -n "$(git status --porcelain)" ]; then
  echo "ERROR: repo is dirty; release verification/attestation must run on a clean tree"
  git status -sb
  exit 3
fi

if ! git rev-parse "${TAG}" >/dev/null 2>&1; then
  echo "ERROR: tag not found: ${TAG}"
  exit 4
fi

TAG_SHA="$(git rev-list -n 1 "${TAG}")"
HEAD_SHA="$(git rev-parse HEAD)"

echo "tag_sha=${TAG_SHA}"
echo "head_sha=${HEAD_SHA}"

if [ "${TAG_SHA}" != "${HEAD_SHA}" ]; then
  echo "ERROR: tag does not point to current HEAD"
  exit 5
fi

DESC="$(git describe --tags --dirty --always)"
echo "tag_describe=${DESC}"

if echo "${DESC}" | grep -q -- "-dirty"; then
  echo "ERROR: describe indicates dirty state (should be unreachable due to porcelain check)"
  exit 6
fi

echo "PASS release tag verify"
