"""MVC-EPC-D-001 D2g — R18 perturbations: the cell-specific X-22 lapse probe (R18 step 2), X-29 report month (R18.1) and the
rulings-register index (R18.5). python3 perturb_epc_d_d2g_r18.py <root>. ARMED = the named evidence FAILS."""
import os
import subprocess
import sys
R = sys.argv[1].rstrip("/") + "/"
PY = lambda t: ["python3", "-m", "pytest", t, "-q", "-p", "no:cacheprovider"]
LIC, M, IDX = "petcare_api/licences.py", "petcare_api/main.py", "evidence/rulings/INDEX.md"
CONT = "tests/governance/test_rulings_register_continuity.py"
PERIOD_RIYADH = '"period": ksa_date(rx.issued_at).strftime("%Y-%m")})'
PERIOD_UTC = '"period": rx.issued_at.strftime("%Y-%m")})'
idx = open(R + IDX).read().splitlines()
ROW_R17 = next(l for l in idx if "rulings-register-c3.md" in l) + "\n"
ROW_R16 = next(l for l in idx if "2026-10-01-epc-d-rulings-register.md" in l)
ROW_R18 = next(l for l in idx if "rulings-register-c4.md" in l) + "\n"
P = [
 ("P-D2G-X22-LAPSE-UTC-PROBE-MATRIX", [(LIC, "time(0), tzinfo=LICENCE_CALENDAR_ZONE)", "time(0), tzinfo=timezone.utc)")],
  ["python3", "evidence/replay/2026-10-01-epc-d-d2g/x22_lapse_probe_matrix.py", "."]),
 ("P-D2G-X29-REPORT-MONTH-UTC", [(M, PERIOD_RIYADH, PERIOD_UTC)],
  PY("petcare_api/tests/test_epc_d2g_x29_report_month.py::test_the_month_boundary")),
 ("P-D2G-X29-REPORT-MONTH-UTC-MATRIX", [(M, PERIOD_RIYADH, PERIOD_UTC)],
  ["python3", "evidence/replay/2026-10-01-epc-d-d2g/x29_month_tz_matrix.py", "."]),
 ("P-D2G-R18-INDEX-ROW-REMOVED", [(IDX, ROW_R17, "")], PY(CONT)),
 ("P-D2G-R18-INDEX-DUPLICATE-REGISTER", [(IDX, ROW_R18, ROW_R18 + ROW_R16.replace("| 2 |", "| 5 |", 1) + "\n")], PY(CONT)),
 ("P-D2G-R18-INDEX-HASH-ALTERED", [(IDX, ROW_R16, ROW_R16.replace(ROW_R16.split("|")[4].strip(), "0" * 64))], PY(CONT)),
]
res = []
for pid, edits, cmd in P:
    files = sorted({f for f, _, _ in edits})
    orig = {f: open(R + f, 'rb').read() for f in files}
    try:
        for f, old, new in edits:
            s = open(R + f).read(); assert s.count(old) == 1, (pid, f, s.count(old)); open(R + f, 'w').write(s.replace(old, new))
        rc = subprocess.run(cmd, cwd=R, capture_output=True, text=True, timeout=2400)
        out = [l for l in (rc.stdout + rc.stderr).splitlines() if "passed" in l or "failed" in l or "MATRIX[" in l][-1:]
    finally:
        for f, b in orig.items(): open(R + f, 'wb').write(b)
    for f, b in orig.items(): assert open(R + f, 'rb').read() == b
    res.append((pid, "ARMED" if rc.returncode != 0 else "VACUOUS")); print(pid, res[-1][1], out, flush=True)
print("ARMED=%d VACUOUS=%d" % (sum(r[1] == "ARMED" for r in res), sum(r[1] == "VACUOUS" for r in res)))
