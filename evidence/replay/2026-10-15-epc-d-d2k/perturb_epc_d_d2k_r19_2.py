"""MVC-EPC-D-001 D2k perturbations: R19.2 licence record completeness (X-31 type/scope, X-32 evidence-document reference,
several licences per location). python3 perturb_epc_d_d2k_r19_2.py <root>. ARMED = the named test FAILS."""
import subprocess
import sys
R = sys.argv[1].rstrip("/") + "/"
T = "petcare_api/tests/test_epc_d2k_r19_2_licence_completeness.py::"
H = "petcare_api/tests/test_epc_d2h_x30_establishment_licence.py::"
PY = lambda t: ["python3", "-m", "pytest", t, "-q", "-p", "no:cacheprovider"]
EST, PG = "petcare_api/establishment_licences.py", "petcare_api/postgres_repositories.py"
MIG = "petcare_runtime/migrations/0061_epc_d2k_r19_2_licence_completeness.sql"
VALIDATE = "    for name in (\"licence_number\", \"issuing_authority\", \"basis\", \"location_id\", \"tenant_id\", \"recorded_by_actor_id\",\n                 *R19_2_FIELDS):\n"
VALIDATE_D2H = "    for name in (\"licence_number\", \"issuing_authority\", \"basis\", \"location_id\", \"tenant_id\", \"recorded_by_actor_id\"):\n"
LIVE = "    live = [l for l in licences if l.expires_on >= on and l.is_complete()]\n"
P = [
 ("P-D2K-R192-FIELDS-NOT-VALIDATED", [(EST, VALIDATE, VALIDATE_D2H)],
  PY(T + "test_each_r19_2_field_is_required_and_may_not_be_blank")),
 ("P-D2K-R192-INCOMPLETE-VALIDATES", [(EST, LIVE, "    live = [l for l in licences if l.expires_on >= on]\n")],
  PY(T + "test_an_incomplete_licence_never_validates_a_delivery")),
 ("P-D2K-R192-ONE-LICENCE-PER-LOCATION", [(EST, "        self._rows[lic.licence_id] = lic\n",
   "        self._rows = {k: v for k, v in self._rows.items() if (v.tenant_id, v.location_id) != (lic.tenant_id, lic.location_id)}\n        self._rows[lic.licence_id] = lic\n")],
  PY(T + "test_a_location_holds_more_than_one_licence_and_any_valid_one_suffices")),
 ("P-D2K-R192-FIRST-NOT-LATEST", [(EST, "    return max(live, key=lambda l: (l.expires_on, l.licence_id)) if live else None\n",
   "    return min(licences, key=lambda l: (l.expires_on, l.licence_id)) if live and min(licences, key=lambda l: l.expires_on).expires_on >= on else None\n")],
  PY(T + "test_two_licences_the_later_expiry_governs_on_the_riyadh_calendar")),
 ("P-D2K-R192-UTC-DATE", [("petcare_api/main.py", "ESTABLISHMENT_LICENCE_REPO.for_location(body.location_id, tenant_id=tenant_id), ksa_date(now))",
   "ESTABLISHMENT_LICENCE_REPO.for_location(body.location_id, tenant_id=tenant_id), now.date())")],
  PY(T + "test_two_licences_the_later_expiry_governs_on_the_riyadh_calendar")),
 ("P-D2K-R192-CLAIMS-REGISTRY-VERIFIED", [(EST, "        d[\"registry_verified\"] = False", "        d[\"registry_verified\"] = True ")],
  PY(T + "test_the_record_carries_every_r19_2_field_and_its_audit")),
 ("P-D2K-R192-PG-FIELDS-DROPPED", [(PG, "lic.expires_on, lic.basis, lic.recorded_by_actor_id, _to_db(lic.recorded_at), lic.licence_type,\n                          lic.scope, lic.evidence_document_ref))",
   "lic.expires_on, lic.basis, lic.recorded_by_actor_id, _to_db(lic.recorded_at), None,\n                          None, None))")],
  PY("petcare_api/tests/test_epc_d2k_r19_2_licence_postgres.py")),
 ("P-D2K-R192-PG-BLANK-ACCEPTED", [(MIG, "    CHECK (evidence_document_ref IS NULL OR (char_length(btrim(evidence_document_ref)) > 0 AND char_length(evidence_document_ref) <= 200));", ";")],
  PY("petcare_api/tests/test_epc_d2k_r19_2_licence_postgres.py")),
 # D2h's own perturbations whose anchor D2k moved or that its script never reached (finding D2K-D2H-PERTURBATION-ANCHOR): the
 # D2h script is committed evidence and is not edited; these re-anchor the same mutations on the D2k source.
 ("P-D2H-X30-EXPIRED-ACCEPTED@D2K", [(EST, LIVE, "    live = [l for l in licences if l.is_complete()]\n")],
  PY(H + "test_an_expired_licence_is_refused")),
 ("P-D2H-X30-UNAUDITED@D2K", [("petcare_api/main.py", "        _audit(event_name=\"order.delivery.refused\",", "        (lambda **_: None)(event_name=\"order.delivery.refused\",")],
  PY(H + "test_a_location_with_no_licence_is_refused_audited_and_nothing_moves")),
 ("P-D2H-X30-ROUTE-ANY-ROLE@D2K", [("petcare_api/main.py", "    if actor_role != ROLE_PLATFORM_ADMIN:\n        raise HTTPException(403, \"Only a platform administrator records establishment licences\")\n", "")],
  PY(H + "test_only_a_platform_administrator_records_a_licence_for_a_location_of_its_tenant")),
 ("P-D2H-X30-ROUTE-ANY-LOCATION@D2K", [("petcare_api/main.py", "    if INVENTORY_REPO.get_location(body.location_id, tenant_id=tenant_id) is None:\n        raise HTTPException(404, \"No such location in this tenant\")\n", "")],
  PY(H + "test_only_a_platform_administrator_records_a_licence_for_a_location_of_its_tenant")),
 ("P-D2H-X30-PG-BLANK-NUMBER@D2K", [("petcare_runtime/migrations/0060_epc_d2h_establishment_licence.sql", "    licence_number TEXT NOT NULL CHECK (char_length(btrim(licence_number)) > 0 AND char_length(licence_number) <= 200),", "    licence_number TEXT NOT NULL,")],
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
        out = [l for l in (rc.stdout + rc.stderr).splitlines() if "passed" in l or "failed" in l or "error" in l][-1:]
    finally:
        for f, b in orig.items(): open(R + f, 'wb').write(b)
    for f, b in orig.items(): assert open(R + f, 'rb').read() == b
    res.append((pid, "ARMED" if rc.returncode != 0 else "VACUOUS")); print(pid, res[-1][1], out, flush=True)
print("ARMED=%d VACUOUS=%d" % (sum(r[1] == "ARMED" for r in res), sum(r[1] == "VACUOUS" for r in res)))
