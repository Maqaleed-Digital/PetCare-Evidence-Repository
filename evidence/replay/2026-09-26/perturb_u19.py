import sys
import subprocess, hashlib
R=sys.argv[1].rstrip("/")+"/"
T=["python3","-m","pytest","petcare_api/tests/test_fr09_notification_language.py","-q","-p","no:cacheprovider"]
P=[
 ("P-AC03-MESSAGE-ENGLISH",[("petcare_api/main.py","        rendered = _render_notification(actor_role, consultation_id, body.body, _recipient_language(recipient))","        rendered = _render_notification(actor_role, consultation_id, body.body, 'en')")],T),
 ("P-AC03-RECALL-ENGLISH",[("petcare_api/main.py",'        rendered_body=rcl.render_notice(_recipient_language(x["owner_id"]), product=product, batch=batch,','        rendered_body=rcl.render_notice("en", product=product, batch=batch,')],T),
 ("P-AC03-SENDER-LANGUAGE",[("petcare_api/main.py",'    return PREFERENCE_REPO.get_language(user_id) or DEFAULT_LANGUAGE\n','    return DEFAULT_LANGUAGE\n')],T),
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
