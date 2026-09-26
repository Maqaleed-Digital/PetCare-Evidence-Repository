import sys
import subprocess, hashlib
R=sys.argv[1].rstrip("/")+"/"
T=["python3","-m","pytest","petcare_api/tests/test_nfr15_rate_limit.py","-q","-p","no:cacheprovider"]
PG=["python3","-m","pytest","petcare_api/tests/test_nfr15_rate_limit_postgres.py","-q","-p","no:cacheprovider"]
P=[
 ("P-RAISE-PRINCIPAL-LIMIT",[("petcare_api/ratelimit.py","DEFAULT_PRINCIPAL_PER_MIN = 100","DEFAULT_PRINCIPAL_PER_MIN = 150")],T),
 ("P-RAISE-ANONYMOUS-LIMIT",[("petcare_api/ratelimit.py","DEFAULT_ANONYMOUS_PER_MIN = 30","DEFAULT_ANONYMOUS_PER_MIN = 60")],T),
 ("P-KEY-BY-HEADER-IDENTITY",[("petcare_api/main.py",'    principal = session.get("user_id") if session else None','    principal = request.headers.get("x-actor-id") or (session.get("user_id") if session else None)')],T),
 ("P-TRUST-ANY-FORWARDED-FOR",[("petcare_api/ratelimit.py","    if peer not in trusted or not forwarded_for:","    if not forwarded_for:")],T),
 ("P-NO-429",[("petcare_api/main.py","    return _JSONResponse(status_code=429,","    return _JSONResponse(status_code=200,")],T),
 ("P-LOST-UPDATE",[("petcare_api/postgres_repositories.py","                \"ON CONFLICT (bucket, window_start) DO UPDATE SET count = rate_limit_counter.count + 1 \"","                \"ON CONFLICT (bucket, window_start) DO UPDATE SET count = 1 \"")],PG),
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
