#!/usr/bin/env python3
"""
MVC-ACCEPT-AUTH-001: read-only extraction of the legacy-FR disposition table
from MVC-BRD-001 V3.0 DRAFT.

`tools/gen_register.py` cannot read V3.0 (exit 3, "no FR rows found in source
instrument"): V3.0 does not restate FR-01..FR-31 as a priority/phase table. It
carries them in ONE disposition table whose header row is
`Legacy | Requirement | Disposition | Where it lands / why`. That table is what
this tool reads, cell by cell. The canonical generator is not modified.

V3.0 assigns no per-FR priority or phase, so both are reported as absent
(None), never inferred. Rows whose Legacy cell is not an FR id (V3.0's NEW
requirements, marked "—") are counted and listed but carry no FR id.

  python3 tools/extract_v30_requirements.py   # JSON on stdout
"""
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V30 = ROOT / "governance" / "brd" / "MVC-BRD-001_V3_0_DRAFT_MyVetiCare_Master_BRD.docx"
V30_SHA256 = "b6991f0888eba781fceb2ae13a9d4c7a85f3204bbecce5b1c68bf160ff79a190"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
HEADER = ["Legacy", "Requirement", "Disposition", "Where it lands / why"]
FR_ID = re.compile(r"^FR-\d{2}$")


def _cell(tc) -> str:
    paras = ["".join(t.text or "" for t in p.iter(W + "t")) for p in tc.iter(W + "p")]
    return " ".join(p.strip() for p in paras if p.strip())


def extract(path: Path = V30) -> dict:
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != V30_SHA256:
        print(f"extract_v30_requirements: {path} sha256 {sha} != pinned {V30_SHA256}", file=sys.stderr)
        raise SystemExit(2)
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    tables = []
    for tbl in root.iter(W + "tbl"):
        rows = [[_cell(tc) for tc in tr.findall(W + "tc")] for tr in tbl.findall(W + "tr")]
        if rows and rows[0] == HEADER and any(r and FR_ID.match(r[0]) for r in rows[1:]):
            tables.append(rows)
    if len(tables) != 1:
        print(f"extract_v30_requirements: expected exactly one FR disposition table, found {len(tables)}",
              file=sys.stderr)
        raise SystemExit(2)
    fr, new = {}, []
    for r in tables[0][1:]:
        if FR_ID.match(r[0]):
            if r[0] in fr:
                print(f"extract_v30_requirements: duplicate row {r[0]}", file=sys.stderr)
                raise SystemExit(2)
            fr[r[0]] = {"title": r[1], "priority": None, "phase": None,
                        "disposition": r[2], "where_it_lands": r[3]}
        else:
            new.append({"legacy": r[0], "title": r[1], "disposition": r[2]})
    return {"source": str(path.relative_to(ROOT)), "sha256": sha, "form": "OOXML_DISPOSITION_TABLE",
            "fields_carried": ["title", "disposition"], "fields_not_carried": ["priority", "phase"],
            "fr": fr, "new_unnumbered": new}


if __name__ == "__main__":
    print(json.dumps(extract(), indent=2, sort_keys=True, ensure_ascii=False))
