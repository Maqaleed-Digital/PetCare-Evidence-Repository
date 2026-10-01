"""X-22 timezone matrix (MVC-EPC-D-001 D2f, Sponsor ruling R16.3 C). Evidence script.

python3 x22_tz_matrix.py <root>

For every host zone in HOST_ZONES and every pinned instant in INSTANTS, runs the WHOLE amended U10 file
(test_fr05_licence.py) and the X-22 acceptance tests in a fresh subprocess. The host zone is the process's TZ — a
host condition, set per cell, never a masking override inside the suite. The clock is pinned (date.today, datetime.now,
datetime.utcnow, time.time all to the SAME instant, the D2d R13.7 method), so U10's own "today"/"yesterday" fixtures and
the product's licence rule are exercised at that instant. Prints one line per cell; exit status 0 only if all cells pass.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

TESTS = ["petcare_api/tests/test_fr05_licence.py", "petcare_api/tests/test_epc_d2f_x22_licence_calendar.py"]
HOST_ZONES = ["UTC", "Asia/Riyadh", "Asia/Dubai"]
INSTANTS = {
    "01:30 Asia/Riyadh": "2026-09-29T22:30:00+00:00",   # Riyadh date 30 Sep, UTC date 29 Sep, Dubai 02:30 30 Sep
    "12:00 Asia/Riyadh": "2026-09-30T09:00:00+00:00",   # all three calendars agree
    "23:30 Asia/Riyadh": "2026-09-30T20:30:00+00:00",   # Riyadh/UTC 30 Sep, Dubai already 1 Oct (00:30)
}

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


def cell(zone: str, instant: str, root: Path) -> tuple:
    with tempfile.TemporaryDirectory() as d:
        Path(d, "sitecustomize.py").write_text(SITE)
        env = {**os.environ, "TZ": zone, "X22_PINNED_INSTANT": instant,
               "PYTHONPATH": d + os.pathsep + os.environ.get("PYTHONPATH", "")}
        p = subprocess.run([sys.executable, "-m", "pytest", *TESTS, "-q", "-p", "no:cacheprovider"], cwd=root,
                           env=env, capture_output=True, text=True, timeout=900)
    tail = [l for l in p.stdout.splitlines() if " passed" in l or " failed" in l or " error" in l][-1:]
    return p.returncode, (tail[0] if tail else p.stdout[-300:])


def matrix(root: Path) -> int:
    bad = 0
    for zone in HOST_ZONES:
        for label, instant in INSTANTS.items():
            rc, out = cell(zone, instant, root)
            bad += rc != 0
            print(f"TZ={zone:<12} {label} ({instant}) {'PASS' if rc == 0 else 'FAIL'} :: {out}", flush=True)
    print(f"X22_TZ_MATRIX={'PASS' if bad == 0 else 'FAIL'} cells={len(HOST_ZONES) * len(INSTANTS)} failed={bad}")
    return bad


if __name__ == "__main__":
    sys.exit(1 if matrix(Path(sys.argv[1]).resolve()) else 0)
