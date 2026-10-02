"""X-22 cell-sensitive lapse probe matrix (MVC-EPC-D-001 D2g; finding D2G-X22-PERTURBATION-BREADTH, Sponsor R18 step 2).

python3 x22_lapse_probe_matrix.py <root> [--expect-utc-signature]

Same host zones, pinned instants and pinning method as x22_lapse_tz_matrix.py, but each cell runs ONLY the cell-sensitive probe
(petcare_api/tests/test_epc_d2g_x22_cell_probe.py), whose outcome depends on the cell's own Riyadh wall clock. Default: exit 0
only if every cell passes (the governed Asia/Riyadh rule). --expect-utc-signature (used to prove a UTC-reverted rule is caught
for the RIGHT reason): exit 0 only if exactly the cells whose Riyadh and UTC dates differ (00:00–02:59 Riyadh) fail and every
other cell passes.
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
PROBE = "petcare_api/tests/test_epc_d2g_x22_cell_probe.py"
DISCRIMINATING = {"01:30 Riyadh", "00:00 Riyadh D+1", "02:59 Riyadh D+1"}


def cell(zone, instant, root):
    with tempfile.TemporaryDirectory() as d:
        Path(d, "sitecustomize.py").write_text(x22m.SITE)
        env = {**os.environ, "TZ": zone, "X22_PINNED_INSTANT": instant,
               "PYTHONPATH": d + os.pathsep + os.environ.get("PYTHONPATH", "")}
        p = subprocess.run([sys.executable, "-m", "pytest", PROBE, "-q", "-p", "no:cacheprovider", "-rf"], cwd=root, env=env,
                           capture_output=True, text=True, timeout=600)
    failed = [l.split("::")[-1].split(" ")[0] for l in p.stdout.splitlines() if l.startswith("FAILED")]
    return p.returncode, failed


def main(root, expect_utc):
    bad = 0
    for zone in x22m.HOST_ZONES:
        for label, instant in x22m.INSTANTS.items():
            rc, failed = cell(zone, instant, root)
            want_fail = expect_utc and label in DISCRIMINATING
            ok = (rc != 0 and failed == ["test_a_clinical_act_now_follows_the_riyadh_calendar[riyadh-yesterday-False]"]) if want_fail else rc == 0
            bad += not ok
            print(f"TZ={zone:<12} {label:<17} {'FAIL' if rc else 'PASS'} failed={failed} {'as-expected' if ok else 'UNEXPECTED'}",
                  flush=True)
    mode = "UTC_SIGNATURE" if expect_utc else "GOVERNED"
    print(f"X22_LAPSE_PROBE_MATRIX[{mode}]={'PASS' if bad == 0 else 'FAIL'} cells={len(x22m.HOST_ZONES) * len(x22m.INSTANTS)} unexpected={bad}")
    return bad


if __name__ == "__main__":
    sys.exit(1 if main(Path(sys.argv[1]).resolve(), "--expect-utc-signature" in sys.argv) else 0)
