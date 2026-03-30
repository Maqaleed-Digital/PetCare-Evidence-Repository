import hashlib
import os
import sys

def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> int:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    reg_path = os.path.join(repo_root, "ops", "ph12_gate_registry.json")
    out_path = os.path.join(repo_root, "ops", "ph12_gate_registry.sha256")

    if not os.path.exists(reg_path):
        print(f"ERROR: missing {reg_path}")
        return 2

    digest = _sha256_file(reg_path)

    rel = "ops/ph12_gate_registry.json"
    line = f"{digest}  {rel}\n"

    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(line)

    os.replace(tmp, out_path)
    print(out_path)
    print(line.rstrip("\n"))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
