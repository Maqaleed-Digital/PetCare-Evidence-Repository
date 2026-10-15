"""MVC-EPC-D-001 D2o perturbations: CO-04 vaccination card (given = recorded completion; due = none; treatments excluded).
python3 perturb_epc_d_d2o_co04.py <root>. ARMED = the named test FAILS."""
import subprocess
import sys
R = sys.argv[1].rstrip("/") + "/"
T = "petcare_api/tests/test_epc_d2o_co04_vaccination_card.py::"
PG = "petcare_api/tests/test_epc_d2o_co04_vaccination_card_postgres.py"
PY = lambda t: ["python3", "-m", "pytest", t, "-q", "-p", "no:cacheprovider"]
VT = lambda t: ["npx", "vitest", "run", t]
RM, M, PGR = "petcare_api/reminders.py", "petcare_api/main.py", "petcare_api/postgres_repositories.py"
PAGE = "petcare_web/app/owner/pets/[petId]/vaccination-card/page.tsx"
UT = "__tests__/co04-vaccination-card.test.tsx"
P = [
 ("P-D2O-CO04-TREATMENT-ON-CARD", [(RM, "        if d.kind != VACCINATION:\n            continue\n", "")],
  PY(T + "test_a_treatment_is_not_a_vaccination")),
 ("P-D2O-CO04-OVERDUE-COUNTED-GIVEN", [(RM, "        c = completion_of(d.due_id)\n",
   "        c = completion_of(d.due_id) or (CareCompletion(d.due_id, d.tenant_id, d.recorded_by, d.due_at)\n"
   "                                        if d.due_at < datetime.now(d.due_at.tzinfo) else None)\n")],
  PY(T + "test_an_overdue_outstanding_vaccination_is_still_due_never_given")),
 ("P-D2O-CO04-GIVEN-DATE-UTC-NOT-RIYADH", [(RM, '"given_on": ksa_date(c.completed_at).isoformat()', '"given_on": c.completed_at.date().isoformat()')],
  PY(T + "test_the_given_date_is_the_riyadh_calendar_date_of_the_recorded_completion")),
 ("P-D2O-CO04-GIVEN-DATE-FROM-DUE-DATE", [(RM, '"given_on": ksa_date(c.completed_at).isoformat()', '"given_on": ksa_date(d.due_at).isoformat()')],
  PY(PG)),
 ("P-D2O-CO04-VET-NAME-DROPPED", [(RM, '"given_by": name_of(c.completed_by)', '"given_by": c.completed_by')],
  PY(T + "test_a_completed_vaccination_is_given_with_its_veterinarian_and_an_outstanding_one_is_due")),
 ("P-D2O-CO04-OWNER-SCOPE-DROPPED", [(M, "    pet, _a, _r, tenant_id = _pet_or_404(request, pet_id)\n",
   "    tenant_id = require_tenant(request)\n    pet = PET_REPO.get(pet_id, tenant_id=tenant_id)\n")],
  PY(T + "test_another_owners_or_another_tenants_pet_card_is_not_found")),
 ("P-D2O-CO04-PG-COMPLETION-UNSCOPED", [(PGR, '"WHERE due_id = %s AND tenant_id = %s", (due_id, tenant_id)).fetchall()\n        return None if not rows',
   '"WHERE due_id = %s", (due_id,)).fetchall()\n        return None if not rows')],
  PY(PG)),
 ("P-D2O-CO04-UI-PRINT-NOT-WIRED", [(PAGE, "onClick={() => window.print()}", "onClick={() => undefined}")], VT(UT)),
 ("P-D2O-CO04-UI-REFUSAL-SILENT", [(PAGE, "{failed && <p role=\"alert\">", "{false && failed && <p role=\"alert\">")], VT(UT)),
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
