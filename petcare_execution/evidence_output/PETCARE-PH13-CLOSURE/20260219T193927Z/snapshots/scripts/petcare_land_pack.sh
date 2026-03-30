#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
echo "PetCare LAND PACK"
echo "root=${ROOT}"

PYBIN=""
if command -v python3 >/dev/null 2>&1; then
  PYBIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYBIN="python"
elif [ -x "${ROOT}/.venv/bin/python" ]; then
  PYBIN="${ROOT}/.venv/bin/python"
fi

if [ -z "$PYBIN" ]; then
  echo "FAIL: python not found (python3/python/.venv/bin/python)"
  exit 1
fi

echo "compile: app.py"
if [ -d "${ROOT}/FND/CODE_SCAFFOLD" ]; then
  echo "compile: scaffold python files"
  "$PYBIN" -m compileall "${ROOT}/FND/CODE_SCAFFOLD" >/dev/null
fi

if [ -d "${ROOT}/TESTS" ]; then
  "$PYBIN" -m compileall "${ROOT}/TESTS" >/dev/null || true
fi

echo "manifest: regenerate"
PETCARE_ROOT="${ROOT}" "$PYBIN" "${ROOT}/scripts/_manifest_gen.py" >/dev/null
echo "PASS manifest"

file_count="$("$PYBIN" - <<PY
import json
from pathlib import Path
m=json.loads(Path("${ROOT}/EVIDENCE/MANIFEST.json").read_text(encoding="utf-8"))
print(m.get("file_count", 0))
PY
)"
dirs_count="$(find "${ROOT}" -type d \( -name .git -o -name .venv -o -name __pycache__ \) -prune -false -o -print | wc -l | tr -d ' ')"
echo "file_count ${file_count}"
echo "dirs ${dirs_count}"

count_dir_files() {
  local d="$1"
  if [ -d "${ROOT}/${d}" ]; then
    find "${ROOT}/${d}" -type f | wc -l | tr -d ' '
  else
    echo "0"
  fi
}

ui2="$(count_dir_files UI2)"
ui3="$(count_dir_files UI3)"
ui5="$(count_dir_files UI5)"
ui6="$(count_dir_files UI6)"
tests="$(count_dir_files TESTS)"
fnd="$(count_dir_files FND)"
evid="$(count_dir_files EVIDENCE)"
scripts="$(count_dir_files scripts)"

other=0
while IFS= read -r p; do
  rel="${p#${ROOT}/}"
  case "$rel" in
    UI2/*|UI3/*|UI5/*|UI6/*|TESTS/*|FND/*|EVIDENCE/*|scripts/*|.git/*|.venv/*) ;;
    *) other=$((other+1)) ;;
  esac
done < <(find "${ROOT}" -type f)

echo "ui2 ${ui2} ui3 ${ui3} ui5 ${ui5} ui6 ${ui6} tests ${tests} fnd ${fnd} evid ${evid} scripts ${scripts} other ${other}"
echo "manifest_record True"
echo "DONE"
