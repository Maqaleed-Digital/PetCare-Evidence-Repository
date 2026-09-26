import sys
import subprocess, hashlib
R=sys.argv[1].rstrip("/")+"/"
T=["python3","-m","pytest","petcare_api/tests/test_sq2_video_nonprod.py","-q","-p","no:cacheprovider"]
W=["sh","-c","cd petcare_web && npx vitest run __tests__/fr06-video-call.test.tsx"]
P=[
 ("P-SWITCH-DEFAULT-ON",[("petcare_api/video.py","SWITCH_DEFAULT = False","SWITCH_DEFAULT = True")],T),
 ("P-SWITCH-BYPASSED",[("petcare_api/main.py","    if not vid.capability_enabled(os.environ):  # SQ-2","    if False and not vid.capability_enabled(os.environ):  # SQ-2")],T),
 ("P-CONFIG-TURNS-SWITCH-ON",[("petcare_api/Dockerfile","ENV PORT=8080","ENV PORT=8080\nENV PETCARE_VIDEO_CAPABILITY_ENABLED=true")],T),
 ("P-NO-SCREEN-SHARE",[("petcare_api/video.py",'SIGNAL_KINDS = ("OFFER", "ANSWER", "ICE", "SCREEN_OFFER", "SCREEN_ANSWER", "BYE")','SIGNAL_KINDS = ("OFFER", "ANSWER", "ICE", "BYE")')],T),
 ("P-NO-STEP-DOWN-RULE",[("petcare_api/video.py","        return self.hd or self.step_down","        return True")],T),
 ("P-WEB-IGNORES-SWITCH",[("petcare_web/app/account/consultations/video/page.tsx","setOffered(Boolean(a.offered) && a.video_capability === true)","setOffered(Boolean(a.offered))")],W),
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
