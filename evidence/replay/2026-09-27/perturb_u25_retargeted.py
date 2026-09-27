"""U25 (NFR-08 mechanism) perturbations RETARGETED after U28 replaced the mechanism under SQ-3 (v1.3 Phase R, one fix).

The 2026-09-26 corpus script perturb_u25.py is left unchanged (historical). Its anchors described the v1.2 U25 code;
U28 rewrote that code, so each rule is re-expressed here against the current code and the tests that now guard it.
P-RUNNER-CHOSEN-WINDOW is SUPERSEDED, not replayed: it guarded "the runner must not choose a freshness window", and
Sponsor act SQ-3 has since ratified the window (15 minutes); its successor is perturb_u28.py P-EXTEND-FRESHNESS.
Run: python3 perturb_u25_retargeted.py <checkout root>.
"""
import sys
import subprocess
R = sys.argv[1].rstrip("/") + "/"
SQ3 = "petcare_api/tests/test_nfr08_sq3.py::"
MECH = ["python3", "-m", "pytest", "petcare_api/tests/test_nfr08_mfa.py", "-q", "-p", "no:cacheprovider"]
PG = ["python3", "-m", "pytest", "petcare_api/tests/test_nfr08_mfa_postgres.py", "-q", "-p", "no:cacheprovider"]
PY = lambda t: ["python3", "-m", "pytest", SQ3 + t, "-q", "-p", "no:cacheprovider"]
P = [
 ("P-BYPASS-STEP-UP", [("petcare_api/main.py", "    if operation not in mfa_mod.MIDDLEWARE_OPERATIONS:\n        return await call_next(request)",
                        "    if True:\n        return await call_next(request)")],
  PY("test_a_step_up_belongs_to_the_session_that_performed_it")),
 ("P-STEP-UP-NOT-SESSION-BOUND", [("petcare_api/mfa.py",
   "        s = self._step_ups.get(session_id)\n        if not authorizes(s, user_id, now, always_fresh):",
   "        s = next((v for v in self._step_ups.values() if v.user_id == user_id), None)\n"
   "        session_id = s.session_id if s is not None else session_id\n        if not authorizes(s, user_id, now, always_fresh):")],
  PY("test_a_step_up_belongs_to_the_session_that_performed_it")),
 ("P-NO-FRESHNESS", [("petcare_api/mfa.py",
   "    if s is None or s.user_id != user_id or (now - s.verified_at).total_seconds() > STEP_UP_FRESHNESS_SECONDS:",
   "    if s is None or s.user_id != user_id:")], PY("test_freshness_is_fifteen_minutes_exactly")),
 ("P-REPLAY-ALLOWED", [("petcare_api/mfa.py", "        if f is None or (f.last_used_step is not None and step <= f.last_used_step):",
                        "        if f is None:")], MECH),
 ("P-PLAINTEXT-SECRET", [("petcare_api/mfa.py", "    return nonce, AESGCM(key).encrypt(nonce, plaintext, b\"petcare-mfa-totp\")",
                          "    return nonce, plaintext + b\"-padding-to-length\"")], MECH),
 ("P-PG-REPLAY-RACE", [("petcare_api/postgres_repositories.py",
   '                               "WHERE user_id = %s AND (last_used_step IS NULL OR last_used_step < %s)",',
   '                               "WHERE user_id = %s AND (TRUE OR last_used_step < %s)",')], PG),
]
SUPERSEDED = {"P-RUNNER-CHOSEN-WINDOW": "SQ-3 ratified the window; successor perturb_u28.py P-EXTEND-FRESHNESS"}
res = []
for pid, edits, cmd in P:
    orig = {f: open(R + f, 'rb').read() for f, _, _ in edits}
    try:
        for f, old, new in edits:
            s = open(R + f).read(); assert s.count(old) == 1, (pid, f, s.count(old)); open(R + f, 'w').write(s.replace(old, new))
        rc = subprocess.run(cmd, cwd=R, capture_output=True, text=True, timeout=600)
        out = [l for l in (rc.stdout + rc.stderr).splitlines() if "failed" in l or "passed" in l][-1:]
    finally:
        for f, b in orig.items(): open(R + f, 'wb').write(b)
    for f, b in orig.items(): assert open(R + f, 'rb').read() == b
    res.append((pid, "ARMED" if rc.returncode != 0 else "VACUOUS")); print(pid, res[-1][1], out, flush=True)
for pid, why in SUPERSEDED.items():
    print(pid, "SUPERSEDED", why)
print("ARMED=%d VACUOUS=%d SUPERSEDED=%d" % (sum(r[1] == "ARMED" for r in res), sum(r[1] == "VACUOUS" for r in res), len(SUPERSEDED)))
