import sys
import subprocess, hashlib
ROOT=sys.argv[1].rstrip("/")
F="petcare_api/tests/test_fr14_prescriptions.py::"
PY=lambda t:["python3","-m","pytest",F+t,"-q","-p","no:cacheprovider"]
F="petcare_api/tests/test_fr05_licence.py::"
PY=lambda t:["python3","-m","pytest",F+t,"-q","-p","no:cacheprovider"]
P=[
 ("P-AC01-REG-NOLICENCE","petcare_api/routers/auth.py",'    if body.role == "veterinarian":\n        lic = body.licence','    if False:\n        lic = body.licence',PY("test_a_veterinarian_cannot_register_without_licence_details")),
 ("P-AC01-RECORD-UNGATED","petcare_api/main.py","    _require_practitioner_authority(actor_id, tenant_id)  # FR-05 (U10): verified licence at the act\n","",PY("test_an_unverified_vet_performs_no_clinical_act_until_the_licence_is_verified")),
 ("P-AC01-REFUSAL-UNAUDITED","petcare_api/main.py",'        _audit(event_name="practitioner.authority.refused",','        (lambda **k: None)(event_name="practitioner.authority.refused",',PY("test_an_unverified_vet_performs_no_clinical_act_until_the_licence_is_verified")),
 ("P-AC01-UI-NOLICENCE","petcare_web/app/register/page.tsx","          ...(role === 'veterinarian' ? { licence: {","          ...(false ? { licence: {",["npx","vitest","run","__tests__/fr05-licence-registration.test.tsx","-t","asks a veterinarian"]),
 ("P-AC02-NOBASIS","petcare_api/main.py","        if not body.basis.strip():\n            raise HTTPException(400, \"A manual verification","        if False:\n            raise HTTPException(400, \"A manual verification",PY("test_a_verification_records_who_when_how_and_against_what_and_is_tenant_scoped")),
 ("P-AC02-NOEXPIRY","petcare_api/main.py","        expires_at=lic.expires_at(), granted_by_actor_id=actor_id, granted_at=now))","        expires_at=None, granted_by_actor_id=actor_id, granted_at=now))",PY("test_the_licence_expiry_is_rechecked_at_the_moment_of_each_clinical_act")),
 ("P-AC02-CROSSTENANT","petcare_api/main.py","    if target is None or target.tenant_id != tenant_id or target.role != ROLE_VETERINARIAN:\n        return None","    if target is None or target.role != ROLE_VETERINARIAN:\n        return None",PY("test_a_verification_records_who_when_how_and_against_what_and_is_tenant_scoped")),
 ("P-AC02-DB-BASIS","petcare_runtime/migrations/0043_fr05_vet_licence.sql","    basis TEXT NOT NULL CHECK (length(TRIM(basis)) > 0),","    basis TEXT NOT NULL,",["python3","-m","pytest","petcare_api/tests/test_fr05_licence_postgres.py::test_the_database_refuses_an_unnamed_or_repeated_verification","-q","-p","no:cacheprovider"]),
 ("P-AC03-PORT-OPEN","petcare_api/licences.py","        return self.status == LICENCE_VALID","        return self.status in (LICENCE_VALID, LICENCE_NOT_FOUND)",PY("test_the_licensing_lookup_port_fails_closed")),
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
