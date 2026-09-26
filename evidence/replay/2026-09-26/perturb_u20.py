import sys
import subprocess, hashlib
R=sys.argv[1].rstrip("/")+"/"
F="petcare_api/tests/test_fr01_account_authority.py::"
PY=lambda t:["python3","-m","pytest",F+t,"-q","-p","no:cacheprovider"]
P=[
 ("P-AC03-TOKEN-TENANT",[("petcare_api/routers/auth.py",'    return {**payload, "user_id": record.user_id, "tenant_id": record.tenant_id, "role": record.role}','    return payload'),
                          ("petcare_api/routers/auth.py",'    if (ident is None or getattr(ident, "disabled_at", None) is not None or ident.tenant_id != record.tenant_id','    if (False and ident.tenant_id != record.tenant_id')],PY("test_tenant_authority_is_server_held_and_a_moved_membership_fails_closed")),
 ("P-AC03-SIGNOUT-NO-REVOKE",[("petcare_api/routers/auth.py","                SESSION_STORE.revoke(record.session_id, tenant_id=record.tenant_id)","                pass")],PY("test_sign_in_and_sign_out_are_chained_and_sign_out_ends_the_session")),
 ("P-AC03-SIGNIN-UNCHAINED",[("petcare_api/routers/auth.py",'    _chain_account_event("account.signed_in",','    (lambda *a, **k: None)("account.signed_in",')],PY("test_sign_in_and_sign_out_are_chained_and_sign_out_ends_the_session")),
 ("P-AC03-IDENTITY-DELETED-ON-END",[("petcare_api/tests/test_fr01_account_authority.py",'    _move("u-u20-owner2", None)                                             # the membership ends','    auth.IDENTITY_REPO._by_id.pop("u-u20-owner2", None) if hasattr(auth.IDENTITY_REPO, "_by_id") else auth.IDENTITY_REPO.__dict__.clear()')],PY("test_ending_a_membership_keeps_history_attributable")),
 ("P-AC04-PHARMACY-ROLE",[("petcare_api/roles.py","    ROLE_OWNER,\n})","    ROLE_OWNER,\n    \"pharmacist\",\n})")],PY("test_no_general_purpose_pharmacy_role_exists_and_no_role_dispenses_unscoped")),
 ("P-AC04-NONVET-DISPENSE",[("petcare_api/main.py","    if role != ROLE_VETERINARIAN:\n        # AC-FR-14-02 (U9): the refusal is audited.","    if False:\n        # AC-FR-14-02 (U9): the refusal is audited.")],PY("test_no_general_purpose_pharmacy_role_exists_and_no_role_dispenses_unscoped")),
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
