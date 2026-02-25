#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
REG="${ROOT%/}/REGISTRY.json"

if [ ! -f "${REG}" ]; then
  echo "ERROR: missing REGISTRY.json at ${REG}"
  exit 1
fi

python3 - << 'PY' "${REG}"
import json,sys,collections
reg_path=sys.argv[1]
data=json.load(open(reg_path,"r",encoding="utf-8"))

phases=data.get("phases",[])
if not isinstance(phases,list):
  raise SystemExit("ERROR: REGISTRY.json phases must be a list")

total=len(phases)
closed=[p for p in phases if str(p.get("status","")).lower()=="closed"]
closed_n=len(closed)

def w(p):
  try:
    return int(p.get("weight",0))
  except Exception:
    return 0

w_total=sum(w(p) for p in phases)
w_closed=sum(w(p) for p in closed)
pct = 0.0 if w_total==0 else (100.0*w_closed/w_total)

by_domain=collections.defaultdict(lambda: {"total":0,"closed":0,"w_total":0,"w_closed":0})
for p in phases:
  dom=str(p.get("domain","UNKNOWN"))
  by_domain[dom]["total"] += 1
  by_domain[dom]["w_total"] += w(p)
  if str(p.get("status","")).lower()=="closed":
    by_domain[dom]["closed"] += 1
    by_domain[dom]["w_closed"] += w(p)

print("PETCARE PROGRESS REPORT")
print(f"registry_version={data.get('version')}")
print(f"generated_utc={data.get('generated_utc')}")
print(f"phases_total={total}")
print(f"phases_closed={closed_n}")
print(f"weighted_total={w_total}")
print(f"weighted_closed={w_closed}")
print(f"weighted_percent={pct:.2f}")

print("")
print("BY DOMAIN")
for dom in sorted(by_domain.keys()):
  d=by_domain[dom]
  dpct = 0.0 if d["w_total"]==0 else (100.0*d["w_closed"]/d["w_total"])
  print(f"- {dom}: phases {d['closed']}/{d['total']}, weight {d['w_closed']}/{d['w_total']}, percent {dpct:.2f}")
PY
