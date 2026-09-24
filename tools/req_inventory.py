#!/usr/bin/env python3
"""
MVC-ACCEPT-AUTH-001 REQ-* estate inventory.

  python3 tools/req_inventory.py > requirements/authority/req_inventory.json

WHAT IT READS. A FROZEN manifest of the requirement-AUTHORITY instruments:
the SET-A documents declared in
petcare_execution/AUTHORITY/MVC-LINEAGE/DENOMINATOR_RECONCILIATION.md, which
are exactly the tracked files under AUTHORITY_ROOT. source_class() enforces the
boundary: product, web, migration, test, tool and generated sources are refused
by class. Each source is pinned by sha256. A missing or changed source exits 2: an inventory computed
over a corpus that moved is not the inventory that was measured, and re-pinning
is a deliberate act, never an automatic one.

GRAMMAR. The repository's governed identifier grammar is REUSED, not restated:
`petcare_execution/tools/mvc_inventory.py` (IDENTIFIER, namespace references,
metavariables, prose suffixes, prefix phantoms). Its `build()` computes the
union, so this tool and the governed 511 measurement cannot disagree about
what an identifier is.

FAILS-IF. Only acceptance/failure language AUTHORED in a source, keyed to a
REQ, is recorded, verbatim. A line qualifies when it opens with "Acceptance —
fails if", "Build fails if", "CI fails if" or "Fails if". It is attributed to
the nearest preceding REQ header in the same source — a line that opens with
exactly one concrete REQ id followed by a provenance tag, separator or line
end (HEADER_TAIL), or a Markdown heading naming exactly one — within
MAX_ATTRIBUTION_DISTANCE lines, with no intervening header. A range header
("REQ-MVC-8.32–8.45"), a multi-id header or a non-REQ Markdown heading breaks
attribution; such lines are counted as unattributed rather than guessed.
Nothing is paraphrased, normalised or authored.
"""
import hashlib
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "petcare_execution" / "tools"))
import mvc_inventory as M  # noqa: E402 — governed grammar, reused

MAX_ATTRIBUTION_DISTANCE = 40
CONTEXT = 160

#: The six-document set whose union the repository reconciled to 511
#: (petcare_execution/AUTHORITY/MVC-LINEAGE/DENOMINATOR_RECONCILIATION.md, SET-A).
SET_A = (
    "petcare_execution/AUTHORITY/MVC-LINEAGE/sources/MVC-BRD-001_V3_1_CANDIDATE_MyVetiCare_Master_BRD.docx",
    "petcare_execution/AUTHORITY/MVC-LINEAGE/sources/MVC-BRD-001_V3_2_EXECUTION_BASELINE_CANDIDATE.md",
    "petcare_execution/AUTHORITY/MVC-LINEAGE/sources/MVC-CLOSE-001_V1_1_PhaseA_Execution_Boundary.docx",
    "petcare_execution/AUTHORITY/MVC-LINEAGE/sources/MVC-GAP-001_V1_7_Ledger_Amendment_ARCH01_Closed_ARCH05_Allocated.md",
    "petcare_execution/AUTHORITY/MVC-LINEAGE/sources/MVC-SPEC-001_V3_0_Execution_Specification_Completion_Pass_Tranches_1_to_3.docx",
    "petcare_execution/AUTHORITY/MVC-LINEAGE/sources/MVC-SPEC-001_V3_1_Annex_K_Split_Taxpayer_Requirements.md",
)

