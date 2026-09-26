import sys
import subprocess, hashlib
R=sys.argv[1].rstrip("/")+"/"
T=["python3","-m","pytest","petcare_api/tests/test_sq1_platform_identity_chain.py","-q","-p","no:cacheprovider"]
PG=["python3","-m","pytest","petcare_api/tests/test_sq1_platform_identity_chain_postgres.py","-q","-p","no:cacheprovider"]
P=[
 ("P-FAILED-SIGNIN-TO-TENANT-CHAIN",[("petcare_api/routers/auth.py","    PERSISTENCE.platform_audit.append({","    ident = IDENTITY_REPO.get_by_user_id(user_id) if user_id else None\n    if event_name == 'auth.sign_in_failed' and ident is not None and ident.tenant_id:\n        import main as _m\n        _m._audit(event_name=event_name, actor_id=user_id, actor_role=ident.role, tenant_id=ident.tenant_id, resource_type='account', resource_id=user_id, action_result='denied', correlation_id=str(uuid4()))\n        return\n    PERSISTENCE.platform_audit.append({")],T),
 ("P-NULL-TENANT-ON-TENANT-CHAIN",[("petcare_runtime/migrations/0053_sq1_platform_identity_chain.sql","    chain_seq BIGINT NOT NULL UNIQUE\n);\n","    chain_seq BIGINT NOT NULL UNIQUE\n);\nALTER TABLE audit_event ALTER COLUMN tenant_id DROP NOT NULL;\n")],PG),
 ("P-REGISTRATION-UNCHAINED",[("petcare_api/routers/auth.py",'_PLATFORM_CHAINED = frozenset({"auth.user_registered", "auth.register_failed",','_PLATFORM_CHAINED = frozenset({"auth.register_failed",')],T),
 ("P-SENTINEL-TENANT-ALLOWED",[("petcare_api/platform_identity_audit.py",'    if "tenant_id" in record:\n        raise PlatformAuditWriteFailed("the platform identity chain carries no tenant")','    pass')],PG),
 ("P-DISTINGUISHABLE-RESPONSE",[("petcare_api/routers/auth.py",'               {"email": body.email, "reason": "user_not_found"})\n        raise HTTPException(status_code=401,\n                            detail={"error": "INVALID_CREDENTIALS"})','               {"email": body.email, "reason": "user_not_found"})\n        raise HTTPException(status_code=401,\n                            detail={"error": "UNKNOWN_IDENTITY"})')],T),
 ("P-PLATFORM-HEAD-UNLOCKED",[("petcare_api/postgres_repositories.py",'"FOR UPDATE", (CHAIN_ID,)).fetchone()','"", (CHAIN_ID,)).fetchone()')],PG),
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
