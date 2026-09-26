import sys
import subprocess, hashlib
R=sys.argv[1].rstrip("/")+"/"
T=["python3","-m","pytest","petcare_api/tests/test_fr27_dashboard_class_scope.py","-q","-p","no:cacheprovider"]
P=[
 ("P-AC02-NONVET-DISPENSE",[("petcare_api/main.py","    if role != ROLE_VETERINARIAN:\n        # AC-FR-14-02 (U9): the refusal is audited.","    if False:\n        # AC-FR-14-02 (U9): the refusal is audited.")],T),
 ("P-AC02-NONVET-SUPPLY",[("petcare_api/main.py",'        if actor_role != ROLE_VETERINARIAN:\n            refuse(403, {"error": "VETERINARIAN_ONLY_SUPPLY_CLASS"','        if False:\n            refuse(403, {"error": "VETERINARIAN_ONLY_SUPPLY_CLASS"')],T),
 ("P-AC02-OUT-OF-SCOPE-CLASS",[("petcare_api/inventory.py","    Enabling it is a code change made under a recorded counsel determination — never a switch.\"\"\"\n    return False","    Enabling it is a code change made under a recorded counsel determination — never a switch.\"\"\"\n    return True")],T),
 ("P-AC02-OVER-RESTRICTED-GENERAL",[("petcare_api/main.py","    gated = prescription_required(supply_class)","    gated = True")],T),
 ("P-AC02-REFUSAL-UNAUDITED",[("petcare_api/main.py",'        _audit(event_name="prescription.dispense_denied", actor_id=actor_id, actor_role=actor_role,\n               tenant_id=require_tenant(request), resource_type="prescription", resource_id=prescription_id,','        (lambda **k: None)(event_name="prescription.dispense_denied", actor_id=actor_id, actor_role=actor_role,\n               tenant_id=require_tenant(request), resource_type="prescription", resource_id=prescription_id,')],T),
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
