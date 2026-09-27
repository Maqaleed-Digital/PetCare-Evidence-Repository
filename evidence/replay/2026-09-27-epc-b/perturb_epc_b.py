"""MVC-EPC-B-001 (Lane B, web step-up UX) perturbations. Run: python3 perturb_epc_b.py <checkout root>.
ARMED = the Lane B web test FAILS with the mutation applied. Lane-specific directory so no existing replay date is touched.
"""
import sys
import subprocess
R = sys.argv[1].rstrip("/") + "/"
W = "petcare_web/"
T = ["npx", "vitest", "run", "__tests__/epc-b-step-up.test.tsx"]
LIB, DLG, SEC = W + "lib/stepUp.ts", W + "components/StepUp.tsx", W + "app/account/security/page.tsx"
P = [
 ("P-AUTO-RETRY-WITHOUT-STEP-UP", [(LIB, "  if (!(await prompt())) return { response: first, state: 'cancelled' }",
                                    "  if (!(true)) return { response: first, state: 'cancelled' }")]),
 ("P-RETRY-LOOP", [(LIB, "  if (again === STEP_UP_REQUIRED) return { response: second, state: 'step_up_failed' }",
                    "  if (again === STEP_UP_REQUIRED) return withStepUp(send, prompt)")]),
 ("P-CLIENT-TIMER-SKIPS-PROMPT", [(LIB, "export async function withStepUp(", "const LAST = { at: 0 }\nexport async function withStepUp("),
                                  (LIB, "  if (!(await prompt())) return { response: first, state: 'cancelled' }",
                                   "  if (!(Date.now() - LAST.at < 900000) && !(await prompt())) return { response: first, state: 'cancelled' }\n  LAST.at = Date.now()")]),
 ("P-CODE-PERSISTED-TO-STORAGE", [(DLG, "    const value = code\n", "    const value = code\n    sessionStorage.setItem('petcare_step_up_code', value)\n")]),
 ("P-CODE-LOGGED", [(DLG, "    const value = code\n", "    const value = code\n    console.info('step-up submitted', value)\n")]),
 ("P-RECOVERY-CODES-REDISPLAYED", [(SEC, "    setCodes([])                                  // gone for good: never stored, never re-displayed\n", ""),
                                   (SEC, "      {phase === 'codes' && (", "      {(phase === 'codes' || codes.length > 0) && (")]),
 ("P-FACTORLESS-ENROLMENT-WITHOUT-REAUTH", [(SEC, "      setPhase('password')\n", "      setPhase('confirm')\n")]),
 ("P-PENDING-REENROLMENT-BYPASS", [(LIB, "  if (refusal === ENROLMENT_REQUIRED) return { response: first, state: 'enrolment_required' }\n", "")]),
 ("P-ENGLISH-STRING-IN-ARABIC-MODE", [(LIB, "  title: { ar: 'تأكيد الهوية مطلوب', en: 'Verification required' },",
                                       "  title: { ar: 'Verification required', en: 'Verification required' },")]),
]
res = []
for pid, edits in P:
    files = sorted({f for f, _, _ in edits})
    orig = {f: open(R + f, 'rb').read() for f in files}
    try:
        for f, old, new in edits:
            s = open(R + f).read(); assert s.count(old) == 1, (pid, f, s.count(old)); open(R + f, 'w').write(s.replace(old, new))
        rc = subprocess.run(T, cwd=R + "petcare_web", capture_output=True, text=True, timeout=600)
        out = [l for l in (rc.stdout + rc.stderr).splitlines() if "Tests " in l][-1:]
    finally:
        for f, b in orig.items(): open(R + f, 'wb').write(b)
    for f, b in orig.items(): assert open(R + f, 'rb').read() == b
    res.append((pid, "ARMED" if rc.returncode != 0 else "VACUOUS")); print(pid, res[-1][1], out, flush=True)
print("ARMED=%d VACUOUS=%d" % (sum(r[1] == "ARMED" for r in res), sum(r[1] == "VACUOUS" for r in res)))
