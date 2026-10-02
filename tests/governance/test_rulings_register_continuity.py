"""R18.5 (MVC-EPC-D-001): rulings-register continuity. Every ruling R1..R<highest> is discoverable through the index
evidence/rulings/INDEX.md and occurs EXACTLY ONCE across the indexed register files' tables (no gap, no duplicate); every
indexed file exists and matches its recorded sha256 (register files are never edited)."""
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "evidence" / "rulings" / "INDEX.md"
ROW = re.compile(r"^\| (\d+) \| `([^`]+)` \| ([^|]+) \| ([0-9a-f]{64}) \|")
RULING = re.compile(r"\bR(\d+)(?![.\d])(?:\s*[–-]\s*R(\d+)(?![.\d]))?")   # R16 or R1–R9, never a sub-section R16.4


def _index():
    rows = [m.groups() for m in map(ROW.match, INDEX.read_text(encoding="utf-8").splitlines()) if m]
    assert rows, "the index lists no register file"
    return rows


def _rulings_in(register: Path) -> list:
    """Ruling numbers named in the FIRST cell of each register-table row (the IDENTIFIER column)."""
    found = []
    for line in register.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| ") or line.startswith("| IDENTIFIER") or line.startswith("|---"):
            continue
        first = line.split("|")[1]
        for a, b in RULING.findall(first):
            found.extend(range(int(a), int(b or a) + 1))
    return found


def test_the_index_is_chronological_and_every_file_matches_its_hash():
    rows = _index()
    assert [int(r[0]) for r in rows] == list(range(1, len(rows) + 1))
    for _n, path, _range, sha in rows:
        f = ROOT / path
        assert f.is_file(), path
        assert hashlib.sha256(f.read_bytes()).hexdigest() == sha, f"{path} changed after it was indexed"


def test_every_ruling_occurs_exactly_once_with_no_gap():
    seen = {}
    for _n, path, _range, _sha in _index():
        for r in _rulings_in(ROOT / path):
            seen.setdefault(r, []).append(path)
    duplicates = {r: p for r, p in seen.items() if len(p) > 1}
    assert duplicates == {}, f"rulings listed more than once: {duplicates}"
    highest = max(seen)
    missing = [r for r in range(1, highest + 1) if r not in seen]
    assert missing == [], f"rulings with no register entry: {missing}"
    assert highest >= 18


def test_each_index_row_states_the_range_its_file_actually_holds():
    for _n, path, declared, _sha in _index():
        nums = sorted(set(_rulings_in(ROOT / path)))
        a, b = RULING.search(declared).groups()
        assert nums == list(range(int(a), int(b or a) + 1)), (path, declared, nums)
