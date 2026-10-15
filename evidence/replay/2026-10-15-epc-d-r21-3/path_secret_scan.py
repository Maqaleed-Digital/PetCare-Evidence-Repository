"""Apply the repository's secret_scan.PATTERNS (6) to named paths. Prints pattern id + line number only, never values."""
import hashlib, importlib.util, sys
from pathlib import Path
repo = Path(sys.argv[1]); targets = sys.argv[2:]
src = repo / "scripts/governance/secret_scan.py"
spec = importlib.util.spec_from_file_location("secret_scan", src); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
pset = "\n".join(f"{k}\t{v.pattern}" for k, v in m.PATTERNS.items()).encode()
print(f"SCANNER={src.relative_to(repo)} sha256={hashlib.sha256(src.read_bytes()).hexdigest()}")
print(f"PATTERNS={len(m.PATTERNS)} ids={','.join(m.PATTERNS)} pattern_set_sha256={hashlib.sha256(pset).hexdigest()}")
total = 0
for t in targets:
    p = Path(t); b = p.read_bytes(); n = 0
    for i, line in enumerate(b.decode("utf-8").splitlines(), 1):
        for k, pat in m.PATTERNS.items():
            if pat.search(line): print(f"HIT {t}:{i}: {k}"); n += 1
    total += n
    print(f"FILE {t} bytes={len(b)} lines={len(b.decode('utf-8').splitlines())} sha256={hashlib.sha256(b).hexdigest()} findings={n}")
print(f"TOTAL_FINDINGS={total} RESULT={'FINDINGS' if total else 'CLEAN'}")
