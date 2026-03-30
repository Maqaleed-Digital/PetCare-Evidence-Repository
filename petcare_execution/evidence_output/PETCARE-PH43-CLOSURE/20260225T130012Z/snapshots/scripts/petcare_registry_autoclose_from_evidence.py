import glob
import json
import os
import re
import sys
from typing import Dict, List, Tuple

PH_RE = re.compile(r"^PH(\d{1,2})$", re.IGNORECASE)

def norm_phase(s: str) -> str:
  s=(s or "").strip().upper()
  m=PH_RE.match(s)
  if not m:
    return s
  return f"PH{int(m.group(1)):02d}"

def find_closure_zip(repo_root: str, ph: str) -> List[str]:
  ph = norm_phase(ph)
  patt = os.path.join(repo_root, "evidence_output", f"PETCARE-{ph}-CLOSURE", f"PETCARE-{ph}-CLOSURE_*.zip")
  hits = sorted(glob.glob(patt))
  return hits

def main():
  if len(sys.argv) < 2:
    raise SystemExit("USAGE: autoclose.py <repo_root> [--apply]")

  repo_root = os.path.abspath(sys.argv[1])
  apply = ("--apply" in sys.argv[2:])

  reg_path = os.path.join(repo_root, "REGISTRY.json")
  if not os.path.isfile(reg_path):
    raise SystemExit(f"ERROR: missing {reg_path}")

  data = json.load(open(reg_path, "r", encoding="utf-8"))
  phases = data.get("phases", [])
  if not isinstance(phases, list):
    raise SystemExit("ERROR: REGISTRY.json phases must be a list")

  changes: List[Tuple[str,str,str]] = []
  open_list = []
  for p in phases:
    ph = norm_phase(str(p.get("phase","")))
    st = str(p.get("status","")).strip()
    if st.lower() != "closed":
      open_list.append(ph)
      zips = find_closure_zip(repo_root, ph)
      if zips:
        old = st
        new = "Closed"
        changes.append((ph, old, new))
        if apply:
          p["status"] = "Closed"

  print("PETCARE REGISTRY AUTOCLOSE FROM EVIDENCE")
  print(f"repo_root={repo_root}")
  print(f"registry={reg_path}")
  print(f"open_before={len(open_list)}")
  print(f"closable_found={len(changes)}")
  for ph, old, new in changes:
    z = find_closure_zip(repo_root, ph)
    zshow = os.path.relpath(z[-1], repo_root).replace("\\","/") if z else "NONE"
    print(f"- {ph}: {old} -> {new} (evidence_zip={zshow})")

  if not apply:
    print("")
    print("RESULT=DRY_RUN")
    return

  tmp = reg_path + ".tmp"
  with open(tmp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write("\n")

  os.replace(tmp, reg_path)

  print("")
  print("RESULT=APPLIED")
  print("OK wrote REGISTRY.json")

if __name__ == "__main__":
  main()
