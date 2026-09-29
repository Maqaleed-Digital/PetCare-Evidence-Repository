"""MVC-EPC-D-001 D2d (R10 reminder consent at dispatch, R12 scratch-cluster ownership, CO-01 owner home, CO-14 J-O10)
perturbations. python3 perturb_epc_d_d2d.py <root>. ARMED = the named test FAILS. The J-O10 case runs the real full
stack (ports 8090/3100 must be free)."""
import os
import subprocess
import sys
R = sys.argv[1].rstrip("/") + "/"
RC = "petcare_api/tests/test_epc_d2d_reminder_consent.py::"
OW = "petcare_api/tests/test_epc_d2d_scratch_ownership.py::"
PY = lambda t: ["python3", "-m", "pytest", t, "-q", "-p", "no:cacheprovider"]
WEB = lambda f: ["npx", "vitest", "run", f]
JO10 = ["npx", "playwright", "test", "-c", "playwright.full.config.ts", "--project", "ar-desktop", "-g", "J-O10"]
JO1 = ["npx", "playwright", "test", "-c", "playwright.full.config.ts", "--project", "ar-desktop", "-g", "J-O1"]
M, OC, H = "petcare_api/main.py", "petcare_api/owner_consent.py", "petcare_api/tests/pg_harness.py"
A, FLOWS = "petcare_api/routers/auth.py", "petcare_web/components/auth/AccountFlows.tsx"
HOME, NOTES = "petcare_web/app/owner/page.tsx", "petcare_web/app/owner/notifications/page.tsx"
P = [
 # R10 / X-25 — consent enforced at the FR-23 dispatch boundary, failing closed
 ("P-D2D-DISPATCH-IGNORES-CONSENT", [(M, "        if not admitted:\n", "        if False:\n")],
  PY(RC + "test_without_any_consent_event_nothing_is_dispatched_and_the_refusal_is_audited")),
 ("P-D2D-ABSENT-CONSENT-ADMITS", [(OC, "        return False, CONSENT_ABSENT\n", "        return True, CONSENT_ABSENT\n")],
  PY(RC + "test_without_any_consent_event_nothing_is_dispatched_and_the_refusal_is_audited")),
 ("P-D2D-REVOKED-CONSENT-ADMITS", [(OC, "        return False, CONSENT_REVOKED\n", "        return True, CONSENT_REVOKED\n")],
  PY(RC + "test_revoking_after_an_earlier_consent_stops_every_later_dispatch")),
 ("P-D2D-UNREADABLE-CONSENT-ADMITS", [(OC, "        return False, CONSENT_UNREADABLE\n", "        return True, CONSENT_UNREADABLE\n")],
  PY(RC + "test_an_unreadable_ledger_fails_closed_at_the_dispatch_boundary")),
 ("P-D2D-MALFORMED-CONSENT-ADMITS", [(OC, "        return False, CONSENT_MALFORMED\n", "        return True, CONSENT_MALFORMED\n")],
  PY(RC + "test_a_malformed_ledger_record_fails_closed_at_the_dispatch_boundary")),
 ("P-D2D-CONSENT-ANY-TENANT", [(OC, " or latest.user_id != owner_id or latest.tenant_id != tenant_id\n", " or latest.user_id != owner_id\n")],
  PY(RC + "test_the_dispatch_decision_admits_only_a_well_formed_grant")),
 ("P-D2D-WITHHOLD-UNAUDITED", [(M, "            _audit(event_name=\"reminder.withheld\",", "            (lambda **_: None)(event_name=\"reminder.withheld\",")],
  PY(RC + "test_without_any_consent_event_nothing_is_dispatched_and_the_refusal_is_audited")),
 # R12 — scratch-cluster cleanup only on positive ownership proof
 ("P-D2D-CLEANUP-WITHOUT-PROOF", [(H, "    proven, reason = ownership_proof(datadir, run_nonce=run_nonce)\n    if not proven:\n        return False, reason\n",
                                   "    proven, reason = True, \"PROVEN_HARNESS_OWNED\"\n")],
  PY(OW + "test_a_stopped_zero_connection_cluster_without_a_marker_is_refused")),
 ("P-D2D-UNMARKED-IS-OWNED", [(H, "    if not marker.is_file():\n        return False, \"UNMARKED\"\n", "    if not marker.is_file():\n        return True, \"PROVEN_HARNESS_OWNED\"\n")],
  PY(OW + "test_an_unmarked_directory_with_the_harness_name_is_refused")),
 ("P-D2D-COPIED-MARKER-TRANSFERS", [(H, "    if m.get(\"datadir\") != os.path.realpath(path):\n", "    if False:\n")],
  PY(OW + "test_a_marker_copied_from_a_proven_directory_does_not_transfer_ownership")),
 ("P-D2D-ANY-NAME-IS-OWNED", [(H, "    if not path.name.startswith(DATADIR_PREFIX):\n", "    if False:\n")],
  PY(OW + "test_an_unrelated_directory_is_refused")),
 ("P-D2D-HARNESS-UNMARKED", [(H, "    _write_marker(datadir, nonce)          # R12", "    pass  # _write_marker(datadir, nonce)          # R12")],
  PY(OW + "test_the_harness_marks_its_cluster_before_start_and_removes_only_that")),
 # CO-01 owner home — served, never a false empty and never a dead link
 # First design targeted surface-states.test.tsx and was VACUOUS there (its fetch stub answers [] — empty is then
 # correct); redesigned against the test that holds the server's answer back (receipt finding D2D-FIRST-ATTEMPT-VACUOUS).
 ("P-D2D-HOME-EMPTY-BEFORE-SERVER", [(HOME, ">('loading')", ">([])")], WEB("__tests__/epc-d2d-owner-home.test.tsx")),
 ("P-D2D-HOME-DEAD-LINK", [(HOME, "href=\"/owner/notifications\" data-testid=\"owner-open-notifications\"", "href=\"#\" data-testid=\"owner-open-notifications\"")],
  WEB("__tests__/owner.test.tsx")),
 # R13.3 — care reminders at signup: optional, unticked, only an explicit boolean true, never implied
 ("P-D2D-SIGNUP-REMINDERS-IMPLIED", [(A, "    if body.care_reminders is True:\n", "    if True:\n")],
  PY(RC + "test_an_owner_who_leaves_care_reminders_unticked_gives_no_reminder_consent")),
 ("P-D2D-SIGNUP-REMINDERS-LAX-BOOLEAN", [(A, "    care_reminders: StrictBool = False", "    care_reminders: bool = False")],
  PY(RC + "test_only_a_real_boolean_counts_as_a_care_reminders_choice")),
 ("P-D2D-SIGNUP-REMINDERS-PRETICKED", [(FLOWS, "  const [reminders, setReminders] = useState(false)", "  const [reminders, setReminders] = useState(true)")], JO1),
 # R13.5 — an admin's owner_id on POST /api/pets is a validated selector, never authority
 ("P-D2D-PET-OWNER-UNVALIDATED", [(M, "        if ident is None or ident.tenant_id != tenant_id or ident.role != ROLE_OWNER:\n"
                                      "            raise HTTPException(400, \"owner_id is not an owner of this tenant\")\n", "")],
  PY("petcare_api/tests/test_epc_d2d_pet_owner_selector.py::test_an_admin_may_create_a_pet_only_for_an_owner_of_their_tenant")),
 # CO-14 / J-O10 — the centre shows what the server sent, in the owner's language
 ("P-D2D-CENTRE-DROPS-REMINDERS", [(NOTES, "          ...reminders.map(", "          ...reminders.slice(0, 0).map(")], JO10),
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
