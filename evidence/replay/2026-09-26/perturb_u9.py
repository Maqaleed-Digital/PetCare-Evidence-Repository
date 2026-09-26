import sys
import subprocess, hashlib
ROOT=sys.argv[1].rstrip("/")
F="petcare_api/tests/test_fr14_prescriptions.py::"
PY=lambda t:["python3","-m","pytest",F+t,"-q","-p","no:cacheprovider"]
P=[
 ("P-AC01-SKIPVERIFY","petcare_api/prescriptions.py","    STATUS_ISSUED: frozenset({STATUS_VET_VERIFIED}),","    STATUS_ISSUED: frozenset({STATUS_VET_VERIFIED, STATUS_DISPENSED}),",
   PY("test_issue_upload_verify_dispense_only_through_the_governed_transitions")),
 ("P-AC01-UI-NOVERIFY","petcare_web/app/vet/prescriptions/page.tsx","    const r = await call(`/api/prescriptions/${id}/verify`, { method: 'POST' })","    const r = await call(`/api/prescriptions/${id}`, { method: 'GET' })",
   ["npx","vitest","run","__tests__/fr14-prescriptions.test.tsx","-t","issues a prescription"]),
 ("P-AC02-DISPENSE-ROLE","petcare_api/main.py","    if role != ROLE_VETERINARIAN:\n        # AC-FR-14-02 (U9): the refusal is audited.","    if False:\n        # AC-FR-14-02 (U9): the refusal is audited.",
   PY("test_dispensing_never_authorises_on_a_client_asserted_class")),
 ("P-AC03-UNGATED","petcare_api/main.py","    gated = prescription_required(supply_class)","    gated = False",
   PY("test_pom_restricted_controlled_are_never_supplied_without_a_verified_prescription")),
 ("P-AC03-OVERGATED","petcare_api/main.py","    gated = prescription_required(supply_class)","    gated = True",
   PY("test_general_and_otc_are_supplied_without_a_prescription")),
 ("P-AC04-NOAUTHORITY","petcare_api/main.py","    tenant_id = require_tenant(request, body.tenant_id)\n    authority = _require_practitioner_authority(actor_id, tenant_id)","    tenant_id = require_tenant(request, body.tenant_id)\n    authority = type('G', (), {'grant_id': 'none'})()",
   PY("test_a_vet_without_a_live_authority_is_refused_naming_the_attribute_and_its_expiry")),
 ("P-AC04-UI-ENABLED","petcare_web/app/vet/prescriptions/page.tsx","        <fieldset disabled={!canPrescribe} className=\"stack\">","        <fieldset disabled={false} className=\"stack\">",
   ["npx","vitest","run","__tests__/fr14-prescriptions.test.tsx","-t","authority expired"]),
 ("P-AC05-READ-UNAUDITED","petcare_api/main.py","    _rx_read_audit(request, \"prescription.transitions_viewed\", \"prescription\", prescription_id, tenant_id)\n","",
   PY("test_every_prescription_read_and_transition_is_tenant_scoped_and_audited")),
 ("P-AC06-UNKNOWN-VALID","petcare_api/sfda.py","        return self.status == VALID","        return self.status in (VALID, UNKNOWN)",
   PY("test_the_sfda_port_never_treats_an_invalid_or_unknown_prescription_as_valid")),
 ("P-AC07-TARGET","petcare_api/main.py","VERIFICATION_TARGET_MINUTES = 30","VERIFICATION_TARGET_MINUTES = 60",
   PY("test_the_verification_time_instrument_reports_the_share_within_thirty_minutes")),
]
res=[]
for pid,f,old,new,cmd in P:
    path=f"{ROOT}/{f}"; orig=open(path,'rb').read(); h=hashlib.sha256(orig).hexdigest()
    s=orig.decode(); assert s.count(old)==1,(pid,s.count(old))
    open(path,'w').write(s.replace(old,new))
    try:
        cwd=ROOT+"/petcare_web" if cmd[0]=="npx" else ROOT
        rc=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True,timeout=300)
        out=[l for l in (rc.stdout+rc.stderr).splitlines() if "failed" in l or "passed" in l][-1:]
    finally:
        open(path,'wb').write(orig)
    assert hashlib.sha256(open(path,'rb').read()).hexdigest()==h
    res.append((pid,"ARMED" if rc.returncode!=0 else "VACUOUS"))
    print(pid,res[-1][1],out,flush=True)
print("ARMED=%d VACUOUS=%d"%(sum(r[1]=="ARMED" for r in res),sum(r[1]=="VACUOUS" for r in res)))
