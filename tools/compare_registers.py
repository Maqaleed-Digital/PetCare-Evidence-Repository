#!/usr/bin/env python3
"""
MVC-ACCEPT-AUTH-001: deterministic field comparison, BRD v1.0 register spine vs
MVC-BRD-001 V3.0 DRAFT.

  python3 tools/compare_registers.py > requirements/authority/v1_0_vs_v3_0.json

Baseline: requirements/register.yaml (generated from the v1.0 BRD by
tools/gen_register.py). Candidate: V3.0, read through
tools/extract_v30_requirements.py because the canonical generator cannot parse
it. Compared per FR: presence, title, priority, phase. Status is ignored.

A field the candidate does not carry at all is reported under
`fields_not_carried_by_candidate`, NOT as a change: "V3.0 assigns no phase" and
"V3.0 moved FR-11 to phase 1" are different facts, and counting the first as the
second would manufacture 62 changes out of an absence.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import extract_v30_requirements as V30  # noqa: E402

REGISTER = ROOT / "requirements" / "register.yaml"
FR_ENTRY = re.compile(
    r'^  - id: (FR-\d{2})\n    title: "(.*)"\n    priority: (\w+)\n    phase: (\d)\n', re.M)
FIELDS = ("title", "priority", "phase")


def baseline() -> tuple:
    text = REGISTER.read_text(encoding="utf-8")
    src = re.search(r"^  path: (.+)$", text, re.M).group(1).strip()
    rows = {m.group(1): {"title": m.group(2), "priority": m.group(3), "phase": int(m.group(4))}
            for m in FR_ENTRY.finditer(text)}
    return src, rows


def main() -> int:
    base_src, base = baseline()
    cand = V30.extract()
    cfr = cand["fr"]
    changed = {}
    for fr in sorted(set(base) & set(cfr)):
        diff = {}
        for f in FIELDS:
            if f in cand["fields_not_carried"]:
                continue
            if base[fr][f] != cfr[fr][f]:
                diff[f] = {"baseline": base[fr][f], "candidate": cfr[fr][f]}
        if diff:
            changed[fr] = diff
    doc = {
        "baseline": f"{base_src} (via requirements/register.yaml)",
        "candidate": f"{cand['source']} sha256={cand['sha256']} ({cand['form']})",
        "only_in_baseline": sorted(set(base) - set(cfr)),
        "only_in_candidate": sorted(set(cfr) - set(base)),
        "changed": changed,
        "fields_not_carried_by_candidate": cand["fields_not_carried"],
        "candidate_disposition": {fr: cfr[fr]["disposition"] for fr in sorted(cfr)},
        "candidate_new_unnumbered": cand["new_unnumbered"],
        "counts": {
            "baseline_fr": len(base),
            "candidate_fr": len(cfr),
            "title_changes": sum("title" in d for d in changed.values()),
            "priority_changes": sum("priority" in d for d in changed.values()),
            "phase_changes": sum("phase" in d for d in changed.values()),
        },
    }
    print(json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
