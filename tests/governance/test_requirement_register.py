"""MVC-REQREG-001 standing controls for the canonical requirement register spine."""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True).strip())
REGISTER = ROOT / "requirements" / "register.yaml"
GENERATOR = ROOT / "tools" / "gen_register.py"


def _text():
    return REGISTER.read_text(encoding="utf-8")


def _field(name):
    m = re.search(rf"^  {name}: (.+)$", _text(), re.M)
    assert m, f"register header lacks {name}"
    return m.group(1).strip()


def test_register_is_bound_to_brd_bytes():
    brd = ROOT / _field("path")
    assert brd.is_file(), f"BRD in custody not found at {brd}"
    assert hashlib.sha256(brd.read_bytes()).hexdigest() == _field("sha256")


def test_register_regenerates_byte_identically():
    out = subprocess.run(
        [sys.executable, str(GENERATOR), _field("path")],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout
    assert out == _text(), "register drifted from its generator or source BRD"


def test_fr_identifiers_unique_and_contiguous():
    ids = re.findall(r"^  - id: (FR-\d{2})$", _text(), re.M)
    assert len(ids) == len(set(ids))
    nums = sorted(int(i[3:]) for i in ids)
    assert nums == list(range(1, len(nums) + 1))
    assert int(_field("fr_count")) == len(ids)


def test_phase1_high_count_matches_listed_ids():
    m = re.search(r"^  phase1_high_ids: \[(.*)\]$", _text(), re.M)
    assert m, "register header lacks phase1_high_ids"
    ids = [s.strip() for s in m.group(1).split(",") if s.strip()]
    assert int(_field("phase1_high_count")) == len(ids)


def test_status_is_never_authored():
    statuses = set(re.findall(r"^    status: (\S+)$", _text(), re.M))
    assert statuses == {"UNASSESSED"}, statuses
