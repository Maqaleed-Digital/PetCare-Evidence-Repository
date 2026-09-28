"""MVC-EPC-D-001 D2c (J-O2 consent ledger, J-O3 profile + export, J-O11 owner MFA, refusals under CORS) perturbations.
python3 perturb_epc_d_d2c.py <root>. ARMED = the named test FAILS. The J-O2 case runs the real full stack (ports
8090/3100 must be free)."""
import os
import subprocess
import sys
R = sys.argv[1].rstrip("/") + "/"
T = "petcare_api/tests/test_epc_d2_consent_profile.py::"
PY = lambda t: ["python3", "-m", "pytest", T + t, "-q", "-p", "no:cacheprovider"]
PG = lambda t: ["python3", "-m", "pytest", "petcare_api/tests/test_epc_d2_consent_postgres.py::" + t, "-q", "-p", "no:cacheprovider"]
WEB = lambda f: ["npx", "vitest", "run", f]
JO2 = ["npx", "playwright", "test", "-c", "playwright.full.config.ts", "--project", "ar-desktop", "-g", "J-O2"]
M, A, OC = "petcare_api/main.py", "petcare_api/routers/auth.py", "petcare_api/owner_consent.py"
PGR, MIG = "petcare_api/postgres_repositories.py", "petcare_runtime/migrations/0057_epc_d2_owner_consent_ledger.sql"
UI = "petcare_web/components/account/AccountCenter.tsx"
NEW = "test_a_new_account_has_no_consent_until_given_and_every_change_is_an_appended_audited_event"
PRIV = "test_the_privacy_notice_cannot_be_withdrawn_by_toggle_and_unknown_purposes_or_actions_are_refused"
OWN, SELF = "test_consent_is_the_callers_own_and_never_another_users", "test_self_registration_requires_the_privacy_notice_and_records_it_server_side"
PROF, EXP = "test_a_profile_edit_changes_only_the_callers_display_name", "test_the_personal_data_export_includes_the_consent_history"
CORS = "test_a_step_up_refusal_carries_cors_headers_so_the_web_origin_can_read_it"
LEDGER, PGPROF = "test_the_consent_ledger_is_append_only_and_its_state_is_the_latest_event", \
    "test_a_profile_edit_writes_only_the_display_name_and_only_in_the_callers_tenant"
P = [
 ("P-D2C-CONSENT-OTHER-USER", [(OC, "        return sorted((e for e in self._events if e.user_id == user_id and e.tenant_id == tenant_id),",
                                "        return sorted((e for e in self._events if e.tenant_id == tenant_id),")], PY(OWN)),
 ("P-D2C-PRIVACY-NOTICE-REVOCABLE", [(M, "    if body.action == owner_consent.REVOKE and purpose not in owner_consent.REVOCABLE:\n"
                                         "        raise HTTPException(409, {\"error\": \"CONSENT_NOT_REVOCABLE\", \"purpose\": purpose})\n", "")], PY(PRIV)),
 ("P-D2C-NOOP-WRITES-AN-EVENT", [(M, "    if currently == (body.action == owner_consent.GRANT):\n        return {**_consent_view(actor_id, tenant_id), \"changed\": False}\n", "")], PY(NEW)),
 ("P-D2C-CONSENT-UNAUDITED", [(M, "    _audit(event_name=\"consent.granted\" if body.action == owner_consent.GRANT else \"consent.revoked\",",
                               "    (lambda **_: None)(event_name=\"consent.granted\" if body.action == owner_consent.GRANT else \"consent.revoked\",")], PY(NEW)),
 ("P-D2C-SELF-REG-WITHOUT-PRIVACY-NOTICE", [(A, "    if body.privacy_notice_accepted is not True:\n        raise HTTPException(400, {\"error\": \"PRIVACY_NOTICE_REQUIRED\"})\n", "")], PY(SELF)),
 ("P-D2C-SELF-REG-CONSENT-NOT-RECORDED", [(A, "    PERSISTENCE.owner_consent.append(owner_consent.ConsentEvent(", "    (lambda _e: None)(owner_consent.ConsentEvent(")], PY(SELF)),
 ("P-D2C-PROFILE-WRITES-ROLE", [("petcare_api/repositories.py", "        updated = replace(existing, full_name=full_name)",
                                 "        updated = replace(existing, full_name=full_name, role=\"veterinarian\")")], PY(PROF)),
 ("P-D2C-EXPORT-WITHOUT-CONSENTS", [(M, "        \"consents\": [e.read_model() for e in CONSENT_REPO.events_for(actor_id, tenant_id=tenant_id)],\n", "")], PY(EXP)),
 ("P-D2C-REFUSAL-OUTSIDE-CORS", [(M, "\n\n_install_cors()\n", "\n"),
                                  (M, "# ---------------------------------------------------------------------------\n# Auth router\n",
                                   "app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS, allow_credentials=True, allow_methods=['*'], "
                                   "allow_headers=['*'], expose_headers=['Set-Cookie', 'Content-Disposition'])\n"
                                   "# ---------------------------------------------------------------------------\n# Auth router\n")], PY(CORS)),
 ("P-D2C-PG-LEDGER-MUTABLE", [(MIG, "    RAISE EXCEPTION 'owner_consent_event is an append-only ledger: % refused', TG_OP;", "    RETURN OLD;")], PG(LEDGER)),
 ("P-D2C-PG-PRIVACY-REVOKE-ALLOWED", [(MIG, "    CHECK (NOT (purpose = 'privacy_notice' AND action = 'REVOKE'))", "    CHECK (true)")], PG(LEDGER)),
 ("P-D2C-PG-PROFILE-ANY-TENANT", [(PGR, "            cur = conn.execute(\"UPDATE user_identity SET full_name = %s WHERE user_id = %s AND tenant_id = %s\",\n"
                                        "                               (full_name, user_id, tenant_id))",
                                   "            cur = conn.execute(\"UPDATE user_identity SET full_name = %s WHERE user_id = %s\",\n"
                                   "                               (full_name, user_id))")], PG(PGPROF)),
 ("P-D2C-UI-IGNORES-SERVER-STATE", [(UI, "    if (r?.ok) setLedger(await r.json()); else setFailed(true)", "    setFailed(!r?.ok)")],
  WEB("__tests__/epc-d2-account-center.test.tsx")),
 ("P-D2C-UI-PRIVACY-NOTICE-TOGGLE", [(UI, "                  {p.granted && p.revocable && (", "                  {p.granted && (")],
  WEB("__tests__/epc-d2-account-center.test.tsx")),
 ("P-D2C-FR09-LTR-OVERRIDE", [("petcare_web/components/PDPLRightsEntry.tsx", ' translate="no">{DPO_EMAIL}</a>', ' translate="no" dir="ltr">{DPO_EMAIL}</a>')],
  WEB("__tests__/language-fr09.test.tsx")),
 ("P-D2C-ACCOUNT-ENGLISH-IN-ARABIC", [(UI, "  consentTitle: { ar: 'الموافقات', en: 'Consents' },", "  consentTitle: { ar: 'Consents', en: 'Consents' },")], JO2),
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
