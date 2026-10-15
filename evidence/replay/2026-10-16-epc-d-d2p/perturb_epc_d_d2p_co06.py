"""MVC-EPC-D-001 D2p perturbations: CO-06 pre-visit intake with photos (owner's upcoming booking, once; images <= 5; ordered;
owner or clinic veterinarian reads). python3 perturb_epc_d_d2p_co06.py <root>. ARMED = the named test FAILS."""
import subprocess
import sys
R = sys.argv[1].rstrip("/") + "/"
T = "petcare_api/tests/test_epc_d2p_co06_previsit_intake.py::"
PG = "petcare_api/tests/test_epc_d2p_co06_previsit_intake_postgres.py"
PY = lambda t: ["python3", "-m", "pytest", t, "-q", "-p", "no:cacheprovider"]
VT = lambda t: ["npx", "vitest", "run", t]
M, PV, PGR = "petcare_api/main.py", "petcare_api/previsit_intake.py", "petcare_api/postgres_repositories.py"
PAGE = "petcare_web/app/owner/appointments/[bookingId]/intake/page.tsx"
UT = "__tests__/co06-previsit-intake.test.tsx"
P = [
 ("P-D2P-CO06-PAST-BOOKING-ACCEPTED", [(M, "    if b.status != bk.BOOKED or b.starts_at <= now:\n", "    if b.status != bk.BOOKED:\n")],
  PY(T + "test_only_an_upcoming_booked_appointment_takes_an_intake")),
 ("P-D2P-CO06-CANCELLED-BOOKING-ACCEPTED", [(M, "    if b.status != bk.BOOKED or b.starts_at <= now:\n", "    if b.starts_at <= now:\n")],
  PY(T + "test_only_an_upcoming_booked_appointment_takes_an_intake")),
 ("P-D2P-CO06-SECOND-INTAKE-REPLACES", [(PV, "            raise IntakeExists(i.booking_id)\n", "            self._rows = {k: x for k, x in self._rows.items() if x.booking_id != i.booking_id}\n"),
   (M, "    if INTAKE_REPO.for_booking(booking_id, tenant_id=tenant_id) is not None:\n        raise HTTPException(409, {\"error\": \"INTAKE_ALREADY_SUBMITTED\"})\n", "")],
  PY(T + "test_one_intake_per_booking_a_second_submission_is_refused_and_the_first_stands")),
 ("P-D2P-CO06-DOCUMENT-ACCEPTED-AS-PHOTO", [(M, "        if ctype not in pvi.PHOTO_CONTENT_TYPES:\n            raise HTTPException(400, {\"error\": \"PHOTO_NOT_IMAGE\"})\n", ""),
   (PV, "        if p.content_type not in PHOTO_CONTENT_TYPES:\n            raise RepositoryDenied(f\"a photo is one of {sorted(PHOTO_CONTENT_TYPES)}\")\n", "")],
  PY(T + "test_photos_are_images_at_most_five_and_a_refusal_stores_nothing")),
 ("P-D2P-CO06-PHOTO-LIMIT-DROPPED", [(M, "    if len(photos) > pvi.MAX_PHOTOS:\n", "    if False:\n"),
   (PV, "    if len(i.photos) > MAX_PHOTOS:\n        raise RepositoryDenied(f\"at most {MAX_PHOTOS} photos\")\n", "")],
  PY(T + "test_photos_are_images_at_most_five_and_a_refusal_stores_nothing")),
 ("P-D2P-CO06-ANOTHER-OWNER-READS", [(M, "    if role == ROLE_OWNER:\n        if b is None or b.owner_id != actor_id:\n", "    if role == ROLE_OWNER:\n        if b is None:\n")],
  PY(T + "test_another_owner_another_tenant_or_another_role_cannot_reach_it")),
 ("P-D2P-CO06-ADMIN-READS", [(M, "    else:\n        raise HTTPException(403, \"Only the owner or a veterinarian of the clinic reads a pre-visit intake\")\n", "")],
  PY(T + "test_another_owner_another_tenant_or_another_role_cannot_reach_it")),
 ("P-D2P-CO06-PHOTO-SERVED-INLINE", [(M, "headers={\"Content-Disposition\": 'attachment; filename=\"intake-photo\"'})", "headers={})")],
  PY(T + "test_a_photo_downloads_as_an_attachment_with_the_exact_bytes")),
 ("P-D2P-CO06-FUTURE-SYMPTOMS-ACCEPTED", [(PV, "    if i.symptoms_since is not None and i.symptoms_since > i.submitted_at.date():\n", "    if False:\n")],
  PY(T + "test_the_fields_are_validated")),
 ("P-D2P-CO06-PG-PHOTO-ORDER-BY-ID", [(PGR, '"ORDER BY position", (r[0], tenant_id)', '"ORDER BY uploaded_at, photo_id", (r[0], tenant_id)')],
  PY(PG)),
 ("P-D2P-CO06-UI-PHOTOS-NOT-SENT", [(PAGE, "    files.forEach(f => body.append('photos', f))\n", "")], VT(UT)),
 ("P-D2P-CO06-UI-FORM-AFTER-SUBMIT", [(PAGE, "      {state === 'form' && (\n", "      {(state === 'form' || state === 'submitted') && (\n")], VT(UT)),
 ("P-D2P-CO06-UI-PHOTO-LIMIT-DROPPED", [(PAGE, "    if (files.length > MAX_PHOTOS) { setError('tooMany'); return }\n", "")], VT(UT)),
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
