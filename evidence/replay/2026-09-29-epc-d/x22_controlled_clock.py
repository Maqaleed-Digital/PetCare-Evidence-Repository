"""X-22 reproduction under a CONTROLLED clock (MVC-EPC-D-001 D2d, Sponsor ruling R13.7). Diagnostic only.

python3 x22_controlled_clock.py <root>

Runs the FROZEN U10 test (test_fr05_licence.py::test_a_veterinarian_cannot_register_without_licence_details), unmodified,
in a subprocess whose clock is pinned to one instant. TZ is NOT set or overridden: the host's own zone is used, and the
script refuses to run under TZ=UTC or on a host whose local offset is not +03:00 (Asia/Riyadh), because the defect is the
gap between the local calendar and the UTC calendar. Production code is untouched. Only `date.today()` / `datetime.now()`
/ `datetime.utcnow()` / `time.time()` are pinned, all to the SAME instant, so every calendar the code reads agrees with
every other one — the pin moves the clock, it does not change timezone semantics.

Two instants are run: one inside 00:00–03:00 Riyadh (the claimed defect window) and a control outside it. The defect is
REPRODUCED only if the window run fails AND the control passes (discrimination); anything else is NOT_REPRODUCED.
"""
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

R = Path(sys.argv[1]).resolve()
TEST = "petcare_api/tests/test_fr05_licence.py::test_a_veterinarian_cannot_register_without_licence_details"
WINDOW = "2026-09-29T22:30:00+00:00"   # = 2026-09-30 01:30 Asia/Riyadh: local date 30 Sep, UTC date 29 Sep
CONTROL = "2026-09-30T09:00:00+00:00"  # = 2026-09-30 12:00 Asia/Riyadh: local and UTC dates agree

SITE = '''
import datetime as _dt, os as _os, time as _time
_AT = _dt.datetime.fromisoformat(_os.environ["X22_PINNED_INSTANT"])
_EPOCH = _AT.timestamp()
_real_date, _real_datetime = _dt.date, _dt.datetime
class _PinnedDate(_real_date):
    @classmethod
    def today(cls):
        l = _AT.astimezone()
        return cls(l.year, l.month, l.day)
class _PinnedDateTime(_real_datetime):
    @classmethod
    def now(cls, tz=None):
        v = _AT.astimezone(tz) if tz is not None else _AT.astimezone().replace(tzinfo=None)
        return cls(v.year, v.month, v.day, v.hour, v.minute, v.second, v.microsecond, v.tzinfo)
    @classmethod
    def utcnow(cls):
        v = _AT.astimezone(_dt.timezone.utc)
        return cls(v.year, v.month, v.day, v.hour, v.minute, v.second, v.microsecond)
    @classmethod
    def today(cls):
        return cls.now()
_dt.date, _dt.datetime = _PinnedDate, _PinnedDateTime
_time.time = lambda: _EPOCH
'''


def run(instant: str) -> tuple:
    with tempfile.TemporaryDirectory() as d:
        Path(d, "sitecustomize.py").write_text(SITE)
        env = {**os.environ, "X22_PINNED_INSTANT": instant, "PYTHONPATH": d + os.pathsep + os.environ.get("PYTHONPATH", "")}
        env.pop("TZ", None)
        p = subprocess.run([sys.executable, "-m", "pytest", TEST, "-q", "-p", "no:cacheprovider"], cwd=R, env=env,
                           capture_output=True, text=True, timeout=600)
    tail = [l for l in p.stdout.splitlines() if "passed" in l or "failed" in l or "error" in l][-1:]
    why = [l for l in p.stdout.splitlines() if l.startswith("E ")][:4]     # the failing assertion, if any
    return p.returncode, tail + why


if os.environ.get("TZ", "").upper() in ("UTC", "UTC0", "ETC/UTC", "GMT"):
    raise SystemExit("refused: TZ=UTC masking is prohibited (R13.7)")
offset = time.strftime("%z")
if offset != "+0300":
    raise SystemExit(f"refused: host local offset is {offset}, not +0300 (Asia/Riyadh); the boundary cannot be exercised")
print(f"host TZ env={os.environ.get('TZ', '<unset>')} local offset={offset}")
w_rc, w_out = run(WINDOW)
c_rc, c_out = run(CONTROL)
print(f"WINDOW  {WINDOW} (01:30 Asia/Riyadh) rc={w_rc} {w_out}")
print(f"CONTROL {CONTROL} (12:00 Asia/Riyadh) rc={c_rc} {c_out}")
print("X22=" + ("REPRODUCED" if w_rc != 0 and c_rc == 0 else "NOT_REPRODUCED"))
