import sys
import subprocess, hashlib
R=sys.argv[1].rstrip("/")+"/"
F="petcare_api/tests/test_fr04_restricted_substances.py"
ALL=["python3","-m","pytest",F,"-q","-p","no:cacheprovider"]
WF=["python3","-m","pytest",F,"-q","-p","no:cacheprovider","-k","disabled_on_every_path"]
A3=["python3","-m","pytest",F+"::test_supply_class_comes_only_from_registration_and_an_unregistered_medicine_is_pom","-q","-p","no:cacheprovider"]
P=[
 ("P-AC02-GATE-ENABLED",[("petcare_api/inventory.py","    Enabling it is a code change made under a recorded counsel determination — never a switch.\"\"\"\n    return False","    Enabling it is a code change made under a recorded counsel determination — never a switch.\"\"\"\n    return True")],ALL),
 ("P-AC02-ENV-SWITCH",[("petcare_api/inventory.py","    Enabling it is a code change made under a recorded counsel determination — never a switch.\"\"\"\n    return False","    Enabling it is a code change made under a recorded counsel determination — never a switch.\"\"\"\n    import os\n    return os.environ.get(\"PETCARE_RESTRICTED_SUBSTANCE_WORKFLOW\") == \"enabled\"")],WF),
 ("P-AC02-MOVEMENT-UNGATED",[("petcare_api/main.py",'                                 resource_id=body.product_id, event_name="inventory.movement.refused",\n                                 correlation_id=x_correlation_id)\n','                                 resource_id=body.product_id, event_name="inventory.movement.refused",\n                                 correlation_id=x_correlation_id) if False else None\n')],WF),
 ("P-AC02-SUPPLY-UNGATED",[("petcare_api/main.py",'                                 resource_id=body.product_id, event_name="inventory.supply.refused",\n                                 correlation_id=x_correlation_id)\n','                                 resource_id=body.product_id, event_name="inventory.supply.refused",\n                                 correlation_id=x_correlation_id) if False else None\n')],WF),
 ("P-AC02-DISPENSE-UNGATED",[("petcare_api/main.py","    if rx.status == STATUS_VET_VERIFIED and body is not None:\n        _refuse_restricted_substance(","    if False:\n        _refuse_restricted_substance(")],WF),
 ("P-AC02-UNAUDITED",[("petcare_api/main.py",'               correlation_id=correlation_id, reason_code="RESTRICTED_SUBSTANCE_WORKFLOW_DISABLED:EV-11")','               correlation_id=correlation_id, reason_code="EV11")')],WF),
 ("P-AC03-CLASS-FROM-BODY-TOLERATED",[("petcare_api/main.py",'class MovementRequest(BaseModel):\n    """No actor, role, tenant or supply class: the session and the product registration decide."""\n    model_config = {"extra": "forbid"}','class MovementRequest(BaseModel):\n    """No actor, role, tenant or supply class: the session and the product registration decide."""\n    model_config = {"extra": "ignore"}')],A3),
 ("P-AC03-UNREGISTERED-GENERAL",[("petcare_api/inventory.py","UNREGISTERED_CLASS = POM","UNREGISTERED_CLASS = GENERAL")],A3),
 ("P-AC01-UI-NO-NOTICE",[("petcare_web/app/owner/orders/page.tsx","      <p role=\"note\" data-testid=\"restricted-notice\">{t('restricted')}</p>\n","")],["npx","vitest","run","__tests__/fr04-restricted-notice.test.tsx"]),
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
