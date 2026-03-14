#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}" || exit 1

echo "=== PETCARE RELEASE INTEGRITY CHECK ==="

for f in "POLICY.md" "POLICY.sha256" "REGISTRY.json" "REGISTRY.sha256"; do
  if [ ! -f "${f}" ]; then
    echo "MISSING_REQUIRED_FILE=${f}"
    exit 3
  fi
done

sha_check() {
  local target="$1"
  local sidecar="$2"
  local actual expected

  if command -v shasum >/dev/null 2>&1; then
    actual="$(shasum -a 256 "${target}" | awk '{print $1}')"
  elif command -v sha256sum >/dev/null 2>&1; then
    actual="$(sha256sum "${target}" | awk '{print $1}')"
  else
    echo "NO_SHA_TOOL_AVAILABLE"
    exit 3
  fi

  expected="$(awk '{print $1}' "${sidecar}")"

  if [ "${actual}" != "${expected}" ]; then
    echo "SHA_MISMATCH target=${target} expected=${expected} actual=${actual}"
    exit 3
  fi

  echo "SHA_OK ${target}"
}

sha_check "POLICY.md" "POLICY.sha256"

if [ -f "REGISTRY.json.sha256" ]; then
  sha_check "REGISTRY.json" "REGISTRY.json.sha256"
else
  sha_check "REGISTRY.json" "REGISTRY.sha256"
fi

if [ -n "$(git status --porcelain)" ]; then
  echo "WORKTREE_NOT_CLEAN"
  git status -sb
  exit 3
fi

echo "RELEASE_INTEGRITY_PASS"
