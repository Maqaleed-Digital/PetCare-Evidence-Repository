import subprocess, hashlib, sys
R=sys.argv[1].rstrip("/")+"/"
T="petcare_api/tests/"
PY=lambda n:["python3","-m","pytest",T+n,"-q","-p","no:cacheprovider"]
VT=lambda f,name=None:["npx","vitest","run","__tests__/"+f]+(["-t",name] if name else [])
HDR='request.headers.get("X-Actor-Id")'
M="petcare_api/main.py"
P=[
 # U1 · FR-02 AC-04
 ("U1-P-ACTOR-HEADER",[(M,'    _pet_audit("pet.profile.created", actor_id, actor_role,','    _pet_audit("pet.profile.created", '+HDR+', actor_role,')],
  PY("test_pet_audit_actor.py::test_e1_client_supplied_actor_has_no_effect_on_audit_record")),
 # U2 · FR-02
 ("U2-P-AC01",[("petcare_api/pets.py","        return pet if pet is not None and pet.tenant_id == tenant_id else None","        return pet")],
  PY("test_pet_profile.py::test_ac01_profile_is_unreadable_from_another_tenant")),
 ("U2-P-AC02",[(M,'            "prescriptions": sorted(prescriptions, key=lambda r: (r["issued_at"], r["prescription_id"])),','            "prescriptions": [],')],
  PY("test_pet_profile.py::test_ac02_history_shows_lab_result_and_prescription")),
 ("U2-P-AC03",[("petcare_api/pets.py","    if ident.id_type not in IDENTIFICATION_TYPES:","    if False:")],
  PY("test_pet_profile.py::test_ac03_identification_is_never_free_text")),
 # U3 · FR-09
 ("U3-P-AC01",[("petcare_web/app/owner/emergency/page.tsx","                    {t(sev === 'critical' ? s.severityBadgeCritical\n                       : sev === 'urgent' ? s.severityBadgeUrgent : s.severityBadgeRoutine)}","                    {sev}")],
  VT("language-fr09.test.tsx","/owner/emergency: Arabic by default")),
 ("U3-P-AC02",[(M,"    stored = PREFERENCE_REPO.get_language(actor_id)\n    return {\"language\": stored or DEFAULT_LANGUAGE","    stored = None\n    return {\"language\": stored or DEFAULT_LANGUAGE")],
  PY("test_language_preference.py::test_choice_survives_a_new_session")),
 # U4 · FR-01 session identity
 ("U4-P-ACTOR-HEADER",[(M,"    actor_id, actor_role = _actor(request)  # AC-FR-01-01: never a client-supplied actor\n    if role not in {ROLE_VETERINARIAN, ROLE_PLATFORM_ADMIN}:",
                          "    actor_id, actor_role = "+HDR+", _actor(request)[1]\n    if role not in {ROLE_VETERINARIAN, ROLE_PLATFORM_ADMIN}:")],
  PY("test_fr01_session_identity.py::test_client_actor_header_is_ignored_on_appointments_and_consultations")),
 # U5 · FR-01 practitioner authority
 ("U5-P-ROLE-ALONE",[(M,"    authority = _require_practitioner_authority(actor_id, tenant_id)  # AC-FR-01-02: live attribute at the act\n    rx_id = str(uuid4())",
                        "    authority = None  # role alone\n    rx_id = str(uuid4())"),
                      (M,'        event_name="prescription.issued",\n        reason_code=f"authority:{authority.grant_id}",',
                         '        event_name="prescription.issued",\n        reason_code=f"authority:{getattr(authority, \'grant_id\', None)}",')],
  PY("test_practitioner_authority.py::test_role_alone_is_refused_and_the_refusal_names_the_attribute")),
 # U6 · FR-27 dashboard
 ("U6-P-AC01",[("petcare_web/app/pharmacy/page.tsx","  useEffect(() => {\n    const id = setInterval(async () => {\n      try {\n        const res = await call('/api/prescriptions/queue/awaiting-dispense')\n        if (res.ok) setQueue(await res.json())\n      } catch { /* keep the last good queue */ }\n    }, QUEUE_REFRESH_MS)\n    return () => clearInterval(id)\n  }, [])",
                "  useEffect(() => {}, [])")],
  VT("fr27-dashboard.test.tsx","appears with no user action")),
 ("U6-P-AC03",[(M,'        event_name="prescription.dispensed",\n        reason_code=f"authority:{authority.grant_id}",\n        actor_id=actor_id,',
                  '        event_name="prescription.dispensed",\n        reason_code=f"authority:{authority.grant_id}",\n        actor_id='+HDR+',')],
  PY("test_option_a_workflow.py::test_j_every_step_is_audited_with_a_server_derived_actor")),
 ("U6-P-AC04",[("petcare_web/app/pharmacy/page.tsx","    <main className=\"stack\" dir={isAr ? 'rtl' : 'ltr'}>","    <main className=\"stack\" dir=\"ltr\">")],
  VT("language-fr09.test.tsx"," /pharmacy: Arabic by default")),
 # U7 · FR-07 messaging
 ("U7-P-AC01",[(M,'    actor_id, actor_role = _actor(request)\n    tenant_id = require_tenant(request)\n    session = _consultation(consultation_id, tenant_id)\n    if not session or actor_id not in (session["owner_id"], session["veterinarian_id"]):\n        raise HTTPException(404, "Consultation not found")',
                  '    actor_id, actor_role = _actor(request)\n    tenant_id = require_tenant(request)\n    session = _consultation(consultation_id, tenant_id)\n    if not session:\n        raise HTTPException(404, "Consultation not found")')],
  PY("test_consultation_messaging.py::test_messages_are_invisible_outside_the_consultation")),
 ("U7-P-AC02",[(M,"        MESSAGE_REPO.record_delivery(DeliveryRecord(","        (lambda r: None)(DeliveryRecord(")],
  PY("test_consultation_messaging.py::test_each_delivery_attempt_is_recorded_with_the_rendered_body_and_audited")),
 # U8 · FR-13 inventory
 ("U8-P-AC01-ISO",[("petcare_api/inventory.py","        return sorted((x for x in self._locations.values() if x.tenant_id == tenant_id),","        return sorted((x for x in self._locations.values()),")],
  PY("test_inventory.py::test_another_tenant_never_sees_or_moves_the_tenants_stock")),
 ("U8-P-AC01-UI",[("petcare_web/app/pharmacy/inventory/page.tsx","    const id = setInterval(() => { void load() }, INVENTORY_REFRESH_MS)","    const id = setInterval(() => {}, INVENTORY_REFRESH_MS)")],
  VT("fr13-inventory.test.tsx","appears with no user action")),
 ("U8-P-AC02-TRIGGER",[("petcare_runtime/migrations/0041_fr13_inventory_ledger.sql","CREATE TRIGGER stock_movement_no_update_delete\n    BEFORE UPDATE OR DELETE ON stock_movement\n    FOR EACH ROW EXECUTE FUNCTION stock_movement_is_immutable();","")],
  PY("test_inventory_postgres.py::test_the_database_refuses_update_and_delete_of_a_movement")),
 ("U8-P-AC02-AUDIT",[(M,'        _audit(event_name="inventory.movement.recorded", actor_id=actor_id, actor_role=actor_role,\n               tenant_id=tenant_id, resource_type="stock_movement", resource_id=m.movement_id,',
                        '        _audit(event_name="inventory.movement.recorded", actor_id='+HDR+', actor_role=actor_role,\n               tenant_id=tenant_id, resource_type="stock_movement", resource_id=m.movement_id,')],
  PY("test_inventory.py::test_every_movement_is_audited_with_the_session_actor_and_client_identity_is_refused")),
 # U14 · FR-20 — both layers of the exact-total confirmation rule
 ("U14-P-AC03-NO-CONFIRMATION-CHECK-ANYWHERE",[(M,"    if body.collected_amount_halalas != o.total_halalas or not body.collection_reference.strip():","    if False:"),
   ("petcare_api/orders.py",'    if c.amount_halalas != order.total_halalas:\n        raise RepositoryDenied(f"collected {c.amount_halalas} halalas does not equal the order total {order.total_halalas}")\n    if not c.reference.strip() or not c.confirmed_by.strip():\n        raise RepositoryDenied("a collection confirmation names its reference and who confirmed it")\n',"")],
  PY("test_fr20_cod_receipt.py::test_an_order_is_never_marked_paid_without_a_confirmation_of_its_exact_total")),
 # U21 · FR-27 AC-02 — supply route: role check AND practitioner authority check
 ("U21-P-AC02-NONVET-SUPPLY-BOTH-LAYERS",[(M,'        if actor_role != ROLE_VETERINARIAN:\n            refuse(403, {"error": "VETERINARIAN_ONLY_SUPPLY_CLASS", "supply_class": supply_class},\n                   f"SUPPLY_CLASS_{supply_class}")\n',""),
   (M,'        try:\n            _require_practitioner_authority(actor_id, tenant_id)\n        except HTTPException as exc:\n            refuse(403, exc.detail, "PRACTITIONER_AUTHORITY_REQUIRED")\n',"")],
  PY("test_fr27_dashboard_class_scope.py::test_dashboard_actions_are_limited_by_supply_class")),
 # U22 · FR-06 video UI
 ("U22-P-VIDEO-UI-NO-GATE",[("petcare_web/app/account/consultations/video/page.tsx","setOffered(Boolean(a.offered) && a.video_capability === true)","setOffered(true)")],VT("fr06-video-call.test.tsx")),
 ("U22-P-VIDEO-UI-NO-SCREEN",[("petcare_web/app/account/consultations/video/page.tsx","    await sender?.replaceTrack(screen.getVideoTracks()[0])\n","")],VT("fr06-video-call.test.tsx")),
]
res=[]
for pid,edits,cmd in P:
    orig={f:open(R+f,'rb').read() for f,_,_ in edits}
    try:
        for f,old,new in edits:
            s=open(R+f).read(); assert s.count(old)==1,(pid,f,s.count(old)); open(R+f,'w').write(s.replace(old,new))
        cwd=R+"petcare_web" if cmd[0]=="npx" else R
        rc=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True,timeout=600)
        out=[l for l in (rc.stdout+rc.stderr).splitlines() if "failed" in l or "passed" in l][-1:]
    finally:
        for f,b in orig.items(): open(R+f,'wb').write(b)
    for f,b in orig.items(): assert open(R+f,'rb').read()==b
    res.append((pid,"ARMED" if rc.returncode!=0 else "VACUOUS")); print(pid,res[-1][1],out,flush=True)
print("ARMED=%d VACUOUS=%d"%(sum(r[1]=="ARMED" for r in res),sum(r[1]=="VACUOUS" for r in res)))
