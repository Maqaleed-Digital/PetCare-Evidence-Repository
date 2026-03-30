import csv
import json
import os
import re
import sys
from typing import Dict, List, Optional, Tuple

PH_RE = re.compile(r"^PH(\d{1,2})(?:\.\d+)?$", re.IGNORECASE)

ALLOWED_EXTRA_PHASES = {"PH41"}

def norm(s: str) -> str:
  return (s or "").strip()

def norm_status(s: str) -> str:
  t = norm(s).lower()
  if t in ("closed", "done", "complete", "completed"):
    return "Closed"
  if t in ("open", "planned", "planning", "backlog", "not started", "not_started"):
    return "Open"
  if t in ("active", "in progress", "in_progress", "working"):
    return "Open"
  return norm(s) if norm(s) else "UNKNOWN"

def canon_domain(s: str) -> str:
  raw = norm(s)
  if not raw:
    return ""
  t = raw.replace("&", ",").replace("/", ",")
  parts = [p.strip() for p in t.split(",") if p.strip()]
  tokens = set()
  for p in parts:
    pl = p.lower()
    if pl == "ops" or pl == "operations":
      tokens.add("Ops")
      continue
    if pl == "security":
      tokens.add("Security")
      continue
    if pl == "ci":
      tokens.add("CI")
      continue
    if pl == "evidence":
      tokens.add("Evidence")
      continue
    if pl == "governance":
      tokens.add("Governance")
      continue
    if pl == "foundation":
      tokens.add("Foundation")
      continue
    if pl == "architecture":
      tokens.add("Architecture")
      continue
    if pl == "product":
      tokens.add("Product")
      continue
    tokens.add(p)

  if tokens == {"Ops", "Security"}:
    return "Security/Ops"
  if tokens == {"CI", "Ops", "Security"}:
    return "CI/Security/Ops"

  order = ["Foundation", "Architecture", "Product", "Governance", "Evidence", "Security", "Ops", "CI"]
  out = []
  for o in order:
    if o in tokens:
      out.append(o)
      tokens.remove(o)
  out.extend(sorted(tokens))
  return "/".join(out)

def pick_col(headers: List[str], rows: List[Dict[str, str]], prefer_names: List[str], value_pred=None) -> Optional[str]:
  hmap = {h.lower(): h for h in headers}
  for pn in prefer_names:
    if pn.lower() in hmap:
      return hmap[pn.lower()]
  if value_pred is not None:
    for h in headers:
      for r in rows[:50]:
        v = norm(r.get(h, ""))
        if v and value_pred(v):
          return h
  return None

def parse_int(s: str) -> Optional[int]:
  t = norm(s)
  if not t:
    return None
  try:
    return int(float(t))
  except Exception:
    return None

def load_registry(path: str) -> List[Dict]:
  data = json.load(open(path, "r", encoding="utf-8"))
  phases = data.get("phases", [])
  if not isinstance(phases, list):
    raise SystemExit("ERROR: REGISTRY.json phases must be a list")
  out = []
  for p in phases:
    phase = norm(str(p.get("phase", ""))).upper()
    status = norm_status(str(p.get("status", "")))
    weight = parse_int(str(p.get("weight", ""))) or 0
    domain = canon_domain(str(p.get("domain", ""))) or "UNKNOWN"
    out.append({"phase": phase, "status": status, "weight": weight, "domain": domain})
  return out

