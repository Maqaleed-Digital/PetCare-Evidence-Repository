"""X-29 report-month timezone matrix (MVC-EPC-D-001 D2g, Sponsor ruling R18.1). Evidence script.

python3 x29_month_tz_matrix.py <root> [--expect-utc-signature]

Per cell (host TZ x pinned instant; method of x22_lapse_tz_matrix.py), runs the clock-driven X-29 test and the amended frozen
FR-30 antimicrobial test (its :122 assertion reads the clock). Instants straddle the 1 November 2026 Riyadh month boundary:
23:59 Riyadh on 31 Oct, then 00:00, 01:30, 02:59 and 03:00 Riyadh on 1 Nov, and 12:00 on 1 Nov.
Default: exit 0 only if every cell passes. --expect-utc-signature: exit 0 only if exactly the cells whose Riyadh and UTC
months differ (00:00-02:59 Riyadh on the 1st) fail — each on the report-month assertions only — and every other cell passes.
"""
import importlib.util
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("x22m", HERE / "x22_lapse_tz_matrix.py")
x22m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(x22m)
TESTS = ["petcare_api/tests/test_epc_d2g_x29_report_month.py::test_the_report_month_now_is_the_riyadh_month",
         "petcare_api/tests/test_fr30_compliance.py::test_antimicrobial_prescribing_aggregates_by_agent_class_species_practitioner_and_period"]
INSTANTS = {
    "23:59 Riyadh 31 Oct": "2026-10-31T20:59:00+00:00",
    "00:00 Riyadh 1 Nov": "2026-10-31T21:00:00+00:00",
    "01:30 Riyadh 1 Nov": "2026-10-31T22:30:00+00:00",
    "02:59 Riyadh 1 Nov": "2026-10-31T23:59:00+00:00",
    "03:00 Riyadh 1 Nov": "2026-11-01T00:00:00+00:00",
    "12:00 Riyadh 1 Nov": "2026-11-01T09:00:00+00:00",
}
DISCRIMINATING = {"00:00 Riyadh 1 Nov", "01:30 Riyadh 1 Nov", "02:59 Riyadh 1 Nov"}
EXPECTED_UTC_FAILURES = {"test_the_report_month_now_is_the_riyadh_month",
                         "test_antimicrobial_prescribing_aggregates_by_agent_class_species_practitioner_and_period"}


def cell(zone, instant, root):
    with tempfile.TemporaryDirectory() as d:
        Path(d, "sitecustomize.py").write_text(x22m.SITE)
        env = {**os.environ, "TZ": zone, "X22_PINNED_INSTANT": instant,
               "PYTHONPATH": d + os.pathsep + os.environ.get("PYTHONPATH", "")}
        p = subprocess.run([sys.executable, "-m", "pytest", *TESTS, "-q", "-p", "no:cacheprovider", "-rf"], cwd=root, env=env,
                           capture_output=True, text=True, timeout=900)
    failed = {l.split("::")[-1].split(" ")[0] for l in p.stdout.splitlines() if l.startswith("FAILED")}
    month = [l for l in p.stdout.splitlines() if "regulated report month" in l or "period" in l][:1]
    return p.returncode, failed, month


def main(root, expect_utc):
    bad = 0
    for zone in x22m.HOST_ZONES:
        for label, instant in INSTANTS.items():
            rc, failed, why = cell(zone, instant, root)
            ok = (rc != 0 and failed == EXPECTED_UTC_FAILURES) if (expect_utc and label in DISCRIMINATING) else rc == 0
            bad += not ok
            print(f"TZ={zone:<12} {label:<20} {'FAIL' if rc else 'PASS'} failed={sorted(failed)} {'as-expected' if ok else 'UNEXPECTED'} {why}",
                  flush=True)
    mode = "UTC_SIGNATURE" if expect_utc else "GOVERNED"
    print(f"X29_MONTH_TZ_MATRIX[{mode}]={'PASS' if bad == 0 else 'FAIL'} cells={len(x22m.HOST_ZONES) * len(INSTANTS)} unexpected={bad}")
    return bad


if __name__ == "__main__":
    sys.exit(1 if main(Path(sys.argv[1]).resolve(), "--expect-utc-signature" in sys.argv) else 0)
