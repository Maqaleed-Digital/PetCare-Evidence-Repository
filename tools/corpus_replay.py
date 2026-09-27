"""Replay the COMPLETE committed perturbation corpus and classify every perturbation (MVC-EPC-D-001 D3).

  python3 tools/corpus_replay.py run <checkout> <out.json>      replay every evidence/replay/*/perturb_*.py in <checkout>
  python3 tools/corpus_replay.py compare <base.json> <head.json> [--new-dir <evidence/replay/dir>]
      D3(a) every perturbation in the PR's new replay dir is ARMED; D3(b) no committed perturbation changes
      classification between base and head; D3(c) every non-ARMED item is listed in evidence/replay/EXCLUSIONS.md.
A script that stops before classifying (e.g. an anchor no longer found) is recorded as `<script>::*` SCRIPT_ERROR.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

#: A perturbation id always contains a hyphen and never "=" — this excludes each script's "ARMED=n VACUOUS=m" summary.
LINE = re.compile(r"^([A-Za-z0-9]+-[A-Za-z0-9-]+) (ARMED|VACUOUS|SUPERSEDED)\b", re.M)


def run(checkout: str, out: str) -> None:
    root = Path(checkout).resolve()
    result = {}
    for script in sorted(root.glob("evidence/replay/*/perturb_*.py")):
        rel = script.relative_to(root).as_posix()
        p = subprocess.run([sys.executable, str(script), str(root)], cwd=root, capture_output=True, text=True, timeout=7200)
        found = LINE.findall(p.stdout)
        for pid, cls in found:
            result[f"{rel}::{pid}"] = cls
        if p.returncode != 0 and not found:
            result[f"{rel}::*"] = "SCRIPT_ERROR"
        print(f"{rel}: {sum(c == 'ARMED' for _, c in found)} ARMED, {len(found)} classified, rc={p.returncode}", flush=True)
    dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=root, capture_output=True, text=True).stdout
    if dirty.strip():
        raise SystemExit(f"replay left the tree modified:\n{dirty}")
    Path(out).write_text(json.dumps(result, indent=1, sort_keys=True))
    print(f"TOTAL {len(result)} · ARMED {sum(v == 'ARMED' for v in result.values())}")


def compare(base: str, head: str, new_dir: str | None) -> None:
    b, h = json.loads(Path(base).read_text()), json.loads(Path(head).read_text())
    listed = set(re.findall(r"^\| (\S+::\S+) \|", Path("evidence/replay/EXCLUSIONS.md").read_text(), re.M))
    problems = []
    if new_dir:
        new = {k: v for k, v in h.items() if k.startswith(new_dir.rstrip("/") + "/")}
        if not new:
            problems.append(f"D3(a) no perturbation found under {new_dir}")
        problems += [f"D3(a) {k} is {v}" for k, v in new.items() if v != "ARMED"]
    problems += [f"D3(b) {k}: {b[k]} -> {h.get(k, 'MISSING')}" for k in b if h.get(k) != b[k]]
    problems += [f"D3(c) {k} ({v}) not in EXCLUSIONS.md" for k, v in h.items() if v != "ARMED" and k not in listed]
    print(f"base {len(b)} · head {len(h)} · head ARMED {sum(v == 'ARMED' for v in h.values())} · "
          f"excluded {sum(v != 'ARMED' for v in h.values())}")
    if problems:
        print("\n".join(problems))
        raise SystemExit(1)
    print("D3 PASS")


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(sys.argv[2], sys.argv[3])
    else:
        nd = sys.argv[sys.argv.index("--new-dir") + 1] if "--new-dir" in sys.argv else None
        compare(sys.argv[2], sys.argv[3], nd)
