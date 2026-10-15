"""MVC-EPC-D-001 D2q perturbations: CO-10 visit summary and care plan (owner's own completed visit; this session's prescriptions
for this pet; one care plan by the consultation's veterinarian after the outcome). python3 perturb_epc_d_d2q_co10.py <root>.
ARMED = the named test FAILS."""
import subprocess
import sys
R = sys.argv[1].rstrip("/") + "/"
T = "petcare_api/tests/test_epc_d2q_co10_visit_summary.py::"
PG = "petcare_api/tests/test_epc_d2q_co10_care_plan_postgres.py"
PY = lambda t: ["python3", "-m", "pytest", t, "-q", "-p", "no:cacheprovider"]
VT = lambda t: ["npx", "vitest", "run", t]
M, CP, PGR = "petcare_api/main.py", "petcare_api/care_plan.py", "petcare_api/postgres_repositories.py"
PAGE = "petcare_web/app/owner/consultations/[sessionId]/summary/page.tsx"
UT = "__tests__/co10-visit-summary.test.tsx"
P = [
 ("P-D2Q-CO10-OTHER-SESSION-PRESCRIPTIONS", [(M, "           if rx.session_id == session_id and rx.pet_id == c.pet_id]", "           if rx.pet_id == c.pet_id]")],
  PY(T + "test_the_owner_reads_outcome_session_prescriptions_and_care_plan")),
 ("P-D2Q-CO10-OTHER-PET-PRESCRIPTIONS", [(M, "           if rx.session_id == session_id and rx.pet_id == c.pet_id]", "           if rx.session_id == session_id]")],
  PY(T + "test_the_owner_reads_outcome_session_prescriptions_and_care_plan")),
 ("P-D2Q-CO10-ANOTHER-OWNER-READS", [(M, "    if c is None or c.owner_id != actor_id:\n        raise HTTPException(404, \"Consultation not found\")",
   "    if c is None:\n        raise HTTPException(404, \"Consultation not found\")")],
  PY(T + "test_another_owner_or_tenant_never_learns_the_visit_exists")),
 ("P-D2Q-CO10-INCOMPLETE-VISIT-SUMMARISED", [(M, "    outcome = CONSULTATION_REPO.outcome_of(session_id, tenant_id=tenant_id)\n    if outcome is None:\n        raise HTTPException(409, {\"error\": \"VISIT_NOT_COMPLETED\"})\n    names",
   "    outcome = CONSULTATION_REPO.outcome_of(session_id, tenant_id=tenant_id) or consult.ConsultationOutcome(session_id, tenant_id, '-', '-', c.created_at)\n    names")],
  PY(T + "test_a_summary_without_a_care_plan_says_so_and_an_incomplete_visit_is_409")),
 ("P-D2Q-CO10-PLAN-BEFORE-OUTCOME", [(M, "    if CONSULTATION_REPO.outcome_of(session_id, tenant_id=tenant_id) is None:\n        raise HTTPException(409, {\"error\": \"VISIT_NOT_COMPLETED\"})\n    try:\n        follow_up",
   "    try:\n        follow_up")],
  PY(T + "test_only_the_consultations_veterinarian_records_one_care_plan_after_the_outcome")),
 ("P-D2Q-CO10-ANY-VET-RECORDS-PLAN", [(M, "    if role != ROLE_VETERINARIAN or actor_id != c.veterinarian_id:\n        raise HTTPException(403, \"Only the consultation's veterinarian records its care plan\")",
   "    if role != ROLE_VETERINARIAN:\n        raise HTTPException(403, \"Only the consultation's veterinarian records its care plan\")")],
  PY(T + "test_only_the_consultations_veterinarian_records_one_care_plan_after_the_outcome")),
 ("P-D2Q-CO10-SECOND-PLAN-REPLACES", [(CP, "            raise CarePlanExists(p.session_id)\n", "            pass\n")],
  PY(T + "test_only_the_consultations_veterinarian_records_one_care_plan_after_the_outcome")),
 ("P-D2Q-CO10-FOLLOW-UP-UTC-DATE", [(CP, "    if p.follow_up_on is not None and p.follow_up_on < ksa_date(p.recorded_at):",
   "    if p.follow_up_on is not None and p.follow_up_on < p.recorded_at.date():")],
  PY(T + "test_a_follow_up_is_compared_on_the_riyadh_calendar")),
 ("P-D2Q-CO10-PG-PLAN-UNSCOPED", [(PGR, '"SELECT {self._C} FROM consultation_care_plan WHERE session_id = %s AND tenant_id = %s",\n                             (session_id, tenant_id)',
   '"SELECT {self._C} FROM consultation_care_plan WHERE session_id = %s",\n                             (session_id,)')],
  PY(PG)),
 ("P-D2Q-CO10-UI-NO-PLAN-SHOWN-AS-PLAN", [(PAGE, "          {s.care_plan === null ? <p data-testid=\"visit-no-care-plan\">", "          {false ? <p data-testid=\"visit-no-care-plan\">")],
  VT(UT)),
 ("P-D2Q-CO10-UI-INCOMPLETE-AS-ERROR", [(PAGE, "    if (r.status === 409) { setState('notCompleted'); return }\n", "")], VT(UT)),
 ("P-D2Q-CO10-UI-FOLLOW-UP-DROPPED", [(PAGE, "data-date={s.care_plan.follow_up_on ?? ''}", "data-date=\"\"")], VT(UT)),
]
res = []
for pid, edits, cmd in P:
    files = sorted({f for f, _, _ in edits})
    orig = {f: open(R + f, 'rb').read() for f in files}
    try:
        for f, old, new in edits:
            s = open(R + f).read(); assert s.count(old) == 1, (pid, f, s.count(old)); open(R + f, 'w').write(s.replace(old, new))
        rc = subprocess.run(cmd, cwd=R + ("petcare_web" if cmd[0] == "npx" else ""), capture_output=True, text=True, timeout=1800)
        out = [l for l in (rc.stdout + rc.stderr).splitlines() if "passed" in l or "failed" in l][-1:]
    finally:
        for f, b in orig.items(): open(R + f, 'wb').write(b)
    for f, b in orig.items(): assert open(R + f, 'rb').read() == b
    res.append((pid, "ARMED" if rc.returncode != 0 else "VACUOUS")); print(pid, res[-1][1], out, flush=True)
print("ARMED=%d VACUOUS=%d" % (sum(r[1] == "ARMED" for r in res), sum(r[1] == "VACUOUS" for r in res)))
