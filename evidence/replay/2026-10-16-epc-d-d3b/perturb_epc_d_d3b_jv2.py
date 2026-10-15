"""MVC-EPC-D-001 D3b perturbations: J-V2 availability and queue (published plan governs slots; default hours only when never
published; latest plan wins; plans validated; the queue is the veterinarian's own upcoming work). python3 perturb_epc_d_d3b_jv2.py
<root>. ARMED = the named test FAILS."""
import subprocess
import sys
R = sys.argv[1].rstrip("/") + "/"
T = "petcare_api/tests/test_epc_d3b_jv2_availability_queue.py::"
PG = "petcare_api/tests/test_epc_d3b_jv2_availability_postgres.py"
PY = lambda t: ["python3", "-m", "pytest", t, "-q", "-p", "no:cacheprovider"]
VT = lambda t: ["npx", "vitest", "run", t]
M, BK, AV, PGR = "petcare_api/main.py", "petcare_api/bookings.py", "petcare_api/availability.py", "petcare_api/postgres_repositories.py"
AVP, QP = "petcare_web/app/vet/availability/page.tsx", "petcare_web/app/vet/queue/page.tsx"
UT = "__tests__/jv2-availability-queue.test.tsx"
P = [
 ("P-D3B-JV2-PLAN-IGNORED-FOR-SLOTS", [(M, "    windows = _vet_windows(veterinarian_id, tenant_id)\n    return [s.isoformat()", "    windows = None\n    return [s.isoformat()")],
  PY(T + "test_published_windows_are_the_only_bookable_slots")),
 ("P-D3B-JV2-BOOKING-OUTSIDE-PLAN-ACCEPTED", [(M, "    if not bk.is_bookable_instant(at, now=datetime.now(timezone.utc), windows=_vet_windows(veterinarian_id, tenant_id)):",
   "    if not bk.is_bookable_instant(at, now=datetime.now(timezone.utc)):")], PY(T + "test_published_windows_are_the_only_bookable_slots")),
 ("P-D3B-JV2-EMPTY-PLAN-MEANS-DEFAULTS", [(BK, "    spans = [(OPENS, CLOSES)] if windows is None else", "    spans = [(OPENS, CLOSES)] if not windows else")],
  PY(T + "test_a_new_plan_never_moves_an_existing_booking_and_the_latest_plan_wins")),
 ("P-D3B-JV2-WRONG-WEEKDAY", [(BK, "for w in windows if w.weekday == on.weekday()]", "for w in windows if w.weekday == on.isoweekday() % 7]")],
  PY(T + "test_published_windows_are_the_only_bookable_slots")),
 ("P-D3B-JV2-FIRST-PLAN-WINS", [(AV, "        return max(mine, key=lambda p: (p.published_at, p.plan_id)) if mine else None", "        return min(mine, key=lambda p: (p.published_at, p.plan_id)) if mine else None")],
  PY(T + "test_a_new_plan_never_moves_an_existing_booking_and_the_latest_plan_wins")),
 ("P-D3B-JV2-OVERLAP-ACCEPTED", [(AV, "        if any(a.closes > b.opens for a, b in zip(day, day[1:])):", "        if False:")],
  PY(T + "test_an_invalid_schedule_is_refused_and_changes_nothing")),
 ("P-D3B-JV2-OFF-GRID-ACCEPTED", [(AV, "    return t.second == 0 and t.microsecond == 0 and t.minute % SLOT_MINUTES == 0", "    return True")],
  PY(T + "test_an_invalid_schedule_is_refused_and_changes_nothing")),
 ("P-D3B-JV2-QUEUE-SHOWS-CANCELLED", [(M, "                    if b.status == bk.BOOKED and b.starts_at > now]", "                    if b.starts_at > now]")],
  PY(T + "test_the_queue_is_the_veterinarians_own_upcoming_bookings_and_open_consultations")),
 ("P-D3B-JV2-QUEUE-SHOWS-COMPLETED", [(M, "                          if c.veterinarian_id == actor_id and CONSULTATION_REPO.outcome_of(c.session_id, tenant_id=tenant_id) is None]",
   "                          if c.veterinarian_id == actor_id]")], PY(T + "test_the_queue_is_the_veterinarians_own_upcoming_bookings_and_open_consultations")),
 ("P-D3B-JV2-QUEUE-OTHER-VET", [(M, "                          if c.veterinarian_id == actor_id and CONSULTATION_REPO", "                          if CONSULTATION_REPO")],
  PY(T + "test_the_queue_is_the_veterinarians_own_upcoming_bookings_and_open_consultations")),
 ("P-D3B-JV2-PG-LATEST-IS-OLDEST", [(PGR, '"AND tenant_id = %s ORDER BY published_at DESC, plan_id DESC LIMIT 1"', '"AND tenant_id = %s ORDER BY published_at ASC, plan_id ASC LIMIT 1"')],
  PY(PG)),
 ("P-D3B-JV2-UI-UNTICKED-DAY-SENT", [(AVP, "    const windows = ORDER.map(d => days[d]).filter((w): w is Window => !!w)", "    const windows = ORDER.map(d => days[d] ?? { weekday: d, opens: '09:00', closes: '17:00' })")],
  VT(UT)),
 ("P-D3B-JV2-UI-INTAKE-MARKER-WRONG", [(QP, "data-intake={a.intake_submitted ? 'true' : 'false'}", "data-intake=\"false\"")], VT(UT)),
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
