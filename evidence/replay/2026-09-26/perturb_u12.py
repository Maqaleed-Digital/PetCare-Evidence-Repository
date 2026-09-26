import sys
import subprocess, hashlib
ROOT=sys.argv[1].rstrip("/")
F="petcare_api/tests/test_fr14_prescriptions.py::"
PY=lambda t:["python3","-m","pytest",F+t,"-q","-p","no:cacheprovider"]
F="petcare_api/tests/test_fr16_delivery.py::"
PY=lambda t:["python3","-m","pytest",F+t,"-q","-p","no:cacheprovider"]
A1="test_a_cold_chain_delivery_carries_a_temperature_log_the_owner_sees"
A4="test_an_out_of_range_reading_raises_an_audited_alert_to_the_pharmacy_only"
P=[
 ("P-AC01-COMPLETE-NOLOG","petcare_api/main.py","    if d.cold_chain and not DELIVERY_REPO.readings(delivery_id, tenant_id=tenant_id):","    if False:",PY(A1)),
 ("P-AC01-OWNER-BLIND","petcare_api/main.py","            if actor_role in INVENTORY_ROLES or d.owner_id == actor_id]","            if actor_role in INVENTORY_ROLES]",PY(A1)),
 ("P-AC01-NO-RANGE","petcare_api/main.py","    rng = INVENTORY_REPO.storage_range_of(body.product_id)","    rng = None",PY(A1)),
 ("P-AC01-UI-NOLOG","petcare_web/app/owner/deliveries/page.tsx","                  {d.temperature_log.map(r => (","                  {[].map((r: Reading) => (",["npx","vitest","run","__tests__/fr16-deliveries.test.tsx"]),
 ("P-AC01-DB-AFTER-COMPLETE","petcare_api/postgres_repositories.py",'                if conn.execute("SELECT 1 FROM delivery_completion WHERE delivery_id = %s", (r.delivery_id,)).fetchall():','                if False:',["python3","-m","pytest","petcare_api/tests/test_fr16_delivery_postgres.py","-q","-p","no:cacheprovider"]),
 ("P-AC04-NOALERT","petcare_api/main.py","    alert = None if not reading.out_of_range else dlv.DeliveryAlert(","    alert = None if True else dlv.DeliveryAlert(",PY(A4)),
 ("P-AC04-UNAUDITED","petcare_api/main.py",'        _audit(event_name="delivery.temperature.alert",','        (lambda **k: None)(event_name="delivery.temperature.alert",',PY(A4)),
 ("P-AC04-TENANT","petcare_api/deliveries.py","        return [a for a in self._alerts if a.tenant_id == tenant_id]","        return list(self._alerts)",PY(A4)),
 ("P-AC02-NO-TIMESTAMP","petcare_api/deliveries.py",'    if ts in (None, "") or val in (None, ""):','    if val in (None, ""):',["python3","-m","pytest","petcare_api/tests/test_fr16_delivery.py","-q","-p","no:cacheprovider","-k","without_a_timestamp"]),
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
