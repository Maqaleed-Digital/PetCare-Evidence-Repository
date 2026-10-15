"""MVC-EPC-D-001 D2r perturbations: CO-13 rate visit (owner's own completed visit, once, 1..5; read by the visit's vet or clinic
admin). python3 perturb_epc_d_d2r_co13.py <root>. ARMED = the named test FAILS."""
import subprocess
import sys
R = sys.argv[1].rstrip("/") + "/"
T = "petcare_api/tests/test_epc_d2r_co13_rate_visit.py::"
PG = "petcare_api/tests/test_epc_d2r_co13_rating_postgres.py"
PY = lambda t: ["python3", "-m", "pytest", t, "-q", "-p", "no:cacheprovider"]
VT = lambda t: ["npx", "vitest", "run", t]
M, VR, PGR = "petcare_api/main.py", "petcare_api/visit_rating.py", "petcare_api/postgres_repositories.py"
PAGE = "petcare_web/app/owner/consultations/[sessionId]/rate/page.tsx"
UT = "__tests__/co13-rate-visit.test.tsx"
P = [
 ("P-D2R-CO13-INCOMPLETE-RATED", [(M, "    if CONSULTATION_REPO.outcome_of(session_id, tenant_id=tenant_id) is None:\n        raise HTTPException(409, {\"error\": \"VISIT_NOT_COMPLETED\"})\n    r = vr.VisitRating(",
   "    r = vr.VisitRating(")], PY(T + "test_an_incomplete_visit_cannot_be_rated")),
 ("P-D2R-CO13-ANOTHER-OWNER-RATES", [(M, "    if c is None or c.owner_id != actor_id:\n        raise HTTPException(404, \"Consultation not found\")\n    if CONSULTATION_REPO.outcome_of",
   "    if c is None:\n        raise HTTPException(404, \"Consultation not found\")\n    if CONSULTATION_REPO.outcome_of")],
  PY(T + "test_only_the_owner_rates_and_only_the_owners_vet_or_clinic_admin_reads")),
 ("P-D2R-CO13-SECOND-RATING-REPLACES", [(VR, "            raise RatingExists(r.session_id)\n", "            pass\n")],
  PY(T + "test_the_owner_rates_a_completed_visit_once_and_reads_it_back")),
 ("P-D2R-CO13-SCORE-UNBOUNDED", [(VR, " or r.score not in SCORES:", ":")], PY(T + "test_the_score_is_a_whole_number_from_1_to_5")),
 ("P-D2R-CO13-BOOL-SCORE-ACCEPTED", [(M, "    score: StrictInt                     # a JSON true is not a score of 1\n", "    score: int\n"),
   (VR, " or isinstance(r.score, bool)", "")], PY(T + "test_the_score_is_a_whole_number_from_1_to_5")),
 ("P-D2R-CO13-ANY-VET-READS", [(M, "(role == ROLE_VETERINARIAN and actor_id == c.veterinarian_id)", "role == ROLE_VETERINARIAN")],
  PY(T + "test_only_the_owner_rates_and_only_the_owners_vet_or_clinic_admin_reads")),
 ("P-D2R-CO13-PG-RATING-UNSCOPED", [(PGR, '"SELECT {self._C} FROM consultation_rating WHERE session_id = %s AND tenant_id = %s",\n                               (session_id, tenant_id)',
   '"SELECT {self._C} FROM consultation_rating WHERE session_id = %s",\n                               (session_id,)')], PY(PG)),
 ("P-D2R-CO13-UI-SCORE-NOT-SENT", [(PAGE, "body: JSON.stringify({ score: Number(f.get('score')),", "body: JSON.stringify({ score: 5,")], VT(UT)),
 ("P-D2R-CO13-UI-FORM-AFTER-RATING", [(PAGE, "      {state === 'form' && (\n", "      {(state === 'form' || state === 'rated') && (\n")], VT(UT)),
 ("P-D2R-CO13-UI-REFUSAL-SILENT", [(PAGE, "      {error && <p role=\"alert\" data-testid=\"rate-error\">", "      {false && error && <p role=\"alert\" data-testid=\"rate-error\">")], VT(UT)),
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
