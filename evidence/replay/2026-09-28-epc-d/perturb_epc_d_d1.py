"""MVC-EPC-D-001 Lane D, unit D1 (SQ-3 completion) perturbations. Run: python3 perturb_epc_d_d1.py <checkout root>.
ARMED = the named test FAILS with the mutation applied."""
import os
import sys
import subprocess
R = sys.argv[1].rstrip("/") + "/"
T = "petcare_api/tests/test_epc_d1_sq3_completion.py::"
PY = lambda t: ["python3", "-m", "pytest", T + t, "-q", "-p", "no:cacheprovider"]
PG = ["python3", "-m", "pytest", "petcare_api/tests/test_epc_d1_sq3_postgres.py", "-q", "-p", "no:cacheprovider"]
M, F, S, A = "petcare_api/main.py", "petcare_api/mfa.py", "petcare_api/sq3_ops.py", "petcare_api/routers/auth.py"
SIGN, ROLE = "test_4_a_veterinarian_signs_a_medical_record_once_and_it_is_then_immutable", \
    "test_5_role_change_is_always_fresh_bounded_by_the_admin_and_revokes_the_subject_sessions"
EXP, FIN = "test_11_an_owner_downloads_their_own_personal_data_and_no_secret", \
    "test_12_13_payout_and_bank_details_are_always_fresh_and_the_iban_is_never_returned_or_logged"
CRED, KEY = "test_14_an_issued_credential_is_shown_once_stored_one_way_redeemed_once_and_never_logged", \
    "test_15_an_api_key_is_shown_once_stored_as_sha256_listed_by_prefix_and_revocable"
P = [
 ("P-D1-SIGN-NO-STEP-UP", [(F, '    4: ("signing medical records", ("POST /api/pets/{pet_id}/medical-records/{record_id}/sign",)),',
                            '    4: ("signing medical records", ()),')], PY(SIGN)),
 ("P-D1-SIGN-TWICE", [("petcare_api/pets.py", "                if r.signed_at is not None:\n                    return \"ALREADY_SIGNED\"\n", "")], PY(SIGN)),
 ("P-D1-PG-SIGNED-RECORD-MUTABLE", [("petcare_runtime/migrations/0055_epc_d1_sq3_completion.sql",
   "CREATE TRIGGER pet_medical_record_signed_immutable\n    BEFORE UPDATE OR DELETE ON pet_medical_record\n    FOR EACH ROW EXECUTE FUNCTION pet_medical_record_signed_is_immutable();\n", "")], PG),
 ("P-D1-ROLE-NOT-ALWAYS-FRESH", [(F, "ALWAYS_FRESH_ITEMS = frozenset({5, 8, 9, 12, 13})", "ALWAYS_FRESH_ITEMS = frozenset({8, 9, 12, 13})")], PY(ROLE)),
 ("P-D1-ROLE-SESSIONS-KEPT", [(M, "    revoked = auth.SESSION_STORE.revoke_all_for_user(user_id, tenant_id=tenant_id)\n    _audit(event_name=\"identity.role.changed\"",
                               "    revoked = 1\n    _audit(event_name=\"identity.role.changed\"")], PY(ROLE)),
 ("P-D1-ROLE-SELF-CHANGE", [(M, "    if user_id == actor_id:\n        raise HTTPException(403, {\"error\": \"ROLE_SELF_CHANGE_REFUSED\"})\n", "")], PY(ROLE)),
 ("P-D1-EXPORT-NO-STEP-UP", [(F, '    11: ("export of personal data", ("GET /api/me/export",)),', '    11: ("export of personal data", ()),')], PY(EXP)),
 ("P-D1-EXPORT-LEAKS-PASSWORD-HASH", [(M, '"role": ident.role,\n                     "tenant_id": ident.tenant_id}',
                                       '"role": ident.role,\n                     "tenant_id": ident.tenant_id, "password_hash": ident.password_hash}')], PY(EXP)),
 ("P-D1-BANK-IBAN-RETURNED", [(M, "    return b.read_model()\n\n\n@app.get(\"/api/admin/tenant/bank-details\")",
                               "    return {**b.read_model(), \"iban\": iban}\n\n\n@app.get(\"/api/admin/tenant/bank-details\")")], PY(FIN)),
 ("P-D1-IBAN-CHECKSUM-SKIPPED", [(S, "    return int(digits) % 97 == 1", "    return True")], PY(FIN)),
 ("P-D1-PAYOUT-NOT-ALWAYS-FRESH", [(F, "ALWAYS_FRESH_ITEMS = frozenset({5, 8, 9, 12, 13})", "ALWAYS_FRESH_ITEMS = frozenset({5, 8, 9, 13})")], PY(FIN)),
 ("P-D1-CREDENTIAL-STORED-RAW", [(M, "    auth.INVITE_REPO.upsert(auth.InviteCode(code=sq3_ops.credential_key(raw), allowed_role=body.role,",
                                  "    auth.INVITE_REPO.upsert(auth.InviteCode(code=raw, allowed_role=body.role,")], PY(CRED)),
 ("P-D1-CREDENTIAL-LOGGED", [(A, '    return "inv:" + hashlib.sha256(str(code).encode()).hexdigest()[:12]', '    return str(code)')], PY(CRED)),
 ("P-D1-API-KEY-STORED-RAW", [(M, "    k = SQ3_OPS.add_api_key(sq3_ops.ApiKey(key_id, tenant_id, body.name.strip(), prefix, digest, actor_id,",
                               "    k = SQ3_OPS.add_api_key(sq3_ops.ApiKey(key_id, tenant_id, body.name.strip(), prefix, key, actor_id,")], PY(KEY)),
 ("P-D1-API-KEY-ANY-ADMIN", [(M, "def issue_api_key(body: ApiKeyRequest, request: Request, role: str = Depends(require_admin),",
                               "def issue_api_key(body: ApiKeyRequest, request: Request, role: str = Depends(require_role),")], PY(KEY)),
]
res = []
for pid, edits, cmd in P:
    files = sorted({f for f, _, _ in edits})
    orig = {f: open(R + f, 'rb').read() for f in files}
    try:
        for f, old, new in edits:
            s = open(R + f).read(); assert s.count(old) == 1, (pid, f, s.count(old)); open(R + f, 'w').write(s.replace(old, new))
        rc = subprocess.run(cmd, cwd=R, capture_output=True, text=True, timeout=900, env={**os.environ, "TZ": "UTC"})
        out = [l for l in (rc.stdout + rc.stderr).splitlines() if "passed" in l or "failed" in l][-1:]
    finally:
        for f, b in orig.items(): open(R + f, 'wb').write(b)
    for f, b in orig.items(): assert open(R + f, 'rb').read() == b
    res.append((pid, "ARMED" if rc.returncode != 0 else "VACUOUS")); print(pid, res[-1][1], out, flush=True)
print("ARMED=%d VACUOUS=%d" % (sum(r[1] == "ARMED" for r in res), sum(r[1] == "VACUOUS" for r in res)))
