"""Secret scan over git-tracked files.

Written after the shell version of this check failed on itself. A `grep -rE`
for secret patterns matches the file that *defines* those patterns — the
workflow step, and an older release-integrity script that carries a similar
regex. The scan then exits non-zero on a repository containing no secrets,
which trains everyone to ignore it.

Two decisions follow from that:

* Only git-TRACKED files are scanned. Untracked scratch (`.claude-flow/`),
  `node_modules`, build output and virtualenvs are not part of what the
  repository publishes, and scanning them produces noise that buries signal.
* Files that legitimately contain the patterns because they define them are
  allowlisted BY PATH WITH A REASON, and a test asserts every entry still
  exists. An allowlist that silently accumulates dead paths becomes a hole.

The patterns are deliberately high-signal — real key material and provider
tokens. Bare names like `SECRET_KEY=` are excluded: this repository is full of
legitimate references to `SECRET_KEY` (the W0-A guard, its tests, its
docstrings), and a scanner that fires on all of them is one that gets muted.

Fails closed: scanning zero files is an error, not a pass.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PATTERNS: dict[str, re.Pattern[str]] = {
    "private_key_block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "aws_access_key_id": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "aws_secret_access_key": re.compile(r"aws_secret_access_key\s*[=:]\s*\S{20,}"),
    "slack_token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "google_api_key": re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b"),
}

#: Paths whose content matches a pattern because they DEFINE it.
#:
#: Kept as small as it can be. Two entries were removed after a test proved they
#: matched nothing: this file's own patterns are written with character classes
#: (`[A-Z ]*`, `[0-9A-Z]{16}`) and so do not match themselves, and the workflow
#: only names the scripts. Allowlisting either "just in case" would have created
#: a permanent blind spot over a file nobody re-reads.
#:
#: Every entry needs a reason; tests assert each path still exists AND would
#: genuinely have been a finding without the entry.
#: Currently EMPTY, and that is the correct state.
#:
#: The third entry was removed after CI failed on it: it named a file under
#: `petcare_execution/evidence_output/`, which `.gitignore` excludes. The file
#: exists in a working copy and not in the repository, so `tracked_files()`
#: never saw it and the entry protected nothing — it only looked like it did.
#: Local runs could not detect that; a clean checkout did immediately.
ALLOWLIST: dict[str, str] = {}

_SKIP_DIRS = {"node_modules", ".git", ".next", ".venv", "__pycache__"}


def tracked_files() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout
    paths = [ROOT / p for p in out.split("\0") if p]
    return [
        p for p in paths
        if p.is_file() and not any(part in _SKIP_DIRS for part in p.parts)
    ]


def scan() -> tuple[list[tuple[str, int, str]], int]:
    findings: list[tuple[str, int, str]] = []
    scanned = 0
    for path in tracked_files():
        rel = path.relative_to(ROOT).as_posix()
        if rel in ALLOWLIST:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # binary or unreadable; nothing textual to match
        scanned += 1
        for lineno, line in enumerate(text.splitlines(), start=1):
            for name, pattern in PATTERNS.items():
                if pattern.search(line):
                    findings.append((rel, lineno, name))
    return findings, scanned


def main() -> int:
    findings, scanned = scan()
    if scanned == 0:
        print("No files were scanned; refusing to report a clean result.")
        return 1
    for rel, lineno, name in findings:
        print(f"{rel}:{lineno}: {name}")
    print(f"\nSCANNED={scanned} ALLOWLISTED={len(ALLOWLIST)} FINDINGS={len(findings)}")
    if findings:
        print("SECRET_SCAN=FINDINGS")
        return 1
    print("SECRET_SCAN=CLEAN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
