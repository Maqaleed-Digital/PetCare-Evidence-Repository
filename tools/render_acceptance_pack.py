#!/usr/bin/env python3
"""
Render the DRAFT Phase-1 High acceptance pack for Sponsor review (MVC-ACCEPT-PACK-P1).
Usage: python3 tools/render_acceptance_pack.py > requirements/acceptance/phase1_high_pack.draft.md
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True).strip())
PACK = ROOT / "requirements" / "acceptance" / "phase1_high_pack.draft.json"


def main() -> int:
    p = json.loads(PACK.read_text(encoding="utf-8"))
    out = [
        "# Phase-1 High acceptance pack — DRAFT, NOT RATIFIED", "",
        f"Authority: {', '.join(p['authority'])}",
        f"BRD SHA-256: {p['denominator']['brd_sha256']}",
        f"W1 status measured at: {p['w1_measured_at']}", "",
        "## Sponsor decision", "",
        "```",
        "[SPONSOR]",
        "DECISION=MVC-ACCEPT-PACK-P1",
        "RESULT=<RATIFY_ALL | RATIFY_EXCEPT>",
        "EXCEPTIONS=[<AC-id or FR-id>: <reason>, ...]",
        "```", "",
        "## Summary", "",
        "| FR | Title | W1 status | Criteria | Dependencies | Interpretations |",
        "|---|---|---|---|---|---|",
    ]
    for fr in sorted(p["fr"]):
        e = p["fr"][fr]
        cs = e["criteria"]
        deps = sorted({c["dependency"] for c in cs if c["dependency"] != "NONE"})
        interp = sum(1 for c in cs if c["interpretation"])
        out.append(f"| {fr} | {e['title']} | {e['w1_status']} | {len(cs)} | "
                   f"{', '.join(deps) or '—'} | {interp} |")
    for fr in sorted(p["fr"]):
        e = p["fr"][fr]
        out += ["", f"## {fr} — {e['title']}", "",
                f"Candidate source: {e['candidate_source']} · Customer-facing: {e['customer_facing']} · "
                f"Client acceptance applies: {e['client_acceptance_applies']}", ""]
        for c in e["criteria"]:
            out += [f"**{c['id']}** — {c['statement']}",
                    f"- Fails if: {c['fails_if']}",
                    f"- Evidence: {', '.join(c['evidence'])}",
                    f"- Sources: {', '.join(s['kind'] + ':' + s['ref'] for s in c['sources'])}",
                    f"- Dependency: {c['dependency']}"]
            if c["interpretation"]:
                out.append(f"- Interpretation for Sponsor: {c['interpretation']}")
            out.append("")
    out += ["## Non-functional requirements", ""]
    for n in sorted(p["nfr"]):
        e = p["nfr"][n]
        out.append(f"**{n} — {e['title']}** · Phase-1 relevant: {e['phase1_relevant']} — {e['rationale']}")
        d = e.get("evidence_definition")
        if d:
            out.append(f"- Metric: {d['metric']} · Method: {d['method']} · Threshold: {d['threshold']} · "
                       f"Environment: {d['environment']} · Dependency: {d['dependency']}")
        out.append("")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
