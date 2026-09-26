import sys
import subprocess, hashlib
R=sys.argv[1].rstrip("/")+"/"
F="petcare_api/tests/test_fr30_compliance.py::"
PY=lambda t:["python3","-m","pytest",F+t,"-q","-p","no:cacheprovider"]
A1="test_the_controlled_substance_report_is_generated_from_recorded_events_and_traces_to_them"
A2="test_antimicrobial_prescribing_aggregates_by_agent_class_species_practitioner_and_period"
A3="test_a_notifiable_case_carries_its_statutory_clock_from_detection"
PG=["python3","-m","pytest","petcare_api/tests/test_fr30_compliance_postgres.py","-q","-p","no:cacheprovider"]
P=[
 ("P-AC01-DISPENSES-OMITTED",[("petcare_api/compliance.py",'            for m in movements if m.supply_class == "CONTROLLED" and period_from <= m.created_at < period_to]','            for m in movements if m.supply_class == "CONTROLLED" and m.reason != "SUPPLY" and period_from <= m.created_at < period_to]')],PY(A1)),
 ("P-AC01-UNTRACEABLE-TOTALS",[("petcare_api/compliance.py",'        a["movement_ids"].append(r["movement_id"])','        pass')],PY(A1)),
 ("P-AC01-REPRODUCE-UNCHECKED",[("petcare_api/main.py",'"stored_content_sha256": h.content_sha256, "reproduces": rep["content_sha256"] == h.content_sha256}','"stored_content_sha256": h.content_sha256, "reproduces": True}')],PY(A1)),
 ("P-AC01-UNAUDITED",[("petcare_api/main.py",'    _audit(event_name="compliance.report.generated",','    (lambda **k: None)(event_name="compliance.report.generated",')],PY(A1)),
 ("P-AC01-CROSS-TENANT",[("petcare_api/inventory.py","        return [m for m in self._movements\n                if m.tenant_id == tenant_id and (location_id is None or m.location_id == location_id)]","        return [m for m in self._movements\n                if (location_id is None or m.location_id == location_id)]")],PY(A1)),
 ("P-AC02-TEXT-SEARCH",[("petcare_api/main.py","            am = INVENTORY_REPO.antimicrobial_of(product) if product else None","            am = INVENTORY_REPO.antimicrobial_of(product) if product else ((\"amoxicillin\", \"penicillin\") if \"amoxicillin\" in rx.medication_name else None)")],PY(A2)),
 ("P-AC02-NO-COVERAGE",[("petcare_api/compliance.py",'            "coverage": {"antimicrobial_prescriptions": n,','            "_": {"antimicrobial_prescriptions": n,')],PY(A2)),
 ("P-AC02-PG-NOT-DURABLE",[("petcare_api/postgres_repositories.py",'        return (rows[0][0], rows[0][1]) if rows else None\n\n    def storage_range_of','        return None\n\n    def storage_range_of')],PG),
 ("P-AC03-NO-CLOCK",[("petcare_api/main.py","        detected_at=detected, report_due_at=detected + timedelta(hours=disease.report_within_hours),","        detected_at=detected, report_due_at=detected + timedelta(hours=1),")],PY(A3)),
 ("P-AC03-UNAUDITED",[("petcare_api/main.py",'    _audit(event_name="notifiable.case.recorded",','    (lambda **k: None)(event_name="notifiable.case.recorded",')],PY(A3)),
 ("P-AC03-DB-NO-CLOCK-CHECK",[("petcare_runtime/migrations/0049_fr30_compliance_reporting.sql","    report_due_at TIMESTAMP NOT NULL CHECK (report_due_at > detected_at),","    report_due_at TIMESTAMP NULL,")],PG),
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
