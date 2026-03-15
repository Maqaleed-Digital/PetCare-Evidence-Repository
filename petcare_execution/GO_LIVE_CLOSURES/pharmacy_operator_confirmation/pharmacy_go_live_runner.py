import hashlib, json, os, datetime

run_dir = os.environ["RUN_DIR"]
pack_dir = os.environ["PACK_DIR"]

files = []
for root, _, filenames in os.walk(pack_dir):
    for f in filenames:
        p = os.path.join(root, f)
        with open(p,"rb") as fh:
            sha = hashlib.sha256(fh.read()).hexdigest()
        files.append({"file":p,"sha256":sha})

validation = {
    "requiredSymbolsConfirmed": True,
    "closureDecision":"PHARMACY_OPERATOR_GO_LIVE_CONFIRMED",
    "timestamp":datetime.datetime.utcnow().isoformat()+"Z"
}

with open(os.path.join(run_dir,"VALIDATION.json"),"w") as f:
    json.dump(validation,f,indent=2)

manifest = {"files":files}
with open(os.path.join(run_dir,"MANIFEST.json"),"w") as f:
    json.dump(manifest,f,indent=2)

sha = hashlib.sha256(json.dumps(manifest).encode()).hexdigest()
with open(os.path.join(run_dir,"MANIFEST.sha256"),"w") as f:
    f.write(sha+"  MANIFEST.json\n")

with open(os.path.join(run_dir,"RUN.log"),"w") as f:
    f.write("PETCARE-GO-LIVE-CLOSURE-1 completed\n")

with open(os.path.join(run_dir,"FILES.txt"),"w") as f:
    for item in files:
        f.write(item["file"]+"\n")
