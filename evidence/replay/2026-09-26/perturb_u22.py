import sys
import subprocess, hashlib
R=sys.argv[1].rstrip("/")+"/"
F="petcare_api/tests/test_fr06_video.py::"
PY=lambda t:["python3","-m","pytest",F+t,"-q","-p","no:cacheprovider"]
VT=["npx","vitest","run","__tests__/fr06-video-call.test.tsx"]
P=[
 ("P-VIDEO-GATE-OPEN",[("petcare_api/main.py",'    if not _remote_consultation_gate()["offered"]:\n        raise HTTPException(403, detail={"error": "REMOTE_CONSULTATION_NOT_OFFERED", **_remote_consultation_gate()})\n    # AC-FR-06-05 is decided first','    if False:\n        raise HTTPException(403, detail={"error": "REMOTE_CONSULTATION_NOT_OFFERED", **_remote_consultation_gate()})\n    # AC-FR-06-05 is decided first')],PY("test_the_video_path_is_closed_while_remote_consultation_is_not_offered")),
 ("P-VIDEO-NONPARTICIPANT",[("petcare_api/main.py",'    if not session or actor_id not in (session["owner_id"], session["veterinarian_id"]):\n        raise HTTPException(404, "Consultation not found")\n    if not _remote_consultation_gate()','    if not session:\n        raise HTTPException(404, "Consultation not found")\n    if not _remote_consultation_gate()')],PY("test_both_participants_exchange_the_session_and_the_screen_share_renegotiation")),
 ("P-VIDEO-OWN-ECHO",[("petcare_api/video.py","                and s.sender_id != recipient_id and s.seq > after]","                and s.seq > after]")],PY("test_both_participants_exchange_the_session_and_the_screen_share_renegotiation")),
 ("P-VIDEO-NO-STEP-DOWN-RULE",[("petcare_api/video.py","        return self.hd or self.step_down","        return True")],PY("test_quality_below_720p_is_compliant_only_with_an_adaptive_bitrate_step_down")),
 ("P-VIDEO-UI-SD-CAPTURE",[("petcare_web/lib/videoCall.ts","height: { ideal: 720, min: 720 }","height: { ideal: 480, min: 360 }")],VT),
 ("P-VIDEO-UI-NO-GATE",[("petcare_web/app/account/consultations/video/page.tsx","      setOffered(Boolean(a.offered) && a.video_capability === true)","      setOffered(true)")],VT),
 ("P-VIDEO-UI-NO-SCREEN",[("petcare_web/app/account/consultations/video/page.tsx","    await sender?.replaceTrack(screen.getVideoTracks()[0])","    void sender")],VT),
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