# Frozen at measurement, 2026-09-24. v1.2: SET-A authority sources ONLY.
# v1.1 pinned all 43 REQ-bearing tracked files, including product code, tests,
# tooling and generated outputs; any build change then failed acceptance
# authority CI. Only requirement-authority instruments belong here, and
# source_class() below refuses anything else.
MANIFEST = [
    {"path": "petcare_execution/AUTHORITY/MVC-LINEAGE/sources/MVC-BRD-001_V3_1_CANDIDATE_MyVetiCare_Master_BRD.docx", "sha256": "024501e639ba3b6d28c76c5f05072e78dfe8f26b5ee9c79258c2a21141078792"},
    {"path": "petcare_execution/AUTHORITY/MVC-LINEAGE/sources/MVC-BRD-001_V3_2_EXECUTION_BASELINE_CANDIDATE.md", "sha256": "32f5366925128ca8f1332a412b253b2a1b797baf08cf6dd5777fac118efc287d"},
    {"path": "petcare_execution/AUTHORITY/MVC-LINEAGE/sources/MVC-CLOSE-001_V1_1_PhaseA_Execution_Boundary.docx", "sha256": "27a07179d911e8ff885a5020dee4832ba9c939b1a9758cb0ad5207d4401c85bc"},
    {"path": "petcare_execution/AUTHORITY/MVC-LINEAGE/sources/MVC-GAP-001_V1_7_Ledger_Amendment_ARCH01_Closed_ARCH05_Allocated.md", "sha256": "e8d221b4beb82708b14d690dd0202f7a3c8e4b8a030cb6281cff5814e98f3ff1"},
    {"path": "petcare_execution/AUTHORITY/MVC-LINEAGE/sources/MVC-SPEC-001_V3_0_Execution_Specification_Completion_Pass_Tranches_1_to_3.docx", "sha256": "a3f2fb2c2a4eb709187dccbee7f045a0b48e0d8364c4816de8f680e93b0a3a19"},
    {"path": "petcare_execution/AUTHORITY/MVC-LINEAGE/sources/MVC-SPEC-001_V3_1_Annex_K_Split_Taxpayer_Requirements.md", "sha256": "058356cc916f9a274315bf19e6e6cbb0d9a20e0c2bc69d471cf94a87d6461c3b"},
]

#: The one directory that holds requirement-authority instruments.
AUTHORITY_ROOT = "petcare_execution/AUTHORITY/MVC-LINEAGE/sources/"
AUTHORITY_SUFFIXES = (".md", ".docx")
#: Source classes that can never be requirement authority, checked before the
#: allow-root so a violation is named by what it is (most specific first: a
#: test inside a product tree is a TEST_FIXTURE). Path/class rules, not
#: filenames, so a NEW product, test or generated file is refused too.
PROHIBITED_CLASSES = (
    ("TEST_FIXTURE", re.compile(r"(?:^|/)(?:tests?|__tests__|fixtures?|e2e)/|(?:^|/)(?:test_[^/]*|conftest\.py)$"
                                r"|\.(?:test|spec)\.[jt]sx?$")),
    ("MIGRATION", re.compile(r"(?:^|/)migrations?/|\.sql$")),
    ("GENERATED_REQUIREMENTS", re.compile(r"^requirements/")),
    ("TOOL", re.compile(r"(?:^|/)(?:tools|scripts)/")),
    ("WEB_APP", re.compile(r"^(?:petcare_web|petcare-web)/")),
    ("PRODUCT_RUNTIME", re.compile(r"^(?:petcare_api|petcare_runtime)/")),
)


def source_class(path: str) -> str:
    """AUTHORITY, or the class that disqualifies `path` as a requirement source."""
    for name, rule in PROHIBITED_CLASSES:
        if rule.search(path):
            return name
    if not path.startswith(AUTHORITY_ROOT):
        return "DERIVATIVE_EVIDENCE"
    if not path.lower().endswith(AUTHORITY_SUFFIXES):
        return "NON_DOCUMENT"
    return "AUTHORITY"


FAILS_LINE = re.compile(r"^[\s*#>`_]*(?:acceptance\s*[—–-]\s*fails if|build fails if|ci fails if|fails if)",
                        re.I)
HEADING = re.compile(r"^\s*#{1,6}\s")
LEAD = re.compile(r"^[\s#*`>_]*(?:§\s*[\w.]+\s*·\s*)?")
RANGE_TAIL = re.compile(r"^\s*[–—-]\s*[0-9]")
#: What may follow the id on a HEADER line: a provenance tag, a separator, a
#: parenthesis, closing emphasis, or nothing. A line that merely OPENS with an id
#: and continues as prose ("REQ-MVC-4.3 makes break-glass …") is body text that
#: cites a requirement, not a header — treating it as one misattributes the next
#: fails-if clause to the cited requirement.
#: A compound header names further requirements by bare number
#: ("REQ-MVC-7.19 (amended) · 7.41, 7.42 (new)"); a clause under it cannot be
#: keyed to one id, so attribution is withheld.
COMPOUND = re.compile(r"(?<![\w.§-])\d+\.\d+")
HEADER_TAIL = re.compile(r"^\s*(?:\[|·|\(|\*|\.\*\*|:|$)")


def text_lines(path: Path) -> list:
    text = M.load(path)
    if path.suffix.lower() == ".docx":
        text = html.unescape(text)
    return text.splitlines()


