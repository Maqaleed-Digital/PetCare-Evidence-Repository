"""U28 (NFR-08 / SQ-3) perturbations. Run: python3 perturb_u28.py <checkout root>. ARMED = the named test FAILS."""
import sys
import subprocess
R = sys.argv[1].rstrip("/") + "/"
T = "petcare_api/tests/test_nfr08_sq3.py"
PG = "petcare_api/tests/test_nfr08_sq3_postgres.py"
PY = lambda *k: ["python3", "-m", "pytest", *[T + "::" + x for x in k], "-q", "-p", "no:cacheprovider"]
PGC = ["python3", "-m", "pytest", PG, "-q", "-p", "no:cacheprovider"]
EVERY = "test_every_served_sensitive_operation_challenges_every_role"
M, F, A = "petcare_api/main.py", "petcare_api/mfa.py", "petcare_api/postgres_repositories.py"
RESET = "test_assisted_reset_needs_a_second_same_tenant_admin_revokes_every_session_and_forces_reenrolment"
RC = "test_recovery_codes_are_ten_hashed_single_use_one_operation_each_and_never_logged"
ENROL = "test_enrolment_needs_reauthentication_without_a_factor_and_a_step_up_with_one"
P = [
 ("P-BYPASS-STEP-UP", [(M, "    if operation not in mfa_mod.MIDDLEWARE_OPERATIONS:\n        return await call_next(request)",
                        "    if True:\n        return await call_next(request)")], PY(EVERY)),
 ("P-POM-SUPPLY-UNGUARDED", [(M, "        _require_step_up(request, mfa_mod.SUPPLY_OF_PRESCRIPTION_CLASS)\n", "        pass\n")], PY(EVERY)),
 ("P-EXTEND-FRESHNESS", [(F, "STEP_UP_FRESHNESS_SECONDS = 15 * 60", "STEP_UP_FRESHNESS_SECONDS = 16 * 60")],
  PY("test_freshness_is_fifteen_minutes_exactly")),
 ("P-ALWAYS-FRESH-REUSE", [(F, "ALWAYS_FRESH_ITEMS = frozenset({5, 8, 9, 12, 13})", "ALWAYS_FRESH_ITEMS = frozenset()")],
  PY("test_an_always_fresh_operation_never_reuses_a_step_up")),
 ("P-PG-ALWAYS-FRESH-REUSE", [(A, '"AND used = FALSE", (session_id, user_id, cutoff))', '"", (session_id, user_id, cutoff))')], PGC),
 ("P-FACTORLESS-ENROL-NO-REAUTH", [(M, "        ok = bool(body.password) and ident is not None and auth._verify_password(body.password, ident.password_hash)[0]",
                                    "        ok = True")], PY(ENROL)),
 ("P-SMS-FACTOR", [(F, 'FACTORS = ("totp",)', 'FACTORS = ("totp", "sms")')], PY(ENROL)),
 ("P-RECOVERY-CODE-TWO-OPERATIONS", [(M, "    MFA_REPO.record_step_up(session[\"sid\"], user_id, now, single_use=True)",
                                      "    MFA_REPO.record_step_up(session[\"sid\"], user_id, now, single_use=False)")], PY(RC)),
 ("P-PLAINTEXT-RECOVERY-CODE", [(F, "                                   digest=code_digest(salt, code)))",
                                 "                                   digest=code.encode()))")], PY(RC)),
 ("P-RECOVERY-CODE-REUSE-EVERY-LAYER", [(F, "        if rc.used_at is None and hmac.compare_digest(code_digest(rc.salt, code), rc.digest):",
                                         "        if hmac.compare_digest(code_digest(rc.salt, code), rc.digest):"),
                                        (F, "            if rc.code_id == code_id and rc.used_at is None:", "            if rc.code_id == code_id:")], PY(RC)),
 ("P-PG-RECOVERY-CODE-REUSE", [(A, '"AND used_at IS NULL", (_to_db(at), code_id, user_id))', '"", (_to_db(at), code_id, user_id))')], PGC),
 ("P-CROSS-TENANT-APPROVER", [(F, "        return r if r is not None and r.tenant_id == tenant_id else None", "        return r")], PY(RESET)),
 ("P-SELF-APPROVAL", [(M, "    if actor_id in (r.requested_by, r.subject_user_id):", "    if actor_id == r.requested_by:")], PY(RESET)),
 ("P-NO-SESSION-REVOCATION", [(M, "    revoked = auth.SESSION_STORE.revoke_all_for_user(r.subject_user_id, tenant_id=tenant_id)", "    revoked = 2")], PY(RESET)),
 ("P-ME-IGNORES-REVOCATION", [("petcare_api/routers/auth.py", "    payload = read_session(request)\n\n    user = IDENTITY_REPO.get_by_email(payload[\"email\"])",
                               "    payload = _serializer().loads(request.cookies.get(COOKIE_NAME_SESSION), max_age=COOKIE_MAX_AGE)\n\n    user = IDENTITY_REPO.get_by_email(payload[\"email\"])")], PY(RESET)),
 ("P-SENSITIVE-BEFORE-REENROLMENT", [(F, "        self._factors.pop(user_id, None)\n        self._codes.pop(user_id, None)",
                                      "        self._codes.pop(user_id, None)")], PY(RESET)),
 ("P-SOLE-ADMIN-RESET-ALLOWED", [(M, "    if not approvers:\n", "    if False:\n")], PY("test_a_sole_admin_cannot_perform_an_in_product_assisted_reset")),
 ("P-ENFORCEMENT-DEFAULT-OFF", [(M, "MFA_STEP_UP_ENFORCED = True", "MFA_STEP_UP_ENFORCED = False")],
  PY("test_step_up_is_enforced_by_default_and_has_no_off_switch")),
]
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
print("ARMED=%d VACUOUS=%d" % (sum(r[1] == "ARMED" for r in res), sum(r[1] == "VACUOUS" for r in res)))