def load_notion_csv(path: str) -> Tuple[List[Dict[str, str]], List[str]]:
  with open(path, "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    headers = reader.fieldnames or []
    rows = [r for r in reader]
  if not headers:
    raise SystemExit("ERROR: Notion CSV has no headers")
  return rows, headers

def phase_value_pred(v: str) -> bool:
  return PH_RE.match(v.strip()) is not None

def main():
  if len(sys.argv) < 3:
    raise SystemExit("USAGE: reconcile.py <REGISTRY.json> <NOTION_EXPORT.csv> [OUT_REPORT.txt]")

  reg_path = sys.argv[1]
  notion_path = sys.argv[2]
  out_report = sys.argv[3] if len(sys.argv) >= 4 else ""

  reg = load_registry(reg_path)
  notion_rows, headers = load_notion_csv(notion_path)

  phase_col = pick_col(headers, notion_rows, ["Phase", "PHASE", "phase"], value_pred=phase_value_pred)
  status_col = pick_col(headers, notion_rows, ["Status", "STATUS", "status"], value_pred=None)
  weight_col = pick_col(headers, notion_rows, ["Weight", "WEIGHT", "weight"], value_pred=None)
  domain_col = pick_col(headers, notion_rows, ["PR Domain", "Domain", "domain", "pr domain"], value_pred=None)

  if not phase_col:
    raise SystemExit("ERROR: could not detect Phase column in Notion CSV (need a column containing PHxx values)")

  notion_map: Dict[str, Dict] = {}
  for r in notion_rows:
    ph_raw = norm(r.get(phase_col, ""))
    if not ph_raw:
      continue
    m = PH_RE.match(ph_raw)
    if not m:
      continue
    ph = f"PH{int(m.group(1)):02d}"
    if ph in notion_map:
      continue
    st = norm_status(r.get(status_col, "")) if status_col else "UNKNOWN"
    wt = parse_int(r.get(weight_col, "")) if weight_col else None
    dm = canon_domain(r.get(domain_col, "")) if domain_col else ""
    notion_map[ph] = {"phase": ph, "status": st, "weight": wt, "domain": dm}

  reg_map = {p["phase"].upper(): p for p in reg}

  missing_in_notion = []
  mismatches = []
  for ph, rp in sorted(reg_map.items()):
    if ph not in notion_map:
      missing_in_notion.append(ph)
      continue
    np = notion_map[ph]
    want_status = norm_status(rp["status"])
    have_status = norm_status(np["status"])
    want_weight = int(rp["weight"])
    have_weight = np["weight"]
    want_domain = canon_domain(rp["domain"])
    have_domain = canon_domain(np["domain"])

    status_ok = (want_status == have_status) or (want_status == "Open" and have_status in ("Open", "Planned"))
    weight_ok = (have_weight is None) or (want_weight == have_weight)
    domain_ok = (have_domain == "") or (want_domain == have_domain)

    if not (status_ok and weight_ok and domain_ok):
      mismatches.append({
        "phase": ph,
        "registry": {"status": want_status, "weight": want_weight, "domain": want_domain},
        "notion": {"status": have_status, "weight": have_weight, "domain": have_domain}
      })

  extra_in_notion = []
  for ph in sorted(notion_map.keys()):
    if ph not in reg_map and ph not in ALLOWED_EXTRA_PHASES:
      extra_in_notion.append(ph)

  def weighted_progress(items: List[Dict]) -> Tuple[int,int,float]:
    w_total = sum(int(p.get("weight", 0) or 0) for p in items)
    w_closed = sum(int(p.get("weight", 0) or 0) for p in items if norm_status(p.get("status","")) == "Closed")
    pct = 0.0 if w_total == 0 else (100.0 * w_closed / w_total)
    return w_total, w_closed, pct

  reg_wt, reg_wc, reg_pct = weighted_progress(reg)

  notion_items = []
  for ph, np in notion_map.items():
    wt = np["weight"]
    if wt is None and ph in reg_map:
      wt = reg_map[ph]["weight"]
    notion_items.append({"phase": ph, "status": np["status"], "weight": wt or 0})

  not_wt, not_wc, not_pct = weighted_progress(notion_items)

  lines = []
  lines.append("PETCARE PHASE REGISTRY RECONCILIATION REPORT")
  lines.append(f"registry={os.path.abspath(reg_path)}")
  lines.append(f"notion_csv={os.path.abspath(notion_path)}")
  lines.append("")
  lines.append("DETECTED COLUMNS")
  lines.append(f"phase_col={phase_col}")
  lines.append(f"status_col={status_col or 'NONE'}")
  lines.append(f"weight_col={weight_col or 'NONE'}")
  lines.append(f"domain_col={domain_col or 'NONE'}")
  lines.append("")
  lines.append("REGISTRY SUMMARY")
  lines.append(f"phases_total={len(reg)}")
  lines.append(f"weighted_total={reg_wt}")
  lines.append(f"weighted_closed={reg_wc}")
  lines.append(f"weighted_percent={reg_pct:.2f}")
  lines.append("")
  lines.append("NOTION SUMMARY (weights: notion if present else registry fallback)")
  lines.append(f"phases_detected={len(notion_map)}")
  lines.append(f"weighted_total={not_wt}")
  lines.append(f"weighted_closed={not_wc}")
  lines.append(f"weighted_percent={not_pct:.2f}")
  lines.append("")
  lines.append("DIFFS")
  lines.append(f"missing_in_notion_count={len(missing_in_notion)}")
  for ph in missing_in_notion:
    lines.append(f"- missing_in_notion: {ph}")
  lines.append(f"extra_in_notion_count={len(extra_in_notion)}")
  for ph in extra_in_notion:
    lines.append(f"- extra_in_notion: {ph}")
  lines.append(f"mismatch_count={len(mismatches)}")
  for mm in mismatches:
    ph = mm["phase"]
    r = mm["registry"]
    n = mm["notion"]
    lines.append(f"- mismatch {ph}: registry(status={r['status']}, weight={r['weight']}, domain={r['domain']}) vs notion(status={n['status']}, weight={n['weight']}, domain={n['domain']})")

  ok = (len(missing_in_notion) == 0 and len(extra_in_notion) == 0 and len(mismatches) == 0)

  lines.append("")
  lines.append(f"RESULT={'PASS' if ok else 'FAIL'}")

  report = "\n".join(lines) + "\n"
  if out_report:
    with open(out_report, "w", encoding="utf-8", newline="\n") as f:
      f.write(report)
  sys.stdout.write(report)

  if not ok:
    sys.exit(2)

if __name__ == "__main__":
  main()
