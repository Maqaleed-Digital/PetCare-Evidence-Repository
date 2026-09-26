import sys
import subprocess, hashlib
ROOT=sys.argv[1].rstrip("/")
F="petcare_api/tests/test_fr14_prescriptions.py::"
PY=lambda t:["python3","-m","pytest",F+t,"-q","-p","no:cacheprovider"]
F="petcare_api/tests/test_fr19_batch_recall.py::"
PY=lambda t:["python3","-m","pytest",F+t,"-q","-p","no:cacheprovider"]
A1="test_every_movement_and_dispense_records_the_batch"
A2="test_a_recall_resolves_through_stored_relationships_and_notifies_every_affected_owner"
P=[
 ("P-AC01-DISPENSE-NOSTOCK","petcare_api/main.py","    if rx.status == STATUS_VET_VERIFIED:\n        if body is None or body.quantity <= 0:","    if False:\n        if body is None or body.quantity <= 0:",PY(A1)),
 ("P-AC01-RECEIPT-NOEXPIRY","petcare_api/main.py",'            expiry = datetime.strptime(body.batch_expiry or "", "%Y-%m-%d").date()','            expiry = datetime.strptime(body.batch_expiry, "%Y-%m-%d").date() if body.batch_expiry else None',PY(A1)),
 ("P-AC01-DB-BATCH","petcare_runtime/migrations/0041_fr13_inventory_ledger.sql","    batch TEXT NOT NULL CHECK (length(TRIM(batch)) > 0),","    batch TEXT NOT NULL,",["python3","-m","pytest","petcare_api/tests/test_fr19_recall_postgres.py::test_the_database_refuses_a_movement_without_a_batch_or_quantity","-q","-p","no:cacheprovider"]),
 ("P-AC01-UI-NOBATCH","petcare_web/app/pharmacy/page.tsx","        body: JSON.stringify({ ...origin, location_id: origin.location_id || locations[0]?.location_id || '' }),","        body: JSON.stringify({ location_id: origin.location_id || locations[0]?.location_id || '' }),",["npx","vitest","run","__tests__/fr19-dispense-batch.test.tsx"]),
 ("P-AC02-HIDE-INDETERMINATE","petcare_api/recalls.py",'            indeterminate.append({"movement_id": m.movement_id, "reason": "PET_NOT_STORED",\n                                  "prescription_id": rx.prescription_id})','            pass',PY(A2)),
 ("P-AC02-NO-COMPLETENESS","petcare_api/recalls.py",'            "completeness": {"supplies_of_batch": n,','            "_": {"supplies_of_batch": n,',PY(A2)),
 ("P-AC02-NO-NOTIFY","petcare_api/main.py",'        for x in res["resolved"]]\n    RECALL_REPO.create(r, notices)','        for x in []]\n    RECALL_REPO.create(r, notices)',PY(A2)),
 ("P-AC02-CROSS-TENANT","petcare_api/inventory.py","        return [m for m in self._movements if m.tenant_id == tenant_id and m.reason == SUPPLY","        return [m for m in self._movements if m.reason == SUPPLY",PY("test_a_recall_never_crosses_tenants")),
 ("P-AC02-UI-HIDDEN","petcare_web/app/owner/recalls/page.tsx","      {items.map(n => (","      {[].map((n: Notice) => (",["npx","vitest","run","__tests__/fr19-recall-notices.test.tsx"]),
 ("P-AC03-EMPTY-BATCH","petcare_api/recalls.py","    if not product or not batch:","    if not product:",["python3","-m","pytest",F+"test_a_recall_without_product_and_batch_is_refused","-q","-p","no:cacheprovider"]),
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
