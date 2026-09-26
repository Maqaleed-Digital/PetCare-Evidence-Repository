import subprocess, sys, shutil, hashlib
ROOT=sys.argv[1].rstrip("/")
P=[
 ("P-AC03-SLOW","petcare_api/postgres_repositories.py","\"HAVING SUM(m.quantity_delta) <> 0 ORDER BY 1, 2, 3\")","\"HAVING SUM(m.quantity_delta) <> 0 ORDER BY 1, 2, 3\")\n        sql = sql.replace(\"WHERE m.tenant_id\", \"CROSS JOIN (SELECT pg_sleep(1.05)) AS _perturb WHERE m.tenant_id\")",
  ["python3","-m","pytest","petcare_api/tests/test_inventory_postgres.py::test_inventory_check_is_sub_second_on_production_sized_data","-q"]),
 ("P-AC04-CLASS","petcare_api/main.py","    if supply_class in VETERINARIAN_ONLY:\n        try:","    if False:\n        try:",
  ["python3","-m","pytest","petcare_api/tests/test_inventory.py","-q","-k","non_veterinarian"]),
]
res=[]
for pid,f,old,new,cmd in P:
    path=f"{ROOT}/{f}"; orig=open(path,'rb').read(); h=hashlib.sha256(orig).hexdigest()
    s=orig.decode(); assert s.count(old)==1,(pid,s.count(old))
    open(path,'w').write(s.replace(old,new))
    try:
        rc=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=300)
        out=(rc.stdout+rc.stderr).strip().splitlines()[-1:]
    finally:
        open(path,'wb').write(orig)
    assert hashlib.sha256(open(path,'rb').read()).hexdigest()==h
    res.append((pid,"ARMED" if rc.returncode!=0 else "VACUOUS",out))
    print(pid,res[-1][1],out,flush=True)
print("ARMED=%d VACUOUS=%d"%(sum(r[1]=="ARMED" for r in res),sum(r[1]=="VACUOUS" for r in res)))