def verify_manifest() -> None:
    for src in MANIFEST:
        cls = source_class(src["path"])
        if cls != "AUTHORITY":
            print(f"req_inventory: manifest source is not requirement authority ({cls}): {src['path']}",
                  file=sys.stderr)
            raise SystemExit(2)
        p = ROOT / src["path"]
        if not p.is_file():
            print(f"req_inventory: manifest source missing: {src['path']}", file=sys.stderr)
            raise SystemExit(2)
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        if h != src["sha256"]:
            print(f"req_inventory: manifest source changed: {src['path']} "
                  f"(pinned {src['sha256'][:12]}, now {h[:12]})", file=sys.stderr)
            raise SystemExit(2)


def _tokens(line: str) -> list:
    return list(M.IDENTIFIER.finditer(line))


def header_of(line: str, union: set):
    """(is_header, req_or_None). None with is_header=True means ambiguous."""
    lead = LEAD.match(line).end()
    distinct = sorted({m.group(0) for m in _tokens(line) if m.group(0) in union})
    if HEADING.match(line):
        return True, (distinct[0] if len(distinct) == 1 else None)
    first = _tokens(line[lead:])
    if first and first[0].start() == 0:
        tail = line[lead + first[0].end():]
        if RANGE_TAIL.match(tail):
            return True, None
        if not HEADER_TAIL.match(tail):
            return False, None
        if COMPOUND.search(tail):
            return True, None
        if len(distinct) != 1 or first[0].group(0) not in union:
            return True, None
        return True, distinct[0]
    return False, None


def main() -> int:
    verify_manifest()
    whole = M.build([ROOT / s["path"] for s in MANIFEST])
    union = set(whole["union"])
    set_a = M.build([ROOT / p for p in SET_A])

    req = {r: {"occurrences": [], "fails_if": []} for r in sorted(union)}
    raw = set()
    fails_total = 0
    unattributed_at = []
    for src in MANIFEST:
        current, since = None, 0
        seen = set()
        for n, line in enumerate(text_lines(ROOT / src["path"]), start=1):
            is_header, hreq = header_of(line, union)
            if is_header:
                current, since = hreq, 0
            else:
                since += 1
            for m in _tokens(line):
                tok = m.group(0)
                raw.add(tok)
                if tok in req and (tok, n) not in seen:
                    seen.add((tok, n))
                    a = max(0, m.start() - CONTEXT // 2)
                    req[tok]["occurrences"].append(
                        {"path": src["path"], "line": n, "context": line[a:a + CONTEXT].strip()})
            if FAILS_LINE.match(line):
                fails_total += 1
                if current is not None and since <= MAX_ATTRIBUTION_DISTANCE:
                    req[current]["fails_if"].append(
                        {"path": src["path"], "line": n, "text": line.strip()})
                else:
                    unattributed_at.append(f"{src['path']}:{n}")

    raw_less_placeholder = sorted(t for t in raw if t != "REQ-MVC-n")
    doc = {
        "schema": "mvc-req-inventory-v1",
        "grammar": "petcare_execution/tools/mvc_inventory.py (IDENTIFIER + build())",
        "sources": [{"path": s["path"], "sha256": s["sha256"]} for s in MANIFEST],
        "counts": {
            "sources": len(MANIFEST),
            "raw_distinct_tokens": whole["counts"]["raw_distinct_tokens"],
            "phantoms_removed": whole["counts"]["phantoms_removed"],
            "excluded": whole["counts"]["excluded"],
            "distinct_req": len(union),
            "req_with_fails_if": sum(1 for r in req.values() if r["fails_if"]),
            "fails_if_lines": fails_total,
            "fails_if_attributed": fails_total - len(unattributed_at),
            "fails_if_unattributed": len(unattributed_at),
        },
        "reconciliation": {
            "set_a_sources": list(SET_A),
            "set_a_union": set_a["counts"]["union"],
            "repo_reconciled_reference": 511,
            "w1_session_reference": 513,
            "raw_tokens_less_placeholder": len(raw_less_placeholder),
            "in_estate_not_in_set_a": sorted(union - set(set_a["union"])),
            "in_set_a_not_in_estate": sorted(set(set_a["union"]) - union),
            "raw_not_in_union": sorted(set(raw_less_placeholder) - union),
        },
        "excluded": whole["excluded"],
        "phantoms": whole["malformed_candidates"],
        "fails_if_unattributed_at": unattributed_at,
        "req": req,
    }
    print(json.dumps(doc, indent=1, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
