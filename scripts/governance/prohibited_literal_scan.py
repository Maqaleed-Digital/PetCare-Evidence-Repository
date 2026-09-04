"""Scan for an ACTIVE literal `SECRET_KEY` default.

This instrument has produced a wrong answer twice, in both directions, and the
reason is the same each time: the retired literal legitimately appears on the
FIXED file.

    petcare_api/routers/auth.py:19   docstring quoting the old expression
    petcare_api/routers/auth.py:41   the guard that REJECTS the literal
    petcare_api/tests/*              test constants naming it

A substring search for `os.getenv("SECRET_KEY", "` matches the docstring and
reports every ref as vulnerable — including `origin/main`, which refuses to
start on that value. The only thing that is a defect is a module-level
assignment that hands the process a default, so that is what is matched.

Fails closed: scanning zero Python files is an error.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

#: A module-level assignment giving SECRET_KEY a fallback value. Anchored at the
#: start of a line, so an indented mention inside a docstring, a comparison or a
#: test constant does not match.
ACTIVE_DEFAULT = re.compile(
    r'^SECRET_KEY\s*=\s*os\.getenv\(\s*["\']SECRET_KEY["\']\s*,', re.MULTILINE
)

_SKIP_DIRS = {"node_modules", ".git", ".venv", "__pycache__", ".next"}


def python_files() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "-z", "--", "*.py"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout
    return [
        ROOT / p for p in out.split("\0")
        if p and not any(part in _SKIP_DIRS for part in Path(p).parts)
    ]


def scan() -> tuple[list[tuple[str, int]], int]:
    findings: list[tuple[str, int]] = []
    scanned = 0
    for path in python_files():
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        scanned += 1
        for match in ACTIVE_DEFAULT.finditer(text):
            line = text[: match.start()].count("\n") + 1
            findings.append((path.relative_to(ROOT).as_posix(), line))
    return findings, scanned


def main() -> int:
    findings, scanned = scan()
    if scanned == 0:
        print("No Python files scanned; refusing to report a clean result.")
        return 1
    for rel, line in findings:
        print(f"{rel}:{line}: active literal SECRET_KEY default")
    print(f"\nSCANNED={scanned} ACTIVE_LITERAL_DEFAULT={len(findings)}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
