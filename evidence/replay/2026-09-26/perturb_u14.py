import sys
import subprocess, hashlib
ROOT=sys.argv[1].rstrip("/")
F="petcare_api/tests/test_fr14_prescriptions.py::"
PY=lambda t:["python3","-m","pytest",F+t,"-q","-p","no:cacheprovider"]
F="petcare_api/tests/test_fr20_cod_receipt.py::"
PY=lambda t:["python3","-m","pytest",F+t,"-q","-p","no:cacheprovider"]
A1="test_an_owner_chooses_cash_on_delivery_and_the_order_records_it"
A2="test_on_delivery_the_owner_receives_a_receipt_in_their_language_retrievable_later"
A3="test_an_order_is_never_marked_paid_without_a_confirmation_of_its_exact_total"
VT=["npx","vitest","run","__tests__/fr20-cod-orders.test.tsx"]
P=[
 ("P-AC01-NOT-COD","petcare_api/main.py","    o = ordr.Order(order_id=str(uuid4()), tenant_id=tenant_id, owner_id=actor_id, payment_method=body.payment_method,","    o = ordr.Order(order_id=str(uuid4()), tenant_id=tenant_id, owner_id=actor_id, payment_method='UNSPECIFIED',",PY(A1)),
 ("P-AC01-PRICE-NOT-SERVER","petcare_api/main.py","        price = ORDER_REPO.price_of(l.product_id, tenant_id=tenant_id)","        price = 1",PY(A1)),
 ("P-AC01-POM-ORDERABLE","petcare_api/main.py","        if prescription_required(INVENTORY_REPO.supply_class_of(l.product_id)):\n            raise HTTPException(409, {\"error\": \"PRESCRIPTION_PRODUCT_NOT_ORDERABLE\"","        if False:\n            raise HTTPException(409, {\"error\": \"PRESCRIPTION_PRODUCT_NOT_ORDERABLE\"",PY(A1)),
 ("P-AC01-UI-NOT-COD","petcare_web/app/owner/orders/page.tsx","      body: JSON.stringify({ lines, payment_method: method }) })","      body: JSON.stringify({ lines, payment_method: 'CARD' }) })",VT),
 ("P-AC02-NO-RECEIPT","petcare_api/orders.py","        r = self._receipts.get(order_id)\n        return r if r is not None and r.tenant_id == tenant_id else None","        return None",PY(A2)),
 ("P-AC02-WRONG-LANGUAGE","petcare_api/main.py","    language = PREFERENCE_REPO.get_language(o.owner_id) or DEFAULT_LANGUAGE","    language = DEFAULT_LANGUAGE",PY(A2)),
 ("P-AC02-RECEIPT-UNSCOPED","petcare_api/main.py","    if o is None or (actor_role not in INVENTORY_ROLES and o.owner_id != actor_id):\n        raise HTTPException(404, \"Order not found\")\n    rec =","    if o is None:\n        raise HTTPException(404, \"Order not found\")\n    rec =",PY(A2)),
 ("P-AC02-UI-LTR","petcare_web/app/owner/orders/page.tsx","dir={o.receipt.language === 'ar' ? 'rtl' : 'ltr'}","dir=\"ltr\"",VT),
 ("P-AC02-DB-NO-FK","petcare_runtime/migrations/0047_fr20_cod_receipt.sql","    order_id TEXT NOT NULL UNIQUE REFERENCES order_collection(order_id),","    order_id TEXT NOT NULL UNIQUE,",["python3","-m","pytest","petcare_api/tests/test_fr20_order_postgres.py","-q","-p","no:cacheprovider"]),
 ("P-AC03-PAID-UNCONFIRMED","petcare_api/main.py","    if body.collected_amount_halalas != o.total_halalas or not body.collection_reference.strip():","    if False:",PY(A3)),
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
