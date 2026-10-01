"""MVC-EPC-D-001 D2f perturbations: X-22 (Sponsor ruling R16.3 Option B — licence validity on the Asia/Riyadh calendar)
and X-27 / J-O6 (R16.5 — a consultation's pet must be the selected owner's pet in the session tenant; owner consultation
screens). python3 perturb_epc_d_d2f.py <root>. ARMED = the named evidence FAILS. The J-O6 cases run the real full stack
(ports 8090/3100 must be free); the X-22 matrix case runs evidence/replay/2026-10-01-epc-d/x22_tz_matrix.py."""
import os
import subprocess
import sys
R = sys.argv[1].rstrip("/") + "/"
X22 = "petcare_api/tests/test_epc_d2f_x22_licence_calendar.py::"
X22PG = "petcare_api/tests/test_epc_d2f_x22_licence_postgres.py::"
X27 = "petcare_api/tests/test_epc_d2f_x27_consultation_pet.py::"
PY = lambda t: ["python3", "-m", "pytest", t, "-q", "-p", "no:cacheprovider"]
WEB = lambda f: ["npx", "vitest", "run", f]
JO6 = ["npx", "playwright", "test", "-c", "playwright.full.config.ts", "--project", "ar-desktop", "-g", "J-O6"]
MATRIX = ["python3", "evidence/replay/2026-10-01-epc-d/x22_tz_matrix.py", "."]
AUTH, LIC, PGR, M = "petcare_api/routers/auth.py", "petcare_api/licences.py", "petcare_api/postgres_repositories.py", "petcare_api/main.py"
MSG, ROOM, HOME = ("petcare_web/app/owner/consultations/messages/page.tsx", "petcare_web/app/owner/consultations/video/page.tsx",
                   "petcare_web/app/owner/page.tsx")
