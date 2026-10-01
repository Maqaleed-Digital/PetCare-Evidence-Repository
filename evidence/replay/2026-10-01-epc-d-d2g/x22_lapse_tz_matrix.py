"""X-22 timezone matrix extended to the clinical-act lapse (MVC-EPC-D-001 D2g, Sponsor ruling R17.2). Evidence script.

python3 x22_lapse_tz_matrix.py <root>

Same method as the D2f matrix (evidence/replay/2026-10-01-epc-d/x22_tz_matrix.py, not modified): per cell a fresh process
whose host zone is TZ (a host condition, never a masking override) and whose clock is pinned (date.today, datetime.now,
datetime.utcnow, time.time all to the SAME instant). Each cell runs the whole U10 file (incl. its clinical-act recheck at
:148-:178), the D2f registration tests and the D2g clinical-lapse boundary tests. Instants: 01:30, 12:00 and 23:30 Riyadh,
plus the lapse boundary on an expiry day D = 30 Sep 2026: 23:59 Riyadh on D, then 00:00, 02:59 and 03:00 Riyadh on D+1.
Exit status 0 only if all cells pass.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

TESTS = ["petcare_api/tests/test_fr05_licence.py", "petcare_api/tests/test_epc_d2f_x22_licence_calendar.py",
         "petcare_api/tests/test_epc_d2g_x22_clinical_lapse.py"]
HOST_ZONES = ["UTC", "Asia/Riyadh", "Asia/Dubai"]
INSTANTS = {
    "01:30 Riyadh": "2026-09-29T22:30:00+00:00",
    "12:00 Riyadh": "2026-09-30T09:00:00+00:00",
    "23:30 Riyadh": "2026-09-30T20:30:00+00:00",
    "23:59 Riyadh D": "2026-09-30T20:59:00+00:00",
    "00:00 Riyadh D+1": "2026-09-30T21:00:00+00:00",
    "02:59 Riyadh D+1": "2026-09-30T23:59:00+00:00",
    "03:00 Riyadh D+1": "2026-10-01T00:00:00+00:00",
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


def cell(zone, instant, root):
    with tempfile.TemporaryDirectory() as d:
        Path(d, "sitecustomize.py").write_text(SITE)
        env = {**os.environ, "TZ": zone, "X22_PINNED_INSTANT": instant,
               "PYTHONPATH": d + os.pathsep + os.environ.get("PYTHONPATH", "")}
        p = subprocess.run([sys.executable, "-m", "pytest", *TESTS, "-q", "-p", "no:cacheprovider"], cwd=root,
                           env=env, capture_output=True, text=True, timeout=900)
    tail = [l for l in p.stdout.splitlines() if " passed" in l or " failed" in l or " error" in l][-1:]
    return p.returncode, (tail[0] if tail else p.stdout[-300:])


def matrix(root):
    bad = 0
    for zone in HOST_ZONES:
        for label, instant in INSTANTS.items():
            rc, out = cell(zone, instant, root)
            bad += rc != 0
            print(f"TZ={zone:<12} {label:<17} ({instant}) {'PASS' if rc == 0 else 'FAIL'} :: {out}", flush=True)
    print(f"X22_LAPSE_TZ_MATRIX={'PASS' if bad == 0 else 'FAIL'} cells={len(HOST_ZONES) * len(INSTANTS)} failed={bad}")
    return bad


if __name__ == "__main__":
    sys.exit(1 if matrix(Path(sys.argv[1]).resolve()) else 0)
