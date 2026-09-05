#!/usr/bin/env python3
"""mvc_inventory.py — deterministic requirement-identifier inventory.

WHY THIS EXISTS
---------------
`governance/tools/mvc_content_completeness.py` in the Maqaleed portfolio repo
CONSUMES an inventory:

    universe = [r for r in json.load(open(a.inventory))['union'] if r != 'REQ-MVC-n']

Nothing in custody ever *built* that file. The inventory and the six-document
`.txt` corpus the historic run scanned were both ephemeral and never committed,
so the corrected `500` universe — and therefore `499` — has never been
reproducible from the repository. This tool closes that hole.

THE ONE RULE
------------
No identifier enters the inventory unless it was FOUND, by this parser, in a
declared source-set document. There is no padding, no seeding from a historic
aggregate, and no special case whose purpose is reaching 500 or 499. If the
measurement disagrees with history, the measurement is reported and history is
corrected — never the reverse.

THE THREE DEFECTS THIS PARSER MUST NOT REPEAT
---------------------------------------------
`MVC-CONTENT-COMPLETENESS-001 V1.0` section 1 names them, and all three produced
the withdrawn `495`:

  D-A  a two-segment identifier regex truncated three-segment ids, collapsing
       `REQ-UX-NTI-1/-2/-3` into one phantom `REQ-UX-NTI`;
  D-B  `MVC-CLOSE-001 V1.1` was absent from the source set, so `REQ-SAF-F2` and
       `REQ-SAF-F3` were never counted;
  D-C  `MVC-BRD-001 V3.2` was absent, so `REQ-DISP-AUTH-FAILCLOSED` was never
       counted.

D-A is a parser defect, prevented here by maximal-munch tokenisation plus a
standalone-occurrence test. D-B and D-C are source-set defects: no parser can
fix them, so the declared source set is an explicit, hashed input and the
known-answer controls fail if either document is missing.

THE PREFIX PROBLEM, AND WHY THE OBVIOUS FIX IS WRONG
-----------------------------------------------------
`REQ-UX-NTI` must NOT be an identifier; `REQ-UX-4` MUST be. Both are prefixes of
longer strings in the corpus. A rule deleting every identifier that has a longer
sibling would wrongly delete `REQ-UX-4`, which the governance record calls
"a real ratified requirement" that "appears standalone 15x".

The discriminator is therefore STANDALONE OCCURRENCE, not prefix-ness: a
candidate survives when at least one of its occurrences is not immediately
continued by another identifier segment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

SCHEMA_VERSION = "mvc-inventory-v1"

# ---------------------------------------------------------------------------
# Tokenisation
# ---------------------------------------------------------------------------
#
# Maximal munch. A segment is uppercase-alphanumeric (`MVC`, `UX`, `NTI`, `G1`,
# `FAILCLOSED`), or a dotted numeric path with an optional letter suffix
# (`4.49`, `5.3a`, `10.12`). The `+` over segments is what makes three-segment
# ids work; the historic two-segment regex is exactly what this replaces.
# Lowercase segments are deliberately ADMITTED here even though they are never
# valid identifiers. If the grammar refused them, `REQ-MVC-n` would tokenise as
# `REQ-MVC` and `REQ-UX-4-conformant` as `REQ-UX-4` — the metavariable and the
# prose suffix would never be SEEN, so excluding them would be vacuous, and
# `REQ-MVC` would enter the union as a phantom identifier. They must be found
# first and rejected by `classify()` second. (Controls D and E.)
# A segment may carry a dotted numeric path: `REQ-MVC-4.49`, but also
# `REQ-A.5`, `REQ-D.22`, `REQ-E.1`, `REQ-F.12`, `REQ-C.35`. Omitting the dotted
# tail from the ALPHABETIC alternative truncated all five families to `REQ-A`,
# `REQ-C`, `REQ-D`, `REQ-E`, `REQ-F` — the historic D-A defect in a new place,
# found by inspecting every single-segment survivor rather than by a green run.
_SEG = r"[A-Z][A-Z0-9]*(?:\.[0-9]+)*[a-z]?|[0-9]+(?:\.[0-9]+)*[a-z]?|[a-z]+"
IDENTIFIER = re.compile(rf"\bREQ(?:-(?:{_SEG}))+")

# `REQ-FIN-*`, `REQ-UX-{3,4,6}`, `REQ-MVC-*` name a NAMESPACE, not a
# requirement. The wildcard or brace is the discriminator, and it sits just past
# the token, so it cannot be seen from the token alone.
# A dangling hyphen counts too: Annex K writes "the `REQ-FIN-` namespace is
# entirely unoccupied". The hyphen is followed by a backtick, quote, whitespace
# or end-of-text rather than a segment, which is what distinguishes a namespace
# from a requirement.
NAMESPACE_REF = re.compile(r"^-(?:[*{]|[`'\"\s)\]]|$)")

# A trailing all-lowercase word is prose, not a segment: `REQ-UX-4-conformant`.
PROSE_SUFFIX = re.compile(r"-[a-z]{3,}$")

# A whole segment that is one lowercase letter is a metavariable: `REQ-MVC-n`.
METAVARIABLE = re.compile(r"-[a-z]$")

# `… (+114)` — a table row naming a few members and eliding the rest.
ELISION = re.compile(r"\(\+\s*(\d+)\s*\)")

# What may immediately continue an identifier. An occurrence followed by one of
# these is part of a longer identifier, so it is not a standalone occurrence.
CONTINUATION = re.compile(r"^-(?:[A-Z][A-Z0-9]*|[0-9])")


def docx_text(path: Path) -> str:
    """Extract paragraph text from a .docx.

    Paragraph boundaries become newlines so identifiers in adjacent paragraphs
    cannot be fused into one token.
    """
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8", "replace")
    xml = re.sub(r"</w:p>", "\n", xml)
    xml = re.sub(r"<w:tab[^>]*/>", " ", xml)
    return re.sub(r"<[^>]+>", "", xml)


def load(path: Path) -> str:
    """Read one source document. Aborts rather than degrading.

    D-1 in the historic run: `load()` swallowed exceptions, three of six
    documents silently vanished, and the tool produced a believable 18.4%. An
    unreadable input is a failure here, never a quietly smaller corpus.
    """
    if path.suffix.lower() == ".docx":
        return docx_text(path)
    return path.read_text(encoding="utf-8", errors="replace")


def classify(token: str) -> str:
    """concrete | metavariable | prose_suffix."""
    if METAVARIABLE.search(token):
        return "metavariable"
    if PROSE_SUFFIX.search(token):
        return "prose_suffix"
    return "concrete"


def scan(text: str) -> tuple[dict[str, int], dict[str, int], dict[str, int]]:
    """Return (standalone, total, namespace-reference) occurrence counts.

    A namespace reference is counted separately and never as standalone: an
    occurrence of `REQ-FIN` in `REQ-FIN-*` names the namespace, not a
    requirement, so it must not make `REQ-FIN` look like a real identifier.
    """
    standalone: dict[str, int] = {}
    total: dict[str, int] = {}
    namespace: dict[str, int] = {}
    for m in IDENTIFIER.finditer(text):
        token = m.group(0)
        total[token] = total.get(token, 0) + 1
        tail = text[m.end():m.end() + 24]
        if NAMESPACE_REF.match(tail):
            namespace[token] = namespace.get(token, 0) + 1
        elif not CONTINUATION.match(tail):
            standalone[token] = standalone.get(token, 0) + 1
    return standalone, total, namespace


def build(sources: list[Path]) -> dict:
    per_doc: dict[str, list[str]] = {}
    standalone_all: dict[str, int] = {}
    total_all: dict[str, int] = {}
    namespace_all: dict[str, int] = {}
    elisions: list[dict] = []
    generated_from: list[dict] = []

    for path in sources:
        if not path.is_file():
            raise SystemExit(f"ABORT: declared source not found: {path}")
        text = load(path)
        if not text.strip():
            raise SystemExit(f"ABORT: declared source produced no text: {path}")
        standalone, total, namespace = scan(text)
        for k, v in standalone.items():
            standalone_all[k] = standalone_all.get(k, 0) + v
        for k, v in total.items():
            total_all[k] = total_all.get(k, 0) + v
        for k, v in namespace.items():
            namespace_all[k] = namespace_all.get(k, 0) + v
        per_doc[path.name] = sorted(total)
        for m in ELISION.finditer(text):
            line = text[max(0, m.start() - 120):m.end()].splitlines()[-1]
            elisions.append({"document": path.name,
                             "hidden_count": int(m.group(1)),
                             "context": line.strip()[:120]})
        generated_from.append({"document": path.name,
                               "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                               "distinct_tokens": len(total)})

    # Prefix resolution: a strict segment-prefix of a longer candidate survives
    # only if it occurs standalone somewhere in the corpus.
    tokens = set(total_all)
    phantoms: list[dict] = []
    kept: set[str] = set()
    for tok in tokens:
        longer = [o for o in tokens
                  if o != tok and o.startswith(tok) and CONTINUATION.match(o[len(tok):])]
        if longer and standalone_all.get(tok, 0) == 0:
            phantoms.append({"id": tok,
                             "reason": "never occurs standalone; prefix of "
                                       + ", ".join(sorted(longer)[:4]),
                             "occurrences": total_all[tok]})
            continue
        kept.add(tok)

    excluded: list[dict] = []
    union: list[str] = []
    for tok in sorted(kept):
        kind = classify(tok)
        if namespace_all.get(tok, 0) and standalone_all.get(tok, 0) == 0:
            excluded.append({"id": tok, "reason": "namespace reference, not an identifier",
                             "evidence": f"every occurrence is followed by a wildcard or brace "
                                         f"(e.g. {tok}-*); {namespace_all[tok]} occurrences"})
        elif kind == "metavariable":
            excluded.append({"id": tok, "reason": "metavariable, not an identifier",
                             "evidence": f"final segment is a single lowercase letter; "
                                         f"{total_all[tok]} occurrences"})
        elif kind == "prose_suffix":
            excluded.append({"id": tok, "reason": "prose suffix, not an identifier",
                             "evidence": f"trailing lowercase word; {total_all[tok]} occurrences"})
        else:
            union.append(tok)

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_from": generated_from,
        "union": union,
        "per_doc": per_doc,
        "duplicates": {k: v for k, v in sorted(total_all.items())
                       if v > 1 and k in set(union)},
        "malformed_candidates": sorted(p["id"] for p in phantoms),
        "phantom_detail": phantoms,
        "elisions_detected": elisions,
        "excluded": excluded,
        "counts": {"raw_distinct_tokens": len(tokens),
                   "phantoms_removed": len(phantoms),
                   "excluded": len(excluded),
                   "union": len(union)},
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", nargs="+", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    inv = build([Path(s) for s in a.sources])
    c = inv["counts"]
    print(f"documents            : {len(inv['generated_from'])}")
    print(f"raw distinct tokens  : {c['raw_distinct_tokens']}")
    print(f"phantoms removed     : {c['phantoms_removed']}  {inv['malformed_candidates']}")
    print(f"excluded             : {c['excluded']}  {[e['id'] for e in inv['excluded']]}")
    print(f"UNION (universe)     : {c['union']}")
    print(f"elisions detected    : {len(inv['elisions_detected'])}")
    if a.out:
        Path(a.out).write_text(json.dumps(inv, indent=1) + "\n", encoding="utf-8")
        print(f"written              : {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
