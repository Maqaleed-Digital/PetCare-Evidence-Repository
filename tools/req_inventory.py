#!/usr/bin/env python3
"""
MVC-ACCEPT-AUTH-001 REQ-* estate inventory.

  python3 tools/req_inventory.py > requirements/authority/req_inventory.json

WHAT IT READS. A FROZEN manifest of every tracked file that carried a REQ-*
token when this lane measured the estate (mechanical discovery: `git grep -I`
over text files plus paragraph extraction of every tracked .docx). Each source
is pinned by sha256. A missing or changed source exits 2: an inventory computed
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

# Frozen at measurement, 2026-09-24, base 413554c7. Regenerate deliberately.
MANIFEST = [
    {"path": "evidence/receipts/2026-09-13-option-a-pilot-substrate.md", "sha256": "91276c413f0eceea7a260ff394562fdf5fa3375d22b6f9cd5537b28731b9cdb1"},
    {"path": "evidence/traceability/OPTION_A_FR14_FR27_BRIDGE.md", "sha256": "568524a8464366b7983da6c94237b7e9239d9cc712484ba85b38619a226b55a0"},
    {"path": "petcare_api/main.py", "sha256": "0aa218e475cccae1fc602538b37b6d2c8f8b5701195cd95e0c622e752adfb121"},
    {"path": "petcare_api/tests/test_dispensing_fail_closed.py", "sha256": "6c4632e4d4ec99bcda2a2ff7fca34a2887545f5b772f2b6235c97a32c1551466"},
    {"path": "petcare_api/tests/test_option_a_workflow.py", "sha256": "0b29bb6bdd8e8aed7735eb704c0ec2f52ae5d1382d29cab176ec745b113a6067"},
    {"path": "petcare_execution/AUTHORITY/AUTHORITY_CANDIDATES.md", "sha256": "4bbe4b5a295678e4f5b93207593e9cfc5a3fc6f774e990995cdb6b0ce2990ca9"},
    {"path": "petcare_execution/AUTHORITY/AUTHORITY_INGESTION_SCHEMA.json", "sha256": "65ab86a75263b25f97dc0f3a3508147bf32e820d15baedbf4dd216c7095ee5ed"},
    {"path": "petcare_execution/AUTHORITY/AUTHORITY_INGESTION_SPEC.md", "sha256": "5cd4b2f48498f33477589708fc23d7a6ca66177cf768172f3d150e1cab03455d"},
    {"path": "petcare_execution/AUTHORITY/MVC-LINEAGE/DENOMINATOR_RECONCILIATION.md", "sha256": "b58901c9f65582fed21ae54dea18602d0a2909b5178a3b58b263bb0aa397add3"},
    {"path": "petcare_execution/AUTHORITY/MVC-LINEAGE/MVC-V3_3-APPENDIX-T-AUTHORING-PLAN.md", "sha256": "540ecfb3c3edb0ba6ed6a086ab533337cba2f787ec10152dda4f7c267703e031"},
    {"path": "petcare_execution/AUTHORITY/MVC-LINEAGE/inventory.json", "sha256": "51123d68865bfb9fa146c238c95758e2376b072bb6ddb823ad32ff0f055b46d1"},
    {"path": "petcare_execution/AUTHORITY/MVC-LINEAGE/sources/MVC-BRD-001_V3_1_CANDIDATE_MyVetiCare_Master_BRD.docx", "sha256": "024501e639ba3b6d28c76c5f05072e78dfe8f26b5ee9c79258c2a21141078792"},
    {"path": "petcare_execution/AUTHORITY/MVC-LINEAGE/sources/MVC-BRD-001_V3_2_EXECUTION_BASELINE_CANDIDATE.md", "sha256": "32f5366925128ca8f1332a412b253b2a1b797baf08cf6dd5777fac118efc287d"},
    {"path": "petcare_execution/AUTHORITY/MVC-LINEAGE/sources/MVC-CLOSE-001_V1_1_PhaseA_Execution_Boundary.docx", "sha256": "27a07179d911e8ff885a5020dee4832ba9c939b1a9758cb0ad5207d4401c85bc"},
    {"path": "petcare_execution/AUTHORITY/MVC-LINEAGE/sources/MVC-GAP-001_V1_7_Ledger_Amendment_ARCH01_Closed_ARCH05_Allocated.md", "sha256": "e8d221b4beb82708b14d690dd0202f7a3c8e4b8a030cb6281cff5814e98f3ff1"},
    {"path": "petcare_execution/AUTHORITY/MVC-LINEAGE/sources/MVC-SPEC-001_V3_0_Execution_Specification_Completion_Pass_Tranches_1_to_3.docx", "sha256": "a3f2fb2c2a4eb709187dccbee7f045a0b48e0d8364c4816de8f680e93b0a3a19"},
    {"path": "petcare_execution/AUTHORITY/MVC-LINEAGE/sources/MVC-SPEC-001_V3_1_Annex_K_Split_Taxpayer_Requirements.md", "sha256": "058356cc916f9a274315bf19e6e6cbb0d9a20e0c2bc69d471cf94a87d6461c3b"},
    {"path": "petcare_execution/EVIDENCE/MVC-AUTHORITY-INGESTION/20260904T140123Z/AUTHORITY_DISCOVERY.md", "sha256": "4bbe4b5a295678e4f5b93207593e9cfc5a3fc6f774e990995cdb6b0ce2990ca9"},
    {"path": "petcare_execution/EVIDENCE/MVC-AUTHORITY-INGESTION/20260904T140123Z/NOTION_UPDATE_BLOCK.md", "sha256": "00d586deaa48277dfb5d094a5cd5bcadf8a686f9013fd2d9a0852a4620b24401"},
    {"path": "petcare_execution/EVIDENCE/MVC-AUTHORITY-INGESTION/20260904T140123Z/REQUIREMENT_MEASUREMENT.md", "sha256": "2edea1dccbc3f39ff4c8a5e46261103430f7d0f17d148b43133fd8390330aa6d"},
    {"path": "petcare_execution/EVIDENCE/MVC-AUTHORITY-INGESTION/20260904T140123Z/RUN_RECEIPT.md", "sha256": "3b3862836037b5add306ca3449338a4985b3c4314b4f96abfefa9c4e25b3f31b"},
    {"path": "petcare_execution/EVIDENCE/MVC-LINEAGE-REPAIR/20260904T215919Z/DENOMINATOR_RECONCILIATION.md", "sha256": "b58901c9f65582fed21ae54dea18602d0a2909b5178a3b58b263bb0aa397add3"},
    {"path": "petcare_execution/EVIDENCE/MVC-LINEAGE-REPAIR/20260904T215919Z/MVC-V3_3-APPENDIX-T-AUTHORING-PLAN.md", "sha256": "540ecfb3c3edb0ba6ed6a086ab533337cba2f787ec10152dda4f7c267703e031"},
    {"path": "petcare_execution/EVIDENCE/MVC-LINEAGE-REPAIR/20260904T215919Z/NOTION_UPDATE_BLOCK.md", "sha256": "ed85833549f7030ed7e20724a8f2496f5fd5f32a01a7c5f15a85618b46127c52"},
    {"path": "petcare_execution/EVIDENCE/MVC-LINEAGE-REPAIR/20260904T215919Z/RUN_RECEIPT.md", "sha256": "67f78e3ce37eddcc8b37c863a93b03c3cd82e6c318daa1d3d1a9e45907d2489c"},
    {"path": "petcare_execution/EVIDENCE/MVC-LINEAGE-REPAIR/20260904T215919Z/inventory.json", "sha256": "51123d68865bfb9fa146c238c95758e2376b072bb6ddb823ad32ff0f055b46d1"},
    {"path": "petcare_execution/EVIDENCE/MVC-POST-PORT-07-10/20260904T125855Z/AUTHORITY_RESIDENCY_GAP.md", "sha256": "372a9306b5c2020bdde764a52b07f8ff89fb410403a19c9a75417c6f34bf1aa2"},
    {"path": "petcare_execution/EVIDENCE/MVC-W0H/20260907T095803Z/RUN_RECEIPT.md", "sha256": "d75e9bca74e947b4352514edc46d852bbc1e40d92a0bb47f979886e0404be28b"},
    {"path": "petcare_execution/EVIDENCE/MVC-W0J/20260907T103127Z/RUN_RECEIPT.md", "sha256": "309c5717c80c0b56f0f058feb57da01f8d27e7b52632558359c22eecc73a40e3"},
    {"path": "petcare_execution/GOVERNANCE/CANONICAL_REPOSITORY_AUTHORITY/CROSS_REPOSITORY_TRACEABILITY.json", "sha256": "7afae525237ce87930aaa2ded75227e031dc45885448660bf59312a7086de5c0"},
    {"path": "petcare_execution/GOVERNANCE/CANONICAL_REPOSITORY_AUTHORITY/CROSS_REPOSITORY_TRACEABILITY.md", "sha256": "89b99161cdebb31cfa7c77fef63df3e5b1f1d3d979074e75a57557912a1fe75c"},
    {"path": "petcare_execution/GOVERNANCE/MVC-W0A-INCIDENT-001/NOTION_CORRECTION_QUEUE.md", "sha256": "08e4f391b99ad4864d28b1748479a2bdc10c9f55d30febd6aa67c9508a352963"},
    {"path": "petcare_execution/GOVERNANCE/MVC-W0F-ENGINEERING-HANDOFF-001/MVC-W0F-DATA-STORE-DECISION-001.md", "sha256": "e66cec6c9d297c298f0df9eaa1ecb125716f79c3be20938caed3ef2d7829243a"},
    {"path": "petcare_execution/tools/mvc_inventory.py", "sha256": "050d69211750f24079a29cc230dc31a7c07427641da39e0af16946f26ba51f93"},
    {"path": "petcare_runtime/migrations/0029_w0h_seller_identity.sql", "sha256": "706880efd7dbf8927f4e765d21e3bf0dfc0cfd274b5561081fbb91848676bf79"},
    {"path": "petcare_web/__tests__/pharmacy-queue.test.tsx", "sha256": "927afb457aaed3196613e5996da4c153a8b7036b1c8b13c0c32e854d8190763d"},
    {"path": "petcare_web/app/pharmacy/page.tsx", "sha256": "51318920f5b1f7ca7b434e9ffd991b4b7017cc80f040eabd09eb0b550dcea4f4"},
    {"path": "requirements/bindings.json", "sha256": "a074e74c758316d3606ed46f718f53f75b8fe746c04044899cda14296e300a82"},
    {"path": "scripts/governance/cross_repository_traceability.py", "sha256": "6dfa1f86b4cd7729d3275159cced6e65d7c34fd44225f98ee2aef037c389ae6a"},
    {"path": "tests/governance/test_authority_residency.py", "sha256": "827ee85e7e3e1da53265397606cffae9b8ab66c07e5cef5562695aca4d0a351a"},
    {"path": "tests/governance/test_migration_invariants.py", "sha256": "ebdf550d08734e701b0106647878602f08f2301904d9fd47881d522ea32c082c"},
    {"path": "tests/governance/test_mvc_inventory.py", "sha256": "ae7ccb886d98b9100e82dc0e6edf100815868aa4cede79f282aef60fd6e7417f"},
    {"path": "tests/governance/test_seller_identity_write_authority.py", "sha256": "5ce8e8e5032721d1cb6bcb93c2a9aff0bb19e901658e011f073efb0280752a40"},
]

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