WT = "__tests__/epc-d2f-consultations.test.tsx"
REG_RIYADH = "        if licence_expiry < licence_calendar_date(now):  # X-22 (R16.3 Option B): the Asia/Riyadh calendar date\n"
REG_UTC = "        if licence_expiry < now.date():\n"
PET_CHECK = "    if pet is None or pet.owner_id != body.owner_id:\n        _audit(event_name=\"consultation.session.refused\""
PET_TENANT_ONLY = "    if pet is None:\n        _audit(event_name=\"consultation.session.refused\""
PET_NONE = "    if False:\n        _audit(event_name=\"consultation.session.refused\""
GATE = "setGate(a.offered !== true ? 'counsel' : a.video_capability !== true ? 'switch' : 'open'))"
P = [
 # X-22 — the registration rule, the calendar, both repositories, and the amended U10 under the timezone matrix
 ("P-D2F-X22-REGISTRATION-UTC", [(AUTH, REG_RIYADH, REG_UTC)],
  PY(X22 + "test_a_licence_that_expired_yesterday_in_riyadh_is_refused_though_it_is_still_today_in_utc")),
 ("P-D2F-X22-REGISTRATION-UTC-U10-MATRIX", [(AUTH, REG_RIYADH, REG_UTC)], MATRIX),
 ("P-D2F-X22-CALENDAR-ZONE-UTC", [(LIC, 'LICENCE_CALENDAR_ZONE = ZoneInfo("Asia/Riyadh")', 'LICENCE_CALENDAR_ZONE = ZoneInfo("UTC")')],
  PY(X22 + "test_the_licence_calendar_is_asia_riyadh_and_refuses_a_naive_instant")),
 ("P-D2F-X22-CALENDAR-ZONE-UTC-SERVED", [(LIC, 'LICENCE_CALENDAR_ZONE = ZoneInfo("Asia/Riyadh")', 'LICENCE_CALENDAR_ZONE = ZoneInfo("UTC")')],
  PY(X22 + "test_a_licence_that_expired_yesterday_in_riyadh_is_refused_though_it_is_still_today_in_utc")),
 ("P-D2F-X22-NAIVE-INSTANT-GUESSED", [(LIC, "    if at.tzinfo is None or at.utcoffset() is None:\n        raise ValueError(\"licence validity needs a timezone-aware instant\")\n", "")],
  PY(X22 + "test_the_licence_calendar_is_asia_riyadh_and_refuses_a_naive_instant")),
 ("P-D2F-X22-MEMORY-REPOSITORY-UTC", [(LIC, "validate_licence(lic, today=licence_calendar_date(lic.submitted_at))", "validate_licence(lic, today=lic.submitted_at.date())")],
  PY(X22 + "test_the_repository_judges_submission_on_the_riyadh_calendar")),
 ("P-D2F-X22-PG-REPOSITORY-UTC", [(PGR, "validate_licence(lic, today=licence_calendar_date(lic.submitted_at))", "validate_licence(lic, today=lic.submitted_at.date())")],
  PY(X22PG + "test_the_postgres_licence_repository_judges_on_the_riyadh_calendar")),
 # X-27 — the consultation's pet is the selected owner's, in the session tenant; the refusal is audited
 ("P-D2F-X27-PET-OWNER-UNCHECKED", [(M, PET_CHECK, PET_TENANT_ONLY)], PY(X27 + "test_another_owners_pet_is_refused")),
 ("P-D2F-X27-PET-OWNER-UNCHECKED-SELECTED", [(M, PET_CHECK, PET_TENANT_ONLY)],
  PY(X27 + "test_the_pet_is_checked_against_the_selected_owner_not_only_the_tenant")),
 ("P-D2F-X27-PET-UNCHECKED", [(M, PET_CHECK, PET_NONE)], PY(X27 + "test_a_nonexistent_pet_is_refused")),
 ("P-D2F-X27-FOREIGN-TENANT-PET", [(M, PET_CHECK, PET_NONE)], PY(X27 + "test_another_tenants_pet_is_refused")),
 ("P-D2F-X27-REFUSAL-UNAUDITED", [(M, "        _audit(event_name=\"consultation.session.refused\", actor_id=actor_id,",
                                   "        (lambda **_: None)(event_name=\"consultation.session.refused\", actor_id=actor_id,")],
  PY(X27 + "test_another_owners_pet_is_refused")),
 ("P-D2F-X27-PET-UNCHECKED-SERVED", [(M, PET_CHECK, PET_NONE)], JO6),
 # J-O6 owner screens — only the message text leaves the browser; the video room stays closed unless the server opens it
 ("P-D2F-WEB-MESSAGE-SENDS-OWNER", [(MSG, "body: JSON.stringify({ body }) })", "body: JSON.stringify({ body, owner_id: 'u-self' }) })")], WEB(WT)),
 ("P-D2F-WEB-VIDEO-ROOM-UNGATED", [(ROOM, GATE, "setGate('open'))")], WEB(WT)),
 ("P-D2F-VIDEO-ROOM-UNGATED-SERVED", [(ROOM, GATE, "setGate('open'))")], JO6),
 ("P-D2F-HOME-NO-CONSULTATIONS-ENTRY", [(HOME, 'href="/owner/consultations" data-testid="owner-open-consultations"',
                                         'href="/owner" data-testid="owner-open-consultations"')], JO6),
]
res = []
for pid, edits, cmd in P:
    files = sorted({f for f, _, _ in edits})
    orig = {f: open(R + f, 'rb').read() for f in files}
    try:
        for f, old, new in edits:
            s = open(R + f).read(); assert s.count(old) == 1, (pid, f, s.count(old)); open(R + f, 'w').write(s.replace(old, new))
        cwd = R + "petcare_web" if cmd[0] == "npx" else R
        rc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=2400, env={**os.environ, "CI": "1"})
        out = [l for l in (rc.stdout + rc.stderr).splitlines() if "passed" in l or "failed" in l or "Tests " in l or "X22_TZ_MATRIX" in l][-1:]
    finally:
        for f, b in orig.items(): open(R + f, 'wb').write(b)
    for f, b in orig.items(): assert open(R + f, 'rb').read() == b
    res.append((pid, "ARMED" if rc.returncode != 0 else "VACUOUS")); print(pid, res[-1][1], out, flush=True)
print("ARMED=%d VACUOUS=%d" % (sum(r[1] == "ARMED" for r in res), sum(r[1] == "VACUOUS" for r in res)))
