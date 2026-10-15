"""MVC-EPC-D-001 D3a perturbations: J-V1 internal licence status (CV-12) — attestation never shown as registry verification;
no authority claimed without the server; registry notice always present. python3 perturb_epc_d_d3a_jv1.py <root>.
ARMED = the named test FAILS."""
import subprocess
import sys
R = sys.argv[1].rstrip("/") + "/"
VT = lambda t: ["npx", "vitest", "run", t]
PAGE = "petcare_web/app/vet/profile/page.tsx"
UT = "__tests__/jv1-vet-licence-status.test.tsx"
P = [
 ("P-D3A-JV1-ATTESTATION-SHOWN-AS-LOOKUP", [(PAGE, "t(l.verification?.method === 'AUTHORITY_LOOKUP' ? 'VERIFIED_LOOKUP' : 'VERIFIED_MANUAL')", "t('VERIFIED_LOOKUP')")], VT(UT)),
 ("P-D3A-JV1-NO-TENANT-CLAIMS-AUTHORITY", [(PAGE, "setAuthority(a.ok ? await a.json() : { in_force: false, reason: null, grants: [] })", "setAuthority(a.ok ? await a.json() : { in_force: true, reason: null, grants: [] })")], VT(UT)),
 ("P-D3A-JV1-REGISTRY-NOTICE-DROPPED", [(PAGE, "      <p className=\"muted\" data-testid=\"vet-registry-notice\">{t('registry')}</p>\n", "")], VT(UT)),
 ("P-D3A-JV1-STATUS-NOT-FROM-SERVER", [(PAGE, "data-status={l.status}", "data-status=\"VERIFIED\"")], VT(UT)),
]
res = []
for pid, edits, cmd in P:
    files = sorted({f for f, _, _ in edits})
    orig = {f: open(R + f, 'rb').read() for f in files}
    try:
        for f, old, new in edits:
            s = open(R + f).read(); assert s.count(old) == 1, (pid, f, s.count(old)); open(R + f, 'w').write(s.replace(old, new))
        rc = subprocess.run(cmd, cwd=R + "petcare_web", capture_output=True, text=True, timeout=1800)
        out = [l for l in (rc.stdout + rc.stderr).splitlines() if "passed" in l or "failed" in l][-1:]
    finally:
        for f, b in orig.items(): open(R + f, 'wb').write(b)
    for f, b in orig.items(): assert open(R + f, 'rb').read() == b
    res.append((pid, "ARMED" if rc.returncode != 0 else "VACUOUS")); print(pid, res[-1][1], out, flush=True)
print("ARMED=%d VACUOUS=%d" % (sum(r[1] == "ARMED" for r in res), sum(r[1] == "VACUOUS" for r in res)))
