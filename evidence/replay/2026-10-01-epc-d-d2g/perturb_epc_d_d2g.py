"""MVC-EPC-D-001 D2g perturbations: X-22 clinical-act lapse (R17.2), X-28 + calendar-date sweep (R17.4), J-O7 owner
prescriptions (FR-14 owner part). python3 perturb_epc_d_d2g.py <root>. ARMED = the named evidence FAILS. J-O7 full-stack cases
run the real stack (ports 8090/3100 must be free); the matrix case runs evidence/replay/2026-10-01-epc-d-d2g/x22_lapse_tz_matrix.py."""
import os
import subprocess
import sys
R = sys.argv[1].rstrip("/") + "/"
PY = lambda t: ["python3", "-m", "pytest", t, "-q", "-p", "no:cacheprovider"]
WEB = lambda f: ["npx", "vitest", "run", f]
JO7 = ["npx", "playwright", "test", "-c", "playwright.full.config.ts", "--project", "ar-desktop", "-g", "J-O7"]
LAPSE = "petcare_api/tests/test_epc_d2g_x22_clinical_lapse.py"
X28 = "petcare_api/tests/test_epc_d2g_x28_ksa_dates.py::"
JT = "petcare_api/tests/test_epc_d2g_jo7_owner_prescriptions.py::"
LIC, M, ORD, REM, KSA = ("petcare_api/licences.py", "petcare_api/main.py", "petcare_api/orders.py", "petcare_api/reminders.py",
                         "petcare_api/ksa_calendar.py")
