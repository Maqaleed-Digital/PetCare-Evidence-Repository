#!/usr/bin/env python3
"""
MVC-REQREG-001 generator: canonical requirement register SPINE derived from the BRD.

The spine is fully generated and bound to the BRD by SHA-256. It carries no authored
content. Bindings live in requirements/bindings.json; status is asserted by
tools/check_register.py into requirements/status.json. Status in the spine is always
UNASSESSED: the spine never assesses.

OOXML sources are read from table rows (one cell per column) and from paragraphs whose
columns are separated by run-level tabs. Tab-stop definitions are never read as columns.

Usage (repository root):
  python3 tools/gen_register.py <repo-relative-BRD-path> > requirements/register.yaml
"""
import hashlib
import io
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

FR_ROW = re.compile(r"^(FR-\d{2})\t(.+?)\t(High|Medium|Low)\t([123])$")
NFR_ROW = re.compile(r"^(NFR-\d{2})\t(.+?)\t(.+)$")
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def _run_text(el):
    out = []
    for r in el.iter(W + "r"):
        for c in r:
            if c.tag == W + "t":
                out.append(c.text or "")
            elif c.tag == W + "tab":
                out.append("\t")
    return "".join(out)


def extract(raw: bytes):
    if raw[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            root = ET.fromstring(z.read("word/document.xml"))
        lines = []
        for tr in root.iter(W + "tr"):
            cells = [_run_text(tc).strip() for tc in tr.findall(W + "tc")]
            lines.append("\t".join(cells))
        for p in root.iter(W + "p"):
            lines.append(_run_text(p).strip())
        return "OOXML", lines
    return "TEXT", [ln.rstrip() for ln in raw.decode("utf-8").splitlines()]


def main(path: str) -> int:
    raw = open(path, "rb").read()
    form, lines = extract(raw)
    fr, nfr, seen = [], [], set()
    for line in lines:
        m = FR_ROW.match(line)
        if m:
            if m.group(1) in seen:
                sys.stderr.write(f"duplicate requirement id {m.group(1)}\n")
                return 2
            seen.add(m.group(1))
            fr.append(m.groups())
            continue
        m = NFR_ROW.match(line)
        if m:
            if m.group(1) in seen:
                sys.stderr.write(f"duplicate requirement id {m.group(1)}\n")
                return 2
            seen.add(m.group(1))
            nfr.append(m.groups())
    if not fr:
        sys.stderr.write("no FR rows found in source instrument\n")
        return 3
    p1h = [r[0] for r in fr if r[2] == "High" and r[3] == "1"]
    out = [
        "# MVC-REQREG-001 canonical requirement register (spine)",
        "# GENERATED: do not hand-edit. Regenerate with tools/gen_register.py.",
        "# Bindings: requirements/bindings.json. Asserted status: requirements/status.json.",
        "source_instrument:",
        f"  path: {path}",
        f"  sha256: {hashlib.sha256(raw).hexdigest()}",
        f"  form: {form}",
        f"  fr_count: {len(fr)}",
        f"  nfr_count: {len(nfr)}",
        f"  phase1_high_count: {len(p1h)}",
        f"  phase1_high_ids: [{', '.join(p1h)}]",
        "",
        "requirements:",
    ]
    for rid, title, prio, phase in fr:
        out += [
            f"  - id: {rid}",
            f"    title: {json.dumps(title.strip(), ensure_ascii=False)}",
            f"    priority: {prio}",
            f"    phase: {int(phase)}",
            "    status: UNASSESSED",
        ]
    out += ["", "non_functional:"]
    for rid, title, target in nfr:
        out += [
            f"  - id: {rid}",
            f"    title: {json.dumps(title.strip(), ensure_ascii=False)}",
            f"    target: {json.dumps(target.strip(), ensure_ascii=False)}",
            "    status: UNASSESSED",
        ]
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
