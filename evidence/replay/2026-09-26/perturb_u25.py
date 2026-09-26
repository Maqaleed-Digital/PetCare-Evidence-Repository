import sys
import subprocess, hashlib
R=sys.argv[1].rstrip("/")+"/"
T=["python3","-m","pytest","petcare_api/tests/test_nfr08_mfa.py","-q","-p","no:cacheprovider"]
PG=["python3","-m","pytest","petcare_api/tests/test_nfr08_mfa_postgres.py","-q","-p","no:cacheprovider"]
P=[
 ("P-BYPASS-STEP-UP",[("petcare_api/main.py","    if not MFA_POLICY.sensitive_operations or _operation_of(request) not in MFA_POLICY.sensitive_operations:","    if True:")],T),
 ("P-STEP-UP-NOT-SESSION-BOUND",[("petcare_api/mfa.py","        v = self._step_ups.get(session_id)\n        return v[1] if v and v[0] == user_id else None","        hits = [v for v in self._step_ups.values() if v[0] == user_id]\n        return hits[-1][1] if hits else None")],T),
 ("P-NO-FRESHNESS",[("petcare_api/main.py","    if at is None or (datetime.now(timezone.utc) - at).total_seconds() > MFA_POLICY.max_age_seconds:","    if at is None:")],T),
 ("P-REPLAY-ALLOWED",[("petcare_api/mfa.py","        if f is None or (f.last_used_step is not None and step <= f.last_used_step):","        if f is None:")],T),
 ("P-RUNNER-CHOSEN-WINDOW",[("petcare_api/mfa.py","        age = None\n","        age = 900\n")],T),
 ("P-PLAINTEXT-SECRET",[("petcare_api/mfa.py","    return nonce, AESGCM(key).encrypt(nonce, plaintext, b\"petcare-mfa-totp\")","    return nonce, plaintext + b\"-padding-to-length\"")],T),
 ("P-PG-REPLAY-RACE",[("petcare_api/postgres_repositories.py",'                               "WHERE user_id = %s AND (last_used_step IS NULL OR last_used_step < %s)",','                               "WHERE user_id = %s AND (TRUE OR last_used_step < %s)",')],PG),
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