MIG = "petcare_runtime/migrations/0059_epc_d2g_owner_prescription_upload.sql"
KT, NOTIF = "petcare_web/lib/ksaTime.ts", "petcare_web/app/owner/notifications/page.tsx"
RXP, HOME = "petcare_web/app/owner/prescriptions/page.tsx", "petcare_web/app/owner/page.tsx"
LAPSE_RIYADH = "time(0), tzinfo=LICENCE_CALENDAR_ZONE)"
LAPSE_UTC = "time(0), tzinfo=timezone.utc)"
P = [
 # X-22 (R17.2) — the clinical-act lapse back to UTC midnight
 ("P-D2G-X22-LAPSE-UTC", [(LIC, LAPSE_RIYADH, LAPSE_UTC)], PY(LAPSE)),
 ("P-D2G-X22-LAPSE-UTC-U10", [(LIC, LAPSE_RIYADH, LAPSE_UTC)],
  PY("petcare_api/tests/test_fr05_licence.py::test_the_licence_expiry_is_rechecked_at_the_moment_of_each_clinical_act")),
 ("P-D2G-X22-LAPSE-UTC-MATRIX", [(LIC, LAPSE_RIYADH, LAPSE_UTC)],
  ["python3", "evidence/replay/2026-10-01-epc-d-d2g/x22_lapse_tz_matrix.py", "."]),
 # X-28 / R17.4 — receipt and reminder dates, the KSA calendar, the web formatter and its guard
 ("P-D2G-X28-RECEIPT-UTC", [(ORD, 'f"Issued: {ksa_date(issued_at).isoformat()}"', 'f"Issued: {issued_at.date().isoformat()}"'),
                            (ORD, 'f"تاريخ الإصدار: {ksa_date(issued_at).isoformat()}"', 'f"تاريخ الإصدار: {issued_at.date().isoformat()}"')],
  PY(X28 + "test_the_receipt_issue_date_is_the_riyadh_date")),
 ("P-D2G-X28-REMINDER-UTC", [(REM, "    when = ksa_date(item.due_at).isoformat()", "    when = item.due_at.date().isoformat()")],
  PY(X28 + "test_the_reminder_due_date_is_the_riyadh_date")),
 ("P-D2G-X28-KSA-ZONE-UTC", [(KSA, 'KSA_ZONE = ZoneInfo("Asia/Riyadh")', 'KSA_ZONE = ZoneInfo("UTC")')],
  PY(X28 + "test_the_ksa_calendar_is_asia_riyadh_and_refuses_a_naive_instant")),
 ("P-D2G-WEB-KSA-FORMAT-HOST-CLOCK", [(KT, "{ ...options, timeZone: KSA_TIME_ZONE }", "options")],
  WEB("__tests__/epc-d2g-ksa-dates.test.ts")),
 ("P-D2G-WEB-RAW-DATE-RENDER", [(NOTIF, "  const when = (iso: string) => formatKsa(iso, lang,\n",
                                 "  const when = (iso: string) => new Date(iso).toLocaleString(lang === 'ar' ? 'ar-SA' : 'en-GB',\n")],
  WEB("__tests__/epc-d2g-ksa-dates.test.ts")),
 # J-O7 — own pets only, own uploads only, download never inline, vet-only queue, DB status check, audited, served entry
 ("P-D2G-JO7-UPLOAD-ANY-PET", [(M, "    if pet is None or pet.owner_id != owner_id:\n        raise HTTPException(404, \"Pet not found\")  # 404, not 403: never confirm another owner's pet exists",
                                "    if pet is None:\n        raise HTTPException(404, \"Pet not found\")  # 404, not 403: never confirm another owner's pet exists")],
  PY(JT + "test_an_owner_cannot_upload_for_or_see_another_owners_pet")),
 ("P-D2G-JO7-LIST-OTHER-PETS", [(M, "for rx in PRESCRIPTION_REPO.list_by_status(tenant_id=tenant_id, status=status) if rx.pet_id in pets]",
                                 "for rx in PRESCRIPTION_REPO.list_by_status(tenant_id=tenant_id, status=status)]")],
  PY(JT + "test_an_owner_sees_the_prescriptions_issued_for_their_own_pets")),
 ("P-D2G-JO7-DOWNLOAD-OTHERS", [(M, "    if u is None or u.owner_id != actor_id:\n        raise HTTPException(404, \"Upload not found\")",
                                 "    if u is None:\n        raise HTTPException(404, \"Upload not found\")")],
  PY(JT + "test_an_owner_cannot_upload_for_or_see_another_owners_pet")),
 ("P-D2G-JO7-INLINE-DOCUMENT", [(M, "    return Response(content=payload, media_type=SERVED_CONTENT_TYPE,\n                    headers={\"Content-Disposition\": 'attachment; filename=\"prescription-upload\"'})",
                                 "    return Response(content=payload, media_type=u.content_type)")],
  PY(JT + "test_an_owner_uploads_an_external_prescription_for_verification")),
 ("P-D2G-JO7-QUEUE-ANY-ROLE", [(M, "    if role != ROLE_VETERINARIAN:\n        raise HTTPException(403, \"Only a veterinarian verifies prescriptions\")\n    tenant_id = require_tenant(request)\n    _rx_read_audit(request, \"prescription.owner_upload_queue_viewed\"",
                                "    tenant_id = require_tenant(request)\n    _rx_read_audit(request, \"prescription.owner_upload_queue_viewed\"")],
  PY(JT + "test_the_routes_are_owner_only_and_the_queue_is_veterinarian_only")),
 ("P-D2G-JO7-NOT-OWNER-ONLY", [(M, "    actor_id, actor_role, tenant_id = _owner_session(request, role)\n    pets = {p.pet_id",
                                "    actor_id, actor_role = _actor(request); tenant_id = require_tenant(request)\n    pets = {p.pet_id")],
  PY(JT + "test_the_routes_are_owner_only_and_the_queue_is_veterinarian_only")),
 ("P-D2G-JO7-UNAUDITED", [(M, "    _audit(event_name=\"prescription.owner_uploaded\",", "    (lambda **_: None)(event_name=\"prescription.owner_uploaded\",")],
  PY(JT + "test_every_upload_is_audited")),
 ("P-D2G-JO7-PG-STATUS-UNCHECKED", [(MIG, "    status TEXT NOT NULL CHECK (status IN ('AWAITING_VERIFICATION')),", "    status TEXT NOT NULL,")],
  PY("petcare_api/tests/test_epc_d2g_owner_prescription_upload_postgres.py")),
 ("P-D2G-JO7-WEB-SENDS-OWNER", [(RXP, "    data.append('file', file)\n", "    data.append('file', file)\n    data.append('owner_id', 'u-self')\n")],
  WEB("__tests__/epc-d2g-prescriptions.test.tsx")),
 ("P-D2G-JO7-HOME-NO-ENTRY", [(HOME, 'href="/owner/prescriptions" data-testid="owner-open-prescriptions"', 'href="/owner" data-testid="owner-open-prescriptions"')], JO7),
 ("P-D2G-JO7-LIST-OTHER-PETS-SERVED", [(M, "for rx in PRESCRIPTION_REPO.list_by_status(tenant_id=tenant_id, status=status) if rx.pet_id in pets]",
                                        "for rx in PRESCRIPTION_REPO.list_by_status(tenant_id=tenant_id, status=status)]")], JO7),
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
        out = [l for l in (rc.stdout + rc.stderr).splitlines() if "passed" in l or "failed" in l or "Tests " in l or "MATRIX=" in l][-1:]
    finally:
        for f, b in orig.items(): open(R + f, 'wb').write(b)
    for f, b in orig.items(): assert open(R + f, 'rb').read() == b
    res.append((pid, "ARMED" if rc.returncode != 0 else "VACUOUS")); print(pid, res[-1][1], out, flush=True)
print("ARMED=%d VACUOUS=%d" % (sum(r[1] == "ARMED" for r in res), sum(r[1] == "VACUOUS" for r in res)))
