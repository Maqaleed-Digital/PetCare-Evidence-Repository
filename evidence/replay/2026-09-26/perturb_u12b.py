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
 ("P-AC02-DEFAULTED-TIMESTAMP","petcare_api/deliveries.py",'    ts, val = raw.get("recorded_at"), raw.get("celsius")','    ts, val = raw.get("recorded_at") or "2026-01-01T00:00:00+00:00", raw.get("celsius")',["python3","-m","pytest","petcare_api/tests/test_fr16_delivery.py","-q","-p","no:cacheprovider","-k","without_a_timestamp"]),
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
