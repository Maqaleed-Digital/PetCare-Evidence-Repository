"""MVC-EPC-D-001 D2e (J-O5 consultation booking; X-26 no client-supplied identity on appointment routes, Sponsor ruling
R11) perturbations. python3 perturb_epc_d_d2e.py <root>. ARMED = the named test FAILS. The J-O5 case runs the real full
stack (ports 8090/3100 must be free)."""
import os
import subprocess
import sys
R = sys.argv[1].rstrip("/") + "/"
BT = "petcare_api/tests/test_epc_d2e_booking.py::"
PG = "petcare_api/tests/test_epc_d2e_booking_postgres.py::"
PY = lambda t: ["python3", "-m", "pytest", t, "-q", "-p", "no:cacheprovider"]
WEB = lambda f: ["npx", "vitest", "run", f]
JO5 = ["npx", "playwright", "test", "-c", "playwright.full.config.ts", "--project", "ar-desktop", "-g", "J-O5"]
M, BK = "petcare_api/main.py", "petcare_api/bookings.py"
MIG = "petcare_runtime/migrations/0058_epc_d2e_consultation_booking.sql"
BOOK, APPTS, HOME = "petcare_web/app/owner/book/page.tsx", "petcare_web/app/owner/appointments/page.tsx", "petcare_web/app/owner/page.tsx"
WT = "__tests__/epc-d2e-booking.test.tsx"
P = [
 # X-26 / R11 — the legacy stub never stores a client-supplied owner
 ("P-D2E-LEGACY-BODY-OWNER", [(M, "        \"owner_id\": actor_id if actor_role == ROLE_OWNER else None,\n", "        \"owner_id\": body.owner_id,\n")],
  PY(BT + "test_the_legacy_appointment_stub_stores_the_session_owner_not_the_body")),
 # J-O5 selectors validated against the session tenant
 ("P-D2E-PET-OWNER-UNCHECKED", [(M, "    if pet is None or pet.owner_id != actor_id:\n        raise HTTPException(404, \"Pet not found\")\n    _tenant_veterinarian(",
                                 "    if pet is None:\n        raise HTTPException(404, \"Pet not found\")\n    _tenant_veterinarian(")],
  PY(BT + "test_an_owner_cannot_book_for_a_pet_that_is_not_theirs")),
 ("P-D2E-VET-ANY-TENANT", [(M, "    if ident is None or ident.tenant_id != tenant_id or ident.role != ROLE_VETERINARIAN or ident.disabled_at:\n",
                            "    if ident is None or ident.role != ROLE_VETERINARIAN or ident.disabled_at:\n")],
  PY(BT + "test_the_veterinarian_must_be_a_veterinarian_of_the_session_tenant")),
 ("P-D2E-VET-ANY-ROLE", [(M, " or ident.role != ROLE_VETERINARIAN or ident.disabled_at:\n        raise HTTPException(400, {\"error\": \"VETERINARIAN_NOT_IN_TENANT\"})",
                          " or ident.disabled_at:\n        raise HTTPException(400, {\"error\": \"VETERINARIAN_NOT_IN_TENANT\"})")],
  PY(BT + "test_the_veterinarian_must_be_a_veterinarian_of_the_session_tenant")),
 ("P-D2E-NOT-OWNER-ONLY", [(M, "    if role != ROLE_OWNER:\n        raise HTTPException(403, {\"error\": \"OWNER_ONLY\"})\n", "")],
  PY(BT + "test_booking_routes_are_for_owners_only")),
 # another owner's booking: invisible and unchangeable
 ("P-D2E-CHANGE-OTHERS-BOOKING", [(M, "    if b is None or b.owner_id != actor_id:\n        raise HTTPException(404, \"Booking not found\")",
                                   "    if b is None:\n        raise HTTPException(404, \"Booking not found\")")],
  PY(BT + "test_another_owner_can_neither_see_nor_change_a_booking")),
 ("P-D2E-LIST-WHOLE-TENANT", [(BK, "if b.owner_id == owner_id and b.tenant_id == tenant_id),", "if b.tenant_id == tenant_id),")],
  PY(BT + "test_another_owner_can_neither_see_nor_change_a_booking")),
 # one live booking per veterinarian slot — repository, database index, and the offered slots
 ("P-D2E-DOUBLE-BOOKING", [(BK, "        validate_booking(b)\n        if self._clash(b, b.starts_at):\n            raise SlotTaken(\"that slot is already booked\")\n",
                            "        validate_booking(b)\n")],
  PY(BT + "test_a_slot_is_held_by_one_live_booking_and_freed_by_cancellation")),
 ("P-D2E-PG-NO-SLOT-INDEX", [(MIG, "CREATE UNIQUE INDEX IF NOT EXISTS consultation_booking_one_live_per_slot",
                              "CREATE INDEX IF NOT EXISTS consultation_booking_one_live_per_slot")],
  PY(PG + "test_one_live_booking_per_veterinarian_slot_is_enforced_by_the_database")),
 ("P-D2E-TAKEN-SLOT-OFFERED", [(M, " if bk.is_bookable_instant(s, now=now) and s not in taken]", " if bk.is_bookable_instant(s, now=now)]")],
  PY(BT + "test_an_owner_books_views_reschedules_and_cancels_their_own_consultation")),
 ("P-D2E-PAST-SLOT-BOOKABLE", [(BK, "    if at.tzinfo is None or at <= now:\n", "    if at.tzinfo is None:\n")],
  PY(BT + "test_only_future_default_hour_slots_are_bookable")),
 # SQ-2 video switch; audit of every booking write
 ("P-D2E-VIDEO-UNSWITCHED", [(M, "    if body.mode == bk.VIDEO and not vid.capability_enabled(os.environ):\n", "    if False:\n")],
  PY(BT + "test_video_mode_stays_behind_its_switch")),
 ("P-D2E-WRITE-UNAUDITED", [(M, "    _audit(event_name=event, actor_id=actor_id, actor_role=actor_role, tenant_id=tenant_id,\n           resource_type=\"consultation_booking\"",
                             "    (lambda **_: None)(event_name=event, actor_id=actor_id, actor_role=actor_role, tenant_id=tenant_id,\n           resource_type=\"consultation_booking\"")],
  PY(BT + "test_an_owner_books_views_reschedules_and_cancels_their_own_consultation")),
 # CO-05 / CO-07 screens: only selectors leave the browser; cancellation needs confirmation; served entry from home
 ("P-D2E-WEB-SENDS-OWNER", [(BOOK, "{ pet_id: pet, veterinarian_id: vet, starts_at: slot,", "{ owner_id: 'u-self', pet_id: pet, veterinarian_id: vet, starts_at: slot,")],
  WEB(WT)),
 ("P-D2E-WEB-ONE-CLICK-CANCEL", [(APPTS, "onClick={() => setConfirming(b.booking_id)}", "onClick={() => cancel(b.booking_id)}")], WEB(WT)),
 ("P-D2E-HOME-NO-BOOKING-ENTRY", [(HOME, "href=\"/owner/book\" data-testid=\"owner-open-book\"", "href=\"/owner\" data-testid=\"owner-open-book\"")], JO5),
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
