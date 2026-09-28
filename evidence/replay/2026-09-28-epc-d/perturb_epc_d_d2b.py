"""MVC-EPC-D-001 D2b (J-00 landing, J-O1 owner self-registration) perturbations. python3 perturb_epc_d_d2b.py <root>.
ARMED = the named test FAILS. The J-00 case runs the real full stack (ports 8090/3100 must be free)."""
import os
import subprocess
import sys
R = sys.argv[1].rstrip("/") + "/"
T = "petcare_api/tests/test_epc_d2_self_registration.py::"
PY = lambda t: ["python3", "-m", "pytest", T + t, "-q", "-p", "no:cacheprovider"]
PG = ["python3", "-m", "pytest", "petcare_api/tests/test_epc_d2_account_tokens_postgres.py", "-q", "-p", "no:cacheprovider"]
WEB = ["npx", "vitest", "run", "__tests__/epc-d2-x1-x6.test.tsx"]
J00 = ["npx", "playwright", "test", "-c", "playwright.full.config.ts", "--project", "ar-desktop", "-g", "J-00"]
A, K, E = "petcare_api/routers/auth.py", "petcare_api/account_tokens.py", "petcare_api/adapters/email.py"
OFF, ON = "test_switch_off_is_the_default_and_self_registration_fails_closed_with_no_bypass", "test_switch_on_register_verify_then_sign_in"
CLOSED, RESET = "test_switch_on_fails_closed_without_an_email_provider_or_a_tenant", \
    "test_password_reset_does_not_enumerate_is_single_use_and_revokes_sessions"
EXP = "test_tokens_expire_and_the_fake_adapter_is_refused_in_production"
P = [
 ("P-D2B-SELF-REG-DEFAULT-ON", [(A, '    return (env.get(SELF_REGISTRATION_SWITCH) or "").strip().lower() in ("on", "true", "1")',
                                 '    return (env.get(SELF_REGISTRATION_SWITCH) or "on").strip().lower() in ("on", "true", "1")')], PY(OFF)),
 ("P-D2B-SELF-REG-API-BYPASS", [(A, '    if not self_registration_enabled():\n        raise HTTPException(404, {"error": "SELF_REGISTRATION_DISABLED"})\n', "")], PY(OFF)),
 ("P-D2B-NO-EMAIL-VERIFICATION-GATE", [(A, "    if PERSISTENCE.account_tokens.verification_pending(user.user_id):", "    if False:")], PY(ON)),
 ("P-D2B-TOKEN-REUSE", [(K, "        if t is None or t.purpose != purpose or t.used_at is not None or now >= t.expires_at:",
                          "        if t is None or t.purpose != purpose or now >= t.expires_at:")], PY(ON)),
 ("P-D2B-TOKEN-STORED-RAW", [(K, "        self._tokens[digest(raw)] = AccountToken(digest(raw), user_id, purpose, now, now + TTL[purpose])",
                               "        self._tokens[raw] = AccountToken(raw, user_id, purpose, now, now + TTL[purpose])")], PY(ON)),
 ("P-D2B-PG-TOKEN-REUSE", [("petcare_api/postgres_repositories.py", '"AND used_at IS NULL AND expires_at > %s RETURNING user_id",',
                             '"AND expires_at > %s RETURNING user_id",')], PG),
 ("P-D2B-EMAIL-UNCONFIGURED-NOT-CHECKED-FIRST", [(A, "    _email_ready()\n    if IDENTITY_REPO.get_by_email(email) is not None:",
                                                  "    if IDENTITY_REPO.get_by_email(email) is not None:")], PY(CLOSED)),
 ("P-D2B-RESET-ENUMERATES", [(A, "    if user is not None and user.is_active:\n        token = PERSISTENCE.account_tokens.issue(user.user_id, \"PASSWORD_RESET\", now=datetime.now(timezone.utc))",
                               "    if user is None:\n        raise HTTPException(404, {\"error\": \"UNKNOWN\"})\n    if user.is_active:\n        token = PERSISTENCE.account_tokens.issue(user.user_id, \"PASSWORD_RESET\", now=datetime.now(timezone.utc))")], PY(RESET)),
 ("P-D2B-RESET-KEEPS-SESSIONS", [(A, "    revoked = SESSION_STORE.revoke_all_for_user(user_id, tenant_id=user.tenant_id) if user and user.tenant_id else 0",
                                   "    revoked = 1")], PY(RESET)),
 ("P-D2B-FAKE-EMAIL-IN-PRODUCTION", [(E, '        if (env.get(ENV_DEPLOYMENT) or "").strip().lower() == "production":\n            raise EmailUnavailable("the FAKE email adapter is refused in production")\n', "")], PY(EXP)),
 ("P-D2B-INVITE-CODE-IN-BROWSER-STORAGE", [("petcare_web/app/register/page.tsx", "          origin: 'pilot_invite',   // X6: never the invite code itself",
                                             "          origin: 'pilot_invite', origin_invite_code: inviteCode,")], WEB),
 ("P-D2B-NAV-RAW-ROLE", [("petcare_web/components/Nav.tsx", "                {STRINGS.nav.roleNames[user.role] ? t(STRINGS.nav.roleNames[user.role]) : user.role}",
                          "                {user.role}")], WEB),
 ("P-D2B-LANDING-ENGLISH-IN-ARABIC", [("petcare_web/lib/strings.ts", "    privacyLink:  { ar: 'إشعار الخصوصية', en: 'Privacy notice' },",
                                        "    privacyLink:  { ar: 'Privacy notice', en: 'Privacy notice' },")], J00),
]
res = []
for pid, edits, cmd in P:
    files = sorted({f for f, _, _ in edits})
    orig = {f: open(R + f, 'rb').read() for f in files}
    try:
        for f, old, new in edits:
            s = open(R + f).read(); assert s.count(old) == 1, (pid, f, s.count(old)); open(R + f, 'w').write(s.replace(old, new))
        cwd = R + "petcare_web" if cmd[0] == "npx" else R
        rc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=1500, env={**os.environ, "CI": "1"})
        out = [l for l in (rc.stdout + rc.stderr).splitlines() if "passed" in l or "failed" in l or "Tests " in l][-1:]
    finally:
        for f, b in orig.items(): open(R + f, 'wb').write(b)
    for f, b in orig.items(): assert open(R + f, 'rb').read() == b
    res.append((pid, "ARMED" if rc.returncode != 0 else "VACUOUS")); print(pid, res[-1][1], out, flush=True)
print("ARMED=%d VACUOUS=%d" % (sum(r[1] == "ARMED" for r in res), sum(r[1] == "VACUOUS" for r in res)))
