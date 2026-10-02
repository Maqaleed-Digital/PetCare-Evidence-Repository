"""MVC-EPC-D-001 D2h perturbations: X-30 establishment-licence enforcement on order fulfilment (Sponsor ruling R18.3).
python3 perturb_epc_d_d2h.py <root>. ARMED = the named test FAILS."""
import os
import subprocess
import sys
R = sys.argv[1].rstrip("/") + "/"
T = "petcare_api/tests/test_epc_d2h_x30_establishment_licence.py::"
PY = lambda t: ["python3", "-m", "pytest", t, "-q", "-p", "no:cacheprovider"]
M, EST = "petcare_api/main.py", "petcare_api/establishment_licences.py"
MIG = "petcare_runtime/migrations/0060_epc_d2h_establishment_licence.sql"
CHECK = "    if est_lic.valid_on(ESTABLISHMENT_LICENCE_REPO.for_location(body.location_id, tenant_id=tenant_id), ksa_date(now)) is None:\n"
P = [
 ("P-D2H-X30-CHECK-REMOVED", [(M, CHECK, "    if False:\n")], PY(T + "test_a_location_with_no_licence_is_refused_audited_and_nothing_moves")),
 ("P-D2H-X30-UTC-DATE", [(M, CHECK, CHECK.replace("ksa_date(now)", "now.date()"))],
  PY(T + "test_the_licence_is_valid_through_its_expiry_day_on_the_riyadh_calendar")),
 ("P-D2H-X30-ANY-TENANT", [(M, CHECK, "    if est_lic.valid_on([l for l in ESTABLISHMENT_LICENCE_REPO._rows.values() if l.location_id == body.location_id], ksa_date(now)) is None:\n")],
  PY(T + "test_another_tenants_licence_for_the_location_is_refused")),
 ("P-D2H-X30-EXPIRED-ACCEPTED", [(EST, "    live = [l for l in licences if l.expires_on >= on]\n", "    live = list(licences)\n")],
  PY(T + "test_an_expired_licence_is_refused")),
 ("P-D2H-X30-UNAUDITED", [(M, "        _audit(event_name=\"order.delivery.refused\",", "        (lambda **_: None)(event_name=\"order.delivery.refused\",")],
  PY(T + "test_a_location_with_no_licence_is_refused_audited_and_nothing_moves")),
 ("P-D2H-X30-ROUTE-ANY-ROLE", [(M, "    if actor_role != ROLE_PLATFORM_ADMIN:\n        raise HTTPException(403, \"Only a platform administrator records establishment licences\")\n", "")],
  PY(T + "test_only_a_platform_administrator_records_a_licence_for_a_location_of_its_tenant")),
 ("P-D2H-X30-ROUTE-ANY-LOCATION", [(M, "    if INVENTORY_REPO.get_location(body.location_id, tenant_id=tenant_id) is None:\n        raise HTTPException(404, \"No such location in this tenant\")\n", "")],
  PY(T + "test_only_a_platform_administrator_records_a_licence_for_a_location_of_its_tenant")),
 ("P-D2H-X30-PG-BLANK-NUMBER", [(MIG, "    licence_number TEXT NOT NULL CHECK (char_length(btrim(licence_number)) > 0 AND char_length(licence_number) <= 200),", "    licence_number TEXT NOT NULL,")],
  PY("petcare_api/tests/test_epc_d2h_establishment_licence_postgres.py")),
]
res = []
for pid, edits, cmd in P:
    files = sorted({f for f, _, _ in edits})
    orig = {f: open(R + f, 'rb').read() for f in files}
    try:
        for f, old, new in edits:
            s = open(R + f).read(); assert s.count(old) == 1, (pid, f, s.count(old)); open(R + f, 'w').write(s.replace(old, new))
        rc = subprocess.run(cmd, cwd=R, capture_output=True, text=True, timeout=1800)
        out = [l for l in (rc.stdout + rc.stderr).splitlines() if "passed" in l or "failed" in l][-1:]
    finally:
        for f, b in orig.items(): open(R + f, 'wb').write(b)
    for f, b in orig.items(): assert open(R + f, 'rb').read() == b
    res.append((pid, "ARMED" if rc.returncode != 0 else "VACUOUS")); print(pid, res[-1][1], out, flush=True)
print("ARMED=%d VACUOUS=%d" % (sum(r[1] == "ARMED" for r in res), sum(r[1] == "VACUOUS" for r in res)))
