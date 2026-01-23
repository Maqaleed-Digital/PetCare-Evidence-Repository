import os
import json
import csv
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

EVIDENCE_REPO = Path(os.environ.get("PETCARE_EVIDENCE_REPO", "")).resolve()
DAY3_ROOT = Path(os.environ.get("PETCARE_DAY3_ROOT", "pilot/sprint-6/day-3"))
BUNDLE_INDEX = DAY3_ROOT / "_bundle" / "index.json"
BUNDLE_CHECKSUMS = DAY3_ROOT / "_bundle" / "checksums.sha256"

app = FastAPI(title="PetCare Evidence API (Read-only)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

def require_evidence_repo():
    if not str(EVIDENCE_REPO) or not EVIDENCE_REPO.exists():
        raise HTTPException(500, "PETCARE_EVIDENCE_REPO not set or missing")

def load_index():
    require_evidence_repo()
    p = EVIDENCE_REPO / BUNDLE_INDEX
    if not p.exists():
        raise HTTPException(500, f"Missing bundle index: {p}")
    return json.loads(p.read_text(encoding="utf-8"))

def allowlisted_path(path: str):
    idx = load_index()
    allowed = {it["path"] for it in idx.get("items", [])}
    if path not in allowed:
        raise HTTPException(404, "Unknown evidence path")

    root = (EVIDENCE_REPO / DAY3_ROOT).resolve()
    fp = (EVIDENCE_REPO / DAY3_ROOT / path).resolve()

    if not str(fp).startswith(str(root)):
        raise HTTPException(400, "Invalid path")
    if not fp.exists():
        raise HTTPException(404, "Evidence file missing")

    return fp

def read_csv(relpath: str):
    fp = allowlisted_path(relpath)
    with fp.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

@app.get("/api/evidence/index")
def evidence_index():
    return load_index()

@app.get("/api/evidence/checksums", response_class=PlainTextResponse)
def evidence_checksums():
    require_evidence_repo()
    p = EVIDENCE_REPO / BUNDLE_CHECKSUMS
    if not p.exists():
        raise HTTPException(500, f"Missing checksums: {p}")
    return p.read_text(encoding="utf-8")

@app.get("/api/evidence/file")
def evidence_file(path: str = Query(...)):
    fp = allowlisted_path(path)
    return FileResponse(str(fp), filename=fp.name)

@app.get("/api/security/rls")
def security_rls():
    return read_csv("addendum/D3_2_rls_status__app.audit_events.csv")

@app.get("/api/security/policies")
def security_policies():
    return read_csv("addendum/D3_2_policies__app.audit_events.csv")

@app.get("/api/security/policy_count")
def security_policy_count():
    return read_csv("addendum/D3_2_policies_count__app.audit_events.csv")

@app.get("/api/security/bypassrls")
def security_bypass():
    return read_csv("addendum/D3_3_roles__bypassrls.csv")

@app.get("/api/security/grants")
def security_grants():
    return read_csv("addendum/D3_3_role_table_grants__app.audit_events.csv")
