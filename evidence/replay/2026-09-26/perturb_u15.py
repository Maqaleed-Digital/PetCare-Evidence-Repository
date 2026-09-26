import sys
import subprocess, hashlib
R=sys.argv[1].rstrip("/")+"/"
F="petcare_api/tests/test_fr23_reminders.py::"
PY=lambda t:["python3","-m","pytest",F+t,"-q","-p","no:cacheprovider"]
A1="test_a_due_date_reminds_the_owner_seven_days_and_again_24_hours_before_if_outstanding"
ISO="test_reminders_never_reach_another_tenants_owner"
A2="test_reminders_are_in_the_owners_language_and_every_send_is_audited"
VT=["npx","vitest","run","__tests__/fr23-reminders.test.tsx"]
P=[
 ("P-AC01-NO-7D",[("petcare_api/reminders.py","    if now >= item.due_at - DEFAULT_OFFSETS[REMIND_7D] and REMIND_7D not in already:","    if False:")],PY(A1)),
 ("P-AC01-24H-EVEN-IF-DONE",[("petcare_api/reminders.py","    if not completed and now >= item.due_at - DEFAULT_OFFSETS[REMIND_24H]","    if now >= item.due_at - DEFAULT_OFFSETS[REMIND_24H]")],PY(A1)),
 ("P-AC01-NOT-IDEMPOTENT",[("petcare_api/reminders.py","        if any(x.due_id == r.due_id and x.kind == r.kind for x in self._sent):\n            return False","        if False:\n            return False"),
                            ("petcare_api/main.py","                                  already=REMINDER_REPO.sent_kinds(d.due_id, tenant_id=tenant_id))","                                  already=set())")],PY(A1)),
 ("P-AC01-NO-TENANT-SCOPE",[("petcare_api/reminders.py","        return sorted((d for d in self._dues.values() if d.tenant_id == tenant_id), key=lambda d: (d.due_at, d.due_id))","        return sorted(self._dues.values(), key=lambda d: (d.due_at, d.due_id))"),
                             ("petcare_api/main.py","        pet = PET_REPO.get(d.pet_id, tenant_id=tenant_id)  # the owner of THIS tenant's pet","        pet = PET_REPO.get(d.pet_id, tenant_id=d.tenant_id)  # the owner of THIS tenant's pet")],PY(ISO)),
 ("P-AC01-UI-HIDDEN",[("petcare_web/app/owner/reminders/page.tsx","      {items.map(r => (","      {[].map((r: Reminder) => (")],VT),
 ("P-AC02-ALWAYS-EN",[("petcare_api/main.py","        language = PREFERENCE_REPO.get_language(pet.owner_id) or DEFAULT_LANGUAGE\n        for kind in kinds:","        language = 'en'\n        for kind in kinds:")],PY(A2)),
 ("P-AC02-UNAUDITED",[("petcare_api/main.py",'                _audit(event_name="reminder.sent",','                (lambda **k: None)(event_name="reminder.sent",')],PY(A2)),
 ("P-AC02-UI-LTR",[("petcare_web/app/owner/reminders/page.tsx","          dir={r.language === 'ar' ? 'rtl' : 'ltr'}>","          dir=\"ltr\">")],VT),
 ("P-AC01-DB-NO-UNIQUE",[("petcare_runtime/migrations/0048_fr23_care_reminders.sql","    sent_at TIMESTAMP NOT NULL,\n    UNIQUE (due_id, kind)\n","    sent_at TIMESTAMP NOT NULL\n"),
                          ("petcare_api/postgres_repositories.py",'                               "ON CONFLICT (due_id, kind) DO NOTHING",','                               "",')],["python3","-m","pytest","petcare_api/tests/test_fr23_reminders_postgres.py","-q","-p","no:cacheprovider"]),
]
res=[]
for pid,edits,cmd in P:
    orig={f:open(R+f,'rb').read() for f,_,_ in edits}
    try:
        for f,old,new in edits:
            s=open(R+f).read(); assert s.count(old)==1,(pid,f,s.count(old)); open(R+f,'w').write(s.replace(old,new))
        cwd=R+"petcare_web" if cmd[0]=="npx" else R
        rc=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True,timeout=300)
        out=[l for l in (rc.stdout+rc.stderr).splitlines() if "failed" in l or "passed" in l][-1:]
    finally:
        for f,b in orig.items(): open(R+f,'wb').write(b)
    for f,b in orig.items(): assert open(R+f,'rb').read()==b
    res.append((pid,"ARMED" if rc.returncode!=0 else "VACUOUS")); print(pid,res[-1][1],out,flush=True)
print("ARMED=%d VACUOUS=%d"%(sum(r[1]=="ARMED" for r in res),sum(r[1]=="VACUOUS" for r in res)))
