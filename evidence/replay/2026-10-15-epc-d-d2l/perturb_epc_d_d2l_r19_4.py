"""MVC-EPC-D-001 D2l perturbations: R19.4 standing test — test-only step-up seeding unreachable under production configuration.
python3 perturb_epc_d_d2l_r19_4.py <root>. ARMED = the named test FAILS. Each mutation plants what R19.4 forbids."""
import subprocess
import sys
R = sys.argv[1].rstrip("/") + "/"
T = "tests/governance/test_r19_4_step_up_seeding_unreachable.py::"
PY = lambda t: ["python3", "-m", "pytest", t, "-q", "-p", "no:cacheprovider"]
M, TOOL = "petcare_api/main.py", "tools/e2e_stack.py"
ENROL = "    MFA_REPO.put_factor(mfa_mod.Factor(user_id=user_id, nonce=nonce, ciphertext=ct, created_at=_mfa_now()))\n"
P = [
 ("P-D2L-R194-API-REFERENCES-SEED-FILE", [(M, ENROL, ENROL + "    _ = os.environ.get(\"PETCARE_E2E_MFA_FILE\")\n")],
  PY(T + "test_no_application_source_contains_or_references_the_seeding[api]")),
 ("P-D2L-R194-API-CONFIRMED-FACTOR", [(M, ENROL, ENROL.replace("created_at=_mfa_now()))", "created_at=_mfa_now(), confirmed_at=_mfa_now()))"))],
  PY(T + "test_no_application_source_constructs_a_confirmed_factor")),
 ("P-D2L-R194-API-CONFIRMED-FACTOR-POSITIONAL", [(M, ENROL, ENROL.replace("mfa_mod.Factor(user_id=user_id, nonce=nonce, ciphertext=ct, created_at=_mfa_now())",
   "mfa_mod.Factor(user_id, nonce, ct, _mfa_now(), _mfa_now())"))],
  PY(T + "test_no_application_source_constructs_a_confirmed_factor")),
 ("P-D2L-R194-SEED-ROUTE", [(M, "@app.post(\"/api/me/mfa/enrol\")\n",
   "@app.post(\"/api/e2e/seed-mfa\")\ndef _planted_seed():\n    return {}\n\n\n@app.post(\"/api/me/mfa/enrol\")\n")],
  PY(T + "test_the_served_app_has_no_seeding_route_and_creates_no_factor_on_import")),
 ("P-D2L-R194-WEB-IMPORTS-E2E", [("petcare_web/components/StepUp.tsx", "'use client'\n", "'use client'\nimport { totp } from '../e2e-full/fixtures'\n")],
  PY(T + "test_no_application_source_contains_or_references_the_seeding[web]")),
 ("P-D2L-R194-TOOL-NO-PRODUCTION-REFUSAL", [(TOOL, "    _refuse_production()                      # R19.4 — before any database is created or touched\n", "")],
  PY(T + "test_the_tool_refuses_production_configuration_before_touching_a_database")),
 ("P-D2L-R194-SEED-NO-MODE-GUARD", [(TOOL, "    if (os.environ.get(\"PETCARE_SECRET_MODE\") or \"\").strip() != \"environment\":\n        raise SystemExit(\"R19.4: test-only step-up seeding refused outside PETCARE_SECRET_MODE=environment\")\n", "")],
  PY(T + "test_the_seed_step_itself_refuses_production_configuration")),
 ("P-D2L-R194-IMAGE-COPIES-TOOL", [("petcare_api/Dockerfile", "COPY petcare_api/routers ./routers\n", "COPY petcare_api/routers ./routers\nCOPY tools ./tools\n")],
  PY(T + "test_no_deployable_image_copies_the_tool_or_the_test_suites[petcare_api/Dockerfile]")),
 ("P-D2L-R194-WEB-IMAGE-COPIES-SOURCE", [("petcare_web/Dockerfile", "COPY --from=builder /app/public ./public\n", "COPY --from=builder /app/public ./public\nCOPY . .\n")],
  PY(T + "test_no_deployable_image_copies_the_tool_or_the_test_suites[petcare_web/Dockerfile]")),
]
res = []
for pid, edits, cmd in P:
    files = sorted({f for f, _, _ in edits})
    orig = {f: open(R + f, 'rb').read() for f in files}
    try:
        for f, old, new in edits:
            s = open(R + f).read(); assert s.count(old) == 1, (pid, f, s.count(old)); open(R + f, 'w').write(s.replace(old, new))
        rc = subprocess.run(cmd, cwd=R, capture_output=True, text=True, timeout=1800)
        out = [l for l in (rc.stdout + rc.stderr).splitlines() if "passed" in l or "failed" in l or "error" in l][-1:]
    finally:
        for f, b in orig.items(): open(R + f, 'wb').write(b)
    for f, b in orig.items(): assert open(R + f, 'rb').read() == b
    res.append((pid, "ARMED" if rc.returncode != 0 else "VACUOUS")); print(pid, res[-1][1], out, flush=True)
print("ARMED=%d VACUOUS=%d" % (sum(r[1] == "ARMED" for r in res), sum(r[1] == "VACUOUS" for r in res)))
