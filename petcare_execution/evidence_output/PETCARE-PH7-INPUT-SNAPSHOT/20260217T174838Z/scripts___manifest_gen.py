from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("PETCARE_ROOT", ".")).resolve()
OUT = ROOT / "EVIDENCE" / "MANIFEST.json"

EXCLUDE_DIRS = {".git", ".venv", "__pycache__", ".DS_Store"}

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def is_excluded(path: Path) -> bool:
    for part in path.parts:
        if part in EXCLUDE_DIRS:
            return True
    return False

def rel_posix(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()

files = []
for p in sorted(ROOT.rglob("*")):
    if p.is_dir():
        continue
    if is_excluded(p):
        continue
    rp = rel_posix(p)
    if rp == "EVIDENCE/MANIFEST.json":
        continue
    st = p.stat()
    files.append(
        {
            "path": rp,
            "bytes": int(st.st_size),
            "sha256": sha256_file(p),
        }
    )

manifest = {
    "root": str(ROOT),
    "file_count": len(files) + 1,
    "files": files + [],
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

m2 = json.loads(OUT.read_text(encoding="utf-8"))
self_hash = sha256_file(OUT)
self_bytes = OUT.stat().st_size
m2["files"].append({"path": "EVIDENCE/MANIFEST.json", "bytes": int(self_bytes), "sha256": self_hash})
m2["files"].sort(key=lambda x: x["path"])
m2["file_count"] = len(m2["files"])
OUT.write_text(json.dumps(m2, indent=2, sort_keys=True) + "\n", encoding="utf-8")
