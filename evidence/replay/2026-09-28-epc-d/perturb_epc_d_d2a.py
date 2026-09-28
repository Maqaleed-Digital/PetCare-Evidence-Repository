"""MVC-EPC-D-001 D2a (X-23 auth-log PII, X-24 canonical web app) perturbations. python3 perturb_epc_d_d2a.py <root>.
ARMED = the named test FAILS. New files are staged (tracked) and removed afterwards."""
import os
import subprocess
import sys
R = sys.argv[1].rstrip("/") + "/"
X23 = ["python3", "-m", "pytest", "petcare_api/tests/test_epc_d2_auth_log_pii.py", "-q", "-p", "no:cacheprovider"]
X24 = ["python3", "-m", "pytest", "tests/governance/test_canonical_web_app.py", "-q", "-p", "no:cacheprovider"]
A = "petcare_api/routers/auth.py"
P = [
 ("P-D2A-AUTH-LOG-RAW-EMAIL", [(A, '    log.info("AUTH_EVENT %s %s", event_name, _log_safe(detail))', '    log.info("AUTH_EVENT %s %s", event_name, detail)')], {}, X23),
 ("P-D2A-AUTH-LOG-NO-CORRELATION", [(A, '    return {("email_ref" if k == "email" else k): (email_ref(v) if k == "email" else v) for k, v in detail.items()}',
                                      '    return {("email_ref" if k == "email" else k): ("redacted" if k == "email" else v) for k, v in detail.items()}')], {}, X23),
 ("P-D2A-PRODUCT-UI-IN-PROTOTYPE-APP", [], {"petcare-web/app/shop/page.tsx": "export default function Shop() { return null }\n"}, X24),
 ("P-D2A-CI-TESTS-PROTOTYPE-APP", [(".github/workflows/verify.yml", "      - name: Web unit tests\n        working-directory: petcare_web\n",
                                    "      - name: Web unit tests\n        working-directory: petcare-web\n")], {}, X24),
]
res = []
for pid, edits, new_files, cmd in P:
    files = sorted({f for f, _, _ in edits})
    orig = {f: open(R + f, 'rb').read() for f in files}
    try:
        for f, old, new in edits:
            s = open(R + f).read(); assert s.count(old) == 1, (pid, f, s.count(old)); open(R + f, 'w').write(s.replace(old, new))
        for f, body in new_files.items():
            assert not os.path.exists(R + f), f
            os.makedirs(os.path.dirname(R + f), exist_ok=True); open(R + f, 'w').write(body)
            subprocess.run(["git", "add", "--", f], cwd=R, check=True)
        rc = subprocess.run(cmd, cwd=R, capture_output=True, text=True, timeout=900)
        out = [l for l in (rc.stdout + rc.stderr).splitlines() if "passed" in l or "failed" in l][-1:]
    finally:
        for f, b in orig.items(): open(R + f, 'wb').write(b)
        for f in new_files:
            subprocess.run(["git", "rm", "-q", "--cached", "--", f], cwd=R)
            os.remove(R + f)
            d = os.path.dirname(R + f)
            while d.rstrip("/") != R.rstrip("/") and os.path.isdir(d) and not os.listdir(d):
                os.rmdir(d); d = os.path.dirname(d)
    for f, b in orig.items(): assert open(R + f, 'rb').read() == b
    for f in new_files: assert not os.path.exists(R + f)
    res.append((pid, "ARMED" if rc.returncode != 0 else "VACUOUS")); print(pid, res[-1][1], out, flush=True)
print("ARMED=%d VACUOUS=%d" % (sum(r[1] == "ARMED" for r in res), sum(r[1] == "VACUOUS" for r in res)))
