import sys
import subprocess, hashlib
R=sys.argv[1].rstrip("/")+"/"
F="petcare_api/tests/test_fr15_routing.py::"
PY=lambda t:["python3","-m","pytest",F+t,"-q","-p","no:cacheprovider"]
A1="test_an_order_is_routed_by_licence_then_basket_then_eta_then_distance_then_id"
A2="test_routing_fails_closed_without_maps_or_without_a_licensed_pharmacy"
A4="test_every_routing_decision_is_recorded_with_its_inputs_and_shown_to_the_owner"
KEY="    return sorted(qualified, key=lambda c: (c.eta_seconds, c.distance_metres, c.location_id))[0]"
P=[
 ("P-AC01-IGNORE-LICENCE",[("petcare_api/main.py","        licensed = all(ROUTING_REPO.licensed(loc.location_id, k) for k in classes)","        licensed = True")],PY(A1)),
 ("P-AC01-IGNORE-BASKET",[("petcare_api/main.py","        has_basket = all(stock.get((loc.location_id, l.product_id), 0) >= l.quantity for l in o.lines)","        has_basket = True")],PY(A1)),
 ("P-AC01-DISTANCE-BEFORE-ETA",[("petcare_api/routing.py",KEY,"    return sorted(qualified, key=lambda c: (c.distance_metres, c.eta_seconds, c.location_id))[0]")],PY(A1)),
 ("P-AC01-REVERSED-ID-TIEBREAK",[("petcare_api/routing.py",KEY,"    return min(qualified, key=lambda c: (c.eta_seconds, c.distance_metres, tuple(-ord(x) for x in c.location_id)))")],PY(A1)),
 ("P-AC01-OWNER-LOCATION-IGNORED",[("petcare_api/main.py","                eta, dist = MAPS_PORT.route(origin=(body.latitude, body.longitude), destination=(loc.latitude, loc.longitude))","                eta, dist = MAPS_PORT.route(origin=(0.0, 0.0), destination=(loc.latitude, loc.longitude))")],PY(A1)),
 ("P-AC01-CROSS-TENANT",[("petcare_api/inventory.py","        return sorted((x for x in self._locations.values() if x.tenant_id == tenant_id),","        return sorted((x for x in self._locations.values()),")],PY(A1)),
 ("P-AC01-MAPS-FAIL-OPEN",[("petcare_api/main.py",'                raise HTTPException(503, {"error": "ROUTING_UNAVAILABLE", "detail": str(exc)}) from None','                eta, dist = 0, 0')],PY(A2)),
 ("P-AC04-UNRECORDED",[("petcare_api/routing.py","        self._decisions.append(d)\n        return d","        return d")],PY(A4)),
 ("P-AC04-UNAUDITED",[("petcare_api/main.py",'    _audit(event_name="order.routed",','    (lambda **k: None)(event_name="order.routed",')],PY(A4)),
 ("P-AC04-OWNER-BLIND",[("petcare_api/main.py",'    return None if loc is None else {"location_id": loc.location_id, "name": loc.name, "decided_at": d.decided_at.isoformat()}','    return None')],PY(A4)),
 ("P-AC04-DELIVER-ANYWHERE",[("petcare_api/main.py","    if routed is not None and routed.chosen_location_id and routed.chosen_location_id != body.location_id:","    if False:")],PY(A4)),
 ("P-AC04-UI-HIDDEN",[("petcare_web/app/owner/orders/page.tsx","          {o.fulfilled_by && <div data-testid=\"fulfilled-by\">{t('fulfilledBy')}: {o.fulfilled_by.name}</div>}\n","")],["npx","vitest","run","__tests__/fr15-fulfilled-by.test.tsx"]),
 ("P-AC04-DB-EMPTY-CANDIDATES",[("petcare_runtime/migrations/0050_fr15_order_routing.sql","    candidates JSONB NOT NULL CHECK (jsonb_typeof(candidates) = 'array' AND jsonb_array_length(candidates) > 0),","    candidates JSONB NOT NULL,")],["python3","-m","pytest","petcare_api/tests/test_fr15_routing_postgres.py","-q","-p","no:cacheprovider"]),
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
