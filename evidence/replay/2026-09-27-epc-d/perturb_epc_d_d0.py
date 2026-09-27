"""MVC-EPC-D-001 Lane D, unit D0 (full-stack harness + design system) perturbations.
Run: python3 perturb_epc_d_d0.py <checkout root>. ARMED = the named test FAILS with the mutation applied.
The harness perturbation runs the real full stack (PostgreSQL + main:app + next dev) — ports 8090/3100 must be free.
"""
import os
import sys
import subprocess
R = sys.argv[1].rstrip("/") + "/"
DS = ["npx", "vitest", "run", "__tests__/epc-d-design-system.test.tsx"]
HARNESS = ["npx", "playwright", "test", "-c", "playwright.full.config.ts", "--project", "en-desktop", "-g", "seeded owner"]
UI = "petcare_web/components/ui/index.tsx"
P = [
 ("P-HARNESS-SEED-CREDENTIAL-WRONG", [("tools/e2e_stack.py", 'SEED_PASSWORD = "E2E-only-Passw0rd!"', 'SEED_PASSWORD = "E2E-only-Passw0rd!-mutated"')], HARNESS),
 ("P-DATAVIEW-NO-EMPTY-STATE", [(UI, "      {status === 'ready' && (data == null || (Array.isArray(data) && data.length === 0)",
                                 "      {status === 'ready' && (data == null")], DS),
 ("P-FIELD-UNLABELLED", [(UI, '      <label className="ds-label" htmlFor={id}>{tr(label)}</label>',
                          '      <label className="ds-label">{tr(label)}</label>')], DS),
 ("P-PAGE-LTR-IN-ARABIC", [(UI, "    <main className=\"ds-page\" dir={isAr ? 'rtl' : 'ltr'} data-testid={testId} data-ds=\"page\">",
                            "    <main className=\"ds-page\" dir=\"ltr\" data-testid={testId} data-ds=\"page\">")], DS),
]
res = []
for pid, edits, cmd in P:
    files = sorted({f for f, _, _ in edits})
    orig = {f: open(R + f, 'rb').read() for f in files}
    try:
        for f, old, new in edits:
            s = open(R + f).read(); assert s.count(old) == 1, (pid, f, s.count(old)); open(R + f, 'w').write(s.replace(old, new))
        env = {**os.environ, "CI": "1"}           # never reuse a running server: the mutated code must be what runs
        rc = subprocess.run(cmd, cwd=R + "petcare_web", capture_output=True, text=True, timeout=1500, env=env)
        out = [l for l in (rc.stdout + rc.stderr).splitlines() if "passed" in l or "failed" in l or "Tests " in l][-1:]
    finally:
        for f, b in orig.items(): open(R + f, 'wb').write(b)
    for f, b in orig.items(): assert open(R + f, 'rb').read() == b
    res.append((pid, "ARMED" if rc.returncode != 0 else "VACUOUS")); print(pid, res[-1][1], out, flush=True)
print("ARMED=%d VACUOUS=%d" % (sum(r[1] == "ARMED" for r in res), sum(r[1] == "VACUOUS" for r in res)))
