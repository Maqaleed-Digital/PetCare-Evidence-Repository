import sys
import subprocess, hashlib
ROOT=sys.argv[1].rstrip("/")
F="petcare_api/tests/test_fr14_prescriptions.py::"
PY=lambda t:["python3","-m","pytest",F+t,"-q","-p","no:cacheprovider"]
F="petcare_api/tests/test_fr06_consultation.py::"
PY=lambda t:["python3","-m","pytest",F+t,"-q","-p","no:cacheprovider"]
T1="test_the_consultation_its_participants_and_outcome_are_recorded_and_audited"
P=[
 ("P-AC04-OUTCOME-UNAUDITED","petcare_api/main.py",'    _audit(event_name="consultation.outcome.recorded",','    (lambda **k: None)(event_name="consultation.outcome.recorded",',PY(T1)),
 ("P-AC04-OUTCOME-ANYONE","petcare_api/main.py",'    if actor_id != session["veterinarian_id"]:\n        raise HTTPException(403, "Only the consultation','    if False:\n        raise HTTPException(403, "Only the consultation',PY(T1)),
 ("P-AC04-PARTICIPANTS","petcare_api/main.py","        if ident is None or ident.tenant_id != tenant_id or ident.role != want:","        if False:",PY("test_participants_must_be_identities_of_the_tenant_in_their_roles")),
 ("P-AC04-TENANT","petcare_api/consultations.py","        return c if c is not None and c.tenant_id == tenant_id else None","        return c",PY("test_a_consultation_is_invisible_and_immovable_across_tenants")),
 ("P-AC04-DB-ONE-OUTCOME","petcare_runtime/migrations/0044_fr06_consultation_record.sql","    session_id TEXT PRIMARY KEY REFERENCES consultation(session_id),","    session_id TEXT NOT NULL REFERENCES consultation(session_id),",["python3","-m","pytest","petcare_api/tests/test_fr06_consultation_postgres.py::test_the_database_refuses_a_second_outcome_and_an_unknown_participant","-q","-p","no:cacheprovider"]),
 ("P-AC05-GATE-OPEN","petcare_api/consultations.py","    return reg[-1] if reg and reg[-1].decision == LAWFUL else None","    return RegulatoryDetermination('x', REG02_TELEMEDICINE, LAWFUL, '-', '-', '-', None)",PY("test_remote_consultation_is_not_offered_until_the_counsel_determination_is_recorded")),
 ("P-AC05-UI-NONOTICE","petcare_web/app/account/consultations/page.tsx","      {remote && !remote.offered && <p role=\"status\" data-testid=\"remote-not-offered\">{t('remoteOff')}</p>}","",["npx","vitest","run","__tests__/fr06-consultations.test.tsx"]),
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
