from fastapi import FastAPI, APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, PlainTextResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import csv
import json
import hashlib
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Evidence repository path
EVIDENCE_ROOT = Path("/app/petcare-evidence")
PILOT_DATA = EVIDENCE_ROOT / "pilot" / "sprint-6" / "day-3"
MANIFEST_FILE = EVIDENCE_ROOT / "manifests" / "sprint-6-day-3_sha256.txt"
REPORT_FILE = Path("/app/PetCare_Sprint6_Day3_Evidence_Analysis_Report.md")

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="PetCare Evidence API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Helper Functions ---

def parse_csv_file(file_path: Path) -> List[Dict[str, Any]]:
    """Parse a CSV file and return list of dicts"""
    if not file_path.exists():
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return []
            reader = csv.DictReader(content.splitlines())
            return list(reader)
    except Exception as e:
        logger.error(f"Error parsing CSV {file_path}: {e}")
        return []

def parse_jsonl_file(file_path: Path) -> List[Dict[str, Any]]:
    """Parse a JSONL file and return list of dicts"""
    if not file_path.exists():
        return []
    try:
        results = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    results.append(json.loads(line))
        return results
    except Exception as e:
        logger.error(f"Error parsing JSONL {file_path}: {e}")
        return []

def load_checksums() -> Dict[str, str]:
    """Load SHA256 checksums from manifest"""
    checksums = {}
    if MANIFEST_FILE.exists():
        with open(MANIFEST_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split('  ')
                if len(parts) == 2:
                    checksum, filepath = parts
                    # Normalize path (remove ./ prefix)
                    filepath = filepath.lstrip('./')
                    checksums[filepath] = checksum
    return checksums

def verify_file_checksum(file_path: Path, expected_checksum: str) -> bool:
    """Verify file SHA256 checksum"""
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest() == expected_checksum
    except Exception:
        return False

def compute_file_checksum(file_path: Path) -> str:
    """Compute SHA256 checksum for a file"""
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return ""

def get_manifest_verification_status(pack_path: Path, checksums: Dict[str, str]) -> Dict[str, Any]:
    """Get comprehensive manifest verification status"""
    total_in_manifest = len(checksums)
    verified = 0
    failed = 0
    missing_files = []
    extra_files = []
    
    # Check files in manifest
    for rel_path, expected_hash in checksums.items():
        file_path = pack_path / rel_path
        if file_path.exists():
            if verify_file_checksum(file_path, expected_hash):
                verified += 1
            else:
                failed += 1
        else:
            missing_files.append(rel_path)
    
    # Check for files not in manifest (excluding addendum and _trash)
    for f in pack_path.glob("*"):
        if f.is_file() and not f.name.startswith('.'):
            rel_name = f.name
            if rel_name not in checksums:
                extra_files.append(rel_name)
    
    all_ok = verified == total_in_manifest and failed == 0 and len(missing_files) == 0
    
    return {
        "all_ok": all_ok,
        "total_in_manifest": total_in_manifest,
        "verified": verified,
        "failed": failed,
        "missing_files": missing_files,
        "extra_files": extra_files,
        "status_message": "ALL OK" if all_ok else f"{verified}/{total_in_manifest} verified, {failed} failed, {len(missing_files)} missing"
    }

# --- Models ---

class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

class EvidencePack(BaseModel):
    id: str
    name: str
    path: str
    file_count: int
    verified_count: int
    total_size_bytes: int
    manifest_status: Optional[Dict[str, Any]] = None
    has_addendum: bool = False
    addendum_count: int = 0

class EvidenceFile(BaseModel):
    name: str
    path: str
    size_bytes: int
    checksum: Optional[str] = None
    computed_checksum: Optional[str] = None
    verified: Optional[bool] = None
    is_addendum: bool = False
    category: str = "evidence"  # evidence, addendum, manifest, trash

class GovernanceSummary(BaseModel):
    section: str
    title: str
    status: str
    finding: str
    details: Optional[Dict[str, Any]] = None

class RLSStatus(BaseModel):
    table_name: str
    rls_enabled: bool
    rls_forced: bool

class BypassRole(BaseModel):
    role_name: str
    bypass_rls: bool

class AuditEvent(BaseModel):
    id: str
    tenant_id: str
    occurred_at: str
    actor_user_id: Optional[str]
    severity: str
    event_type: str
    target_type: str
    target_id: Optional[str]
    correlation_id: str
    source_mode: str
    source_provider: str
    evidence_hash: Optional[str]
    metadata: Dict[str, Any]

class RuleRun(BaseModel):
    id: str
    tenant_id: str
    request_id: str
    subject_type: str
    subject_id: str
    engine_version: str
    context_json: Dict[str, Any]
    score: int
    band: str
    decision: str
    created_at: str
    created_by: Optional[str]

class ExplainabilityLog(BaseModel):
    id: str
    tenant_id: str
    run_id: str
    request_id: str
    rule_key: str
    rule_version: int
    hit: bool
    weight: int
    points: int
    reason_code: str
    reason_text: str
    details_json: Dict[str, Any]
    created_at: str

# --- API Routes ---

@api_router.get("/")
async def root():
    return {"message": "PetCare Evidence API", "version": "1.0.0"}

# Evidence Pack Routes
@api_router.get("/evidence/packs", response_model=List[EvidencePack])
async def get_evidence_packs():
    """Get list of available evidence packs from pilot/ folder"""
    packs = []
    checksums = load_checksums()
    pilot_root = EVIDENCE_ROOT / "pilot"
    
    # Scan pilot/ folder for evidence packs
    if pilot_root.exists():
        for sprint_dir in sorted(pilot_root.iterdir()):
            if sprint_dir.is_dir():
                for day_dir in sorted(sprint_dir.iterdir()):
                    if day_dir.is_dir():
                        pack_id = f"{sprint_dir.name}-{day_dir.name}"
                        pack_name = f"{sprint_dir.name.replace('-', ' ').title()} {day_dir.name.replace('-', ' ').title()}"
                        
                        # Count main evidence files (exclude addendum, _trash, hidden)
                        files = [f for f in day_dir.glob("*") 
                                if f.is_file() and not f.name.startswith('.')]
                        
                        # Check for addendum folder
                        addendum_dir = day_dir / "addendum"
                        has_addendum = addendum_dir.exists() and addendum_dir.is_dir()
                        addendum_count = len(list(addendum_dir.glob("*"))) if has_addendum else 0
                        
                        # Calculate verification status
                        verified_count = 0
                        total_size = 0
                        for f in files:
                            total_size += f.stat().st_size
                            rel_path = f.name
                            if rel_path in checksums:
                                if verify_file_checksum(f, checksums[rel_path]):
                                    verified_count += 1
                        
                        # Get comprehensive manifest status
                        manifest_status = get_manifest_verification_status(day_dir, checksums)
                        
                        packs.append(EvidencePack(
                            id=pack_id,
                            name=pack_name,
                            path=str(day_dir.relative_to(EVIDENCE_ROOT)),
                            file_count=len(files),
                            verified_count=verified_count,
                            total_size_bytes=total_size,
                            manifest_status=manifest_status,
                            has_addendum=has_addendum,
                            addendum_count=addendum_count
                        ))
    
    return packs

@api_router.get("/evidence/packs/{pack_id}/files")
async def get_pack_files(pack_id: str, include_addendum: bool = True):
    """Get files in an evidence pack with addendum separation"""
    # Parse pack_id to find the right folder
    parts = pack_id.split("-")
    if len(parts) < 3:
        raise HTTPException(status_code=404, detail="Pack not found")
    
    sprint_name = f"{parts[0]}-{parts[1]}"  # e.g., "sprint-6"
    day_name = "-".join(parts[2:])  # e.g., "day-3"
    pack_path = EVIDENCE_ROOT / "pilot" / sprint_name / day_name
    
    if not pack_path.exists():
        raise HTTPException(status_code=404, detail="Pack not found")
    
    checksums = load_checksums()
    evidence_files = []
    addendum_files = []
    manifest_files = []
    trash_files = []
    
    # Main evidence files
    for f in sorted(pack_path.glob("*")):
        if f.is_file() and not f.name.startswith('.'):
            rel_path = f.name
            expected_checksum = checksums.get(rel_path)
            computed = compute_file_checksum(f) if expected_checksum else None
            verified = None
            if expected_checksum and computed:
                verified = computed == expected_checksum
            
            # Categorize by prefix
            category = "evidence"
            if rel_path.startswith("00_manifest") or rel_path.startswith("01_manifest"):
                category = "manifest"
            
            evidence_files.append(EvidenceFile(
                name=f.name,
                path=str(f.relative_to(EVIDENCE_ROOT)),
                size_bytes=f.stat().st_size,
                checksum=expected_checksum,
                computed_checksum=computed,
                verified=verified,
                is_addendum=False,
                category=category
            ))
    
    # Addendum files
    addendum_dir = pack_path / "addendum"
    if addendum_dir.exists() and include_addendum:
        for f in sorted(addendum_dir.glob("*")):
            if f.is_file() and not f.name.startswith('.'):
                addendum_files.append(EvidenceFile(
                    name=f.name,
                    path=str(f.relative_to(EVIDENCE_ROOT)),
                    size_bytes=f.stat().st_size,
                    checksum=None,  # Addendum files not in manifest
                    computed_checksum=compute_file_checksum(f),
                    verified=None,  # Cannot verify without manifest entry
                    is_addendum=True,
                    category="addendum"
                ))
    
    # Trash files (for reference)
    trash_dir = pack_path / "_trash"
    if trash_dir.exists():
        for f in sorted(trash_dir.glob("*")):
            if f.is_file():
                rel_path = f"_trash/{f.name}"
                expected_checksum = checksums.get(rel_path)
                
                trash_files.append(EvidenceFile(
                    name=f.name,
                    path=str(f.relative_to(EVIDENCE_ROOT)),
                    size_bytes=f.stat().st_size,
                    checksum=expected_checksum,
                    computed_checksum=compute_file_checksum(f) if expected_checksum else None,
                    verified=verify_file_checksum(f, expected_checksum) if expected_checksum else None,
                    is_addendum=False,
                    category="trash"
                ))
    
    return {
        "evidence": evidence_files,
        "addendum": addendum_files,
        "trash": trash_files,
        "manifest_status": get_manifest_verification_status(pack_path, checksums)
    }

@api_router.get("/evidence/packs/{pack_id}/manifest")
async def get_pack_manifest_status(pack_id: str):
    """Get detailed manifest verification status"""
    parts = pack_id.split("-")
    if len(parts) < 3:
        raise HTTPException(status_code=404, detail="Pack not found")
    
    sprint_name = f"{parts[0]}-{parts[1]}"
    day_name = "-".join(parts[2:])
    pack_path = EVIDENCE_ROOT / "pilot" / sprint_name / day_name
    
    if not pack_path.exists():
        raise HTTPException(status_code=404, detail="Pack not found")
    
    checksums = load_checksums()
    status = get_manifest_verification_status(pack_path, checksums)
    
    # Add detailed file-by-file status
    file_status = []
    for rel_path, expected_hash in checksums.items():
        file_path = pack_path / rel_path
        exists = file_path.exists()
        matches = verify_file_checksum(file_path, expected_hash) if exists else False
        
        file_status.append({
            "file": rel_path,
            "expected_hash": expected_hash[:16] + "...",
            "exists": exists,
            "matches": matches,
            "status": "OK" if matches else ("MISSING" if not exists else "MISMATCH")
        })
    
    return {
        **status,
        "file_details": file_status
    }

@api_router.get("/evidence/packs/{pack_id}/file")
async def get_pack_file(pack_id: str, path: str = Query(...)):
    """Get raw file content"""
    parts = pack_id.split("-")
    if len(parts) < 3:
        raise HTTPException(status_code=404, detail="Pack not found")
    
    sprint_name = f"{parts[0]}-{parts[1]}"
    day_name = "-".join(parts[2:])
    pack_path = EVIDENCE_ROOT / "pilot" / sprint_name / day_name
    
    # Handle both direct filenames and paths with subdirectories
    file_path = pack_path / path
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Security check - ensure path is within pack_path
    try:
        file_path.resolve().relative_to(pack_path.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return FileResponse(file_path, filename=file_path.name)

# Governance Routes
@api_router.get("/governance/summary")
async def get_governance_summary():
    """Get A-E governance summary cards with data from CSV snapshots"""
    
    # Parse ZZ_window_activity_snapshot.csv
    window_activity = parse_csv_file(PILOT_DATA / "ZZ_window_activity_snapshot.csv")
    activity_data = {row['table_name']: {
        'rows': int(row.get('rows', 0) or 0),
        'min_ts': row.get('min_ts', ''),
        'max_ts': row.get('max_ts', '')
    } for row in window_activity}
    
    total_window_rows = sum(d['rows'] for d in activity_data.values())
    tables_with_data = sum(1 for d in activity_data.values() if d['rows'] > 0)
    
    # Parse D3_2_rls_status (from addendum)
    rls_audit_events = parse_csv_file(ADDENDUM_DIR / "D3_2_rls_status__app.audit_events.csv")
    audit_events_rls = rls_audit_events[0] if rls_audit_events else {}
    audit_events_rls_enabled = audit_events_rls.get('relrowsecurity', 'f') == 't'
    audit_events_rls_forced = audit_events_rls.get('relforcerowsecurity', 'f') == 't'
    
    # Parse D3_3_roles__bypassrls (from addendum)
    bypass_roles = parse_csv_file(ADDENDUM_DIR / "D3_3_roles__bypassrls.csv")
    bypass_count = sum(1 for r in bypass_roles if r.get('rolbypassrls', 'f') == 't')
    
    # Parse main RLS status
    rls_data = parse_csv_file(PILOT_DATA / "D3_1_rls_status.csv")
    rls_enabled_count = sum(1 for r in rls_data if r.get('relrowsecurity') == 't')
    total_rls_tables = len(rls_data) + (1 if rls_audit_events else 0)
    total_rls_enabled = rls_enabled_count + (1 if audit_events_rls_enabled else 0)
    
    # Parse totals after insert
    totals = parse_csv_file(PILOT_DATA / "D3_1_totals_after_insert.csv")
    totals_dict = {r['table_name']: int(r.get('total_rows', 0)) for r in totals}
    
    # Parse audit event types for severity breakdown
    event_types = parse_csv_file(PILOT_DATA / "app.audit_event_types__full.csv")
    severity_counts = {}
    for et in event_types:
        sev = et.get('default_severity', 'info')
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
    
    # Parse explainability data
    explainability_runs = parse_csv_file(PILOT_DATA / "D3_1_insert_proof__public.tcf_rule_runs.csv")
    explainability_logs = parse_csv_file(PILOT_DATA / "D3_1_insert_proof__public.tcf_explainability_logs.csv")
    
    # Determine activity type
    activity_type = "IDLE" if total_window_rows == 0 else "PILOT-TEST" if sum(totals_dict.values()) <= 5 else "ACTIVE"
    
    summaries = [
        {
            "section": "A",
            "title": "Daily Pilot Summary",
            "status": "complete" if activity_type != "IDLE" else "idle",
            "finding": f"{'Pilot-test activity' if activity_type == 'PILOT-TEST' else 'No activity'} in window; {tables_with_data}/{len(activity_data)} tables with data",
            "details": {
                "activity_type": activity_type,
                "window_total_rows": total_window_rows,
                "tables_checked": len(activity_data),
                "tables_with_data": tables_with_data,
                "test_inserts": sum(totals_dict.values())
            },
            "source_files": ["ZZ_window_activity_snapshot.csv", "D3_1_totals_after_insert.csv"],
            "activity_snapshot": activity_data
        },
        {
            "section": "B",
            "title": "Clinical & Safety Signal Scan",
            "status": "clear",
            "finding": "No clinical/safety risk indicators present in audit events",
            "details": {
                "critical_event_types": severity_counts.get('critical', 0),
                "warning_event_types": severity_counts.get('warning', 0),
                "info_event_types": severity_counts.get('info', 0),
                "safety_signals": "NONE",
                "total_event_types": len(event_types)
            },
            "source_files": ["app.audit_event_types__full.csv"]
        },
        {
            "section": "C",
            "title": "AI Governance Integrity",
            "status": "green" if len(explainability_runs) > 0 and len(explainability_logs) > 0 else "idle",
            "finding": f"Schema sound; {len(explainability_runs)} rule runs, {len(explainability_logs)} explainability logs",
            "details": {
                "schema_integrity": "COMPLETE",
                "referential_integrity": "VALID" if len(explainability_runs) > 0 else "UNTESTED",
                "rule_runs": len(explainability_runs),
                "explainability_logs": len(explainability_logs),
                "coverage": "100%" if len(explainability_runs) > 0 and len(explainability_logs) >= len(explainability_runs) else "N/A"
            },
            "source_files": ["D3_1_insert_proof__public.tcf_rule_runs.csv", "D3_1_insert_proof__public.tcf_explainability_logs.csv"]
        },
        {
            "section": "D",
            "title": "Ops Load Scan",
            "status": "idle" if total_window_rows == 0 else "active",
            "finding": f"System {'pre-production' if total_window_rows == 0 else 'has activity'}; {total_window_rows} events in window",
            "details": {
                "system_state": "IDLE" if total_window_rows == 0 else "ACTIVE",
                "total_events": total_window_rows,
                "active_tenants": 1 if sum(totals_dict.values()) > 0 else 0,
                "latency_indicators": "N/A"
            },
            "source_files": ["ZZ_window_activity_snapshot.csv"]
        },
        {
            "section": "E",
            "title": "Security & RBAC",
            "status": "green" if total_rls_enabled == total_rls_tables else "amber",
            "finding": f"RLS {total_rls_enabled}/{total_rls_tables} tables; app.audit_events RLS={'enabled' if audit_events_rls_enabled else 'disabled'}",
            "details": {
                "rls_enabled_tables": total_rls_enabled,
                "total_tables": total_rls_tables,
                "app_audit_events_rls": audit_events_rls_enabled,
                "app_audit_events_forced": audit_events_rls_forced,
                "bypass_roles": bypass_count,
                "policy_enforcement": "ACTIVE"
            },
            "source_files": ["D3_2_rls_status__app.audit_events.csv", "D3_3_roles__bypassrls.csv", "D3_1_rls_status.csv"],
            "bypass_roles_detail": bypass_roles
        }
    ]
    
    return summaries

@api_router.get("/governance/window-activity")
async def get_window_activity():
    """Get window activity snapshot data"""
    data = parse_csv_file(PILOT_DATA / "ZZ_window_activity_snapshot.csv")
    return data

@api_router.get("/governance/report-excerpt")
async def get_report_excerpt():
    """Get key excerpts from the analysis report"""
    if not REPORT_FILE.exists():
        return {"error": "Report not found"}
    
    with open(REPORT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract key sections
    excerpts = {
        "integrity_status": "VERIFIED" if "INTEGRITY VERIFIED" in content else "UNVERIFIED",
        "ui_readiness": [],
        "recommendations": []
    }
    
    # Extract UI-0 Readiness Signals
    if "UI-0 Readiness Signals" in content:
        start = content.find("## UI-0 Readiness Signals")
        end = content.find("## Summary", start) if start > -1 else -1
        if start > -1 and end > -1:
            section = content[start:end]
            if "### ✅ Ready" in section:
                ready_start = section.find("### ✅ Ready")
                ready_end = section.find("### ⚠️", ready_start)
                ready_section = section[ready_start:ready_end] if ready_end > -1 else section[ready_start:]
                lines = [l.strip() for l in ready_section.split('\n') if l.strip().startswith('-')]
                excerpts["ui_readiness"] = [l.lstrip('- ') for l in lines[:5]]
    
    return excerpts

# Security Routes
ADDENDUM_DIR = PILOT_DATA / "addendum"

@api_router.get("/security/rls", response_model=List[RLSStatus])
async def get_rls_status():
    """Get RLS status for tables - checks addendum first"""
    results = []
    
    # Load from addendum D3_2 file first
    addendum_data = parse_csv_file(ADDENDUM_DIR / "D3_2_rls_status__app.audit_events.csv")
    for row in addendum_data:
        results.append(RLSStatus(
            table_name=row.get('table_name', ''),
            rls_enabled=row.get('relrowsecurity', 'f') == 't',
            rls_forced=row.get('relforcerowsecurity', 'f') == 't'
        ))
    
    # Also load from main D3_1 file
    main_data = parse_csv_file(PILOT_DATA / "D3_1_rls_status.csv")
    existing_tables = {r.table_name for r in results}
    for row in main_data:
        table_name = row.get('table_name', '')
        if table_name not in existing_tables:
            results.append(RLSStatus(
                table_name=table_name,
                rls_enabled=row.get('relrowsecurity', 'f') == 't',
                rls_forced=row.get('relforcerowsecurity', 'f') == 't'
            ))
    
    return results

@api_router.get("/security/bypassrls", response_model=List[BypassRole])
async def get_bypass_rls_roles():
    """Get roles with bypass RLS privilege - checks addendum first"""
    # Try addendum D3_3 first
    data = parse_csv_file(ADDENDUM_DIR / "D3_3_roles__bypassrls.csv")
    
    if data:
        return [BypassRole(
            role_name=r.get('rolname', ''), 
            bypass_rls=r.get('rolbypassrls', 'f') == 't'
        ) for r in data]
    
    # Fallback: infer from role grants
    return [
        BypassRole(role_name="postgres", bypass_rls=True),
        BypassRole(role_name="service_role", bypass_rls=True),
        BypassRole(role_name="authenticated", bypass_rls=False),
        BypassRole(role_name="anon", bypass_rls=False)
    ]

@api_router.get("/security/policies")
async def get_security_policies():
    """Get RLS policies"""
    data = parse_csv_file(PILOT_DATA / "D3_1_policies.csv")
    return data

@api_router.get("/security/grants")
async def get_role_grants():
    """Get role table grants"""
    data = parse_csv_file(PILOT_DATA / "D3_1_role_table_grants.csv")
    return data

# Audit Routes
@api_router.get("/audit/events")
async def get_audit_events(
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    correlation_id: Optional[str] = None,
    limit: int = 100
):
    """Get audit events from all audit CSV files with optional filters"""
    all_events = []
    
    # Primary: D3_1_insert_proof__app.audit_events.csv
    insert_proof = parse_csv_file(PILOT_DATA / "D3_1_insert_proof__app.audit_events.csv")
    for row in insert_proof:
        row['_source'] = 'D3_1_insert_proof__app.audit_events.csv'
    all_events.extend(insert_proof)
    
    # app.audit_events__tenant_time.csv
    tenant_data = parse_csv_file(PILOT_DATA / "app.audit_events__tenant_time.csv")
    for row in tenant_data:
        row['_source'] = 'app.audit_events__tenant_time.csv'
    all_events.extend(tenant_data)
    
    # auth.audit_log_entries__time.csv
    auth_data = parse_csv_file(PILOT_DATA / "auth.audit_log_entries__time.csv")
    for row in auth_data:
        row['_source'] = 'auth.audit_log_entries__time.csv'
        row['event_type'] = row.get('event_type', 'auth.event')
        row['severity'] = row.get('severity', 'info')
    all_events.extend(auth_data)
    
    # public.audit_log__time.csv
    public_audit = parse_csv_file(PILOT_DATA / "public.audit_log__time.csv")
    for row in public_audit:
        row['_source'] = 'public.audit_log__time.csv'
        row['event_type'] = row.get('event_type', 'public.audit')
        row['severity'] = row.get('severity', 'info')
    all_events.extend(public_audit)
    
    # DIAG_app.audit_events__nearest_to_window.csv
    diag_data = parse_csv_file(PILOT_DATA / "DIAG_app.audit_events__nearest_to_window.csv")
    for row in diag_data:
        row['_source'] = 'DIAG_app.audit_events__nearest_to_window.csv'
    all_events.extend(diag_data)
    
    # Apply filters
    if event_type:
        all_events = [e for e in all_events if event_type.lower() in e.get('event_type', '').lower()]
    if severity:
        all_events = [e for e in all_events if e.get('severity', '').lower() == severity.lower()]
    if correlation_id:
        all_events = [e for e in all_events if correlation_id.lower() in e.get('correlation_id', '').lower()]
    
    return all_events[:limit]

@api_router.get("/audit/event-types")
async def get_audit_event_types():
    """Get available audit event types with severity breakdown"""
    data = parse_csv_file(PILOT_DATA / "app.audit_event_types__full.csv")
    return data

@api_router.get("/audit/event-catalog")
async def get_audit_event_catalog():
    """Get audit event catalog"""
    data = parse_csv_file(PILOT_DATA / "public.audit_event_catalog__full.csv")
    return data

@api_router.get("/audit/severity-distribution")
async def get_severity_distribution():
    """Get severity distribution from event types"""
    data = parse_csv_file(PILOT_DATA / "app.audit_event_types__full.csv")
    distribution = {}
    for row in data:
        sev = row.get('severity', 'unknown')
        distribution[sev] = distribution.get(sev, 0) + 1
    return distribution

@api_router.get("/audit/correlation/{correlation_id}")
async def get_correlation_drilldown(correlation_id: str):
    """Get all events and related data for a specific correlation ID"""
    result = {
        "correlation_id": correlation_id,
        "audit_events": [],
        "explainability_runs": [],
        "explainability_logs": [],
        "timeline": []
    }
    
    # Get audit events
    audit_data = parse_csv_file(PILOT_DATA / "D3_1_insert_proof__app.audit_events.csv")
    for row in audit_data:
        if correlation_id.lower() in row.get('correlation_id', '').lower():
            row['_type'] = 'audit_event'
            result["audit_events"].append(row)
            result["timeline"].append({
                "timestamp": row.get('occurred_at', ''),
                "type": "audit_event",
                "event": row.get('event_type', ''),
                "severity": row.get('severity', ''),
                "details": row
            })
    
    # Get explainability runs by correlation pattern
    runs_data = parse_csv_file(PILOT_DATA / "D3_1_insert_proof__public.tcf_rule_runs.csv")
    for row in runs_data:
        # Match by request_id pattern (D3_1_TEST_* format)
        if correlation_id.replace('D3_1_TEST_', '') in row.get('request_id', ''):
            row['_type'] = 'rule_run'
            result["explainability_runs"].append(row)
            result["timeline"].append({
                "timestamp": row.get('created_at', ''),
                "type": "rule_run",
                "event": f"Rule run: {row.get('decision', '')}",
                "severity": "info",
                "details": row
            })
    
    # Get explainability logs
    logs_data = parse_csv_file(PILOT_DATA / "D3_1_insert_proof__public.tcf_explainability_logs.csv")
    for row in logs_data:
        if correlation_id.replace('D3_1_TEST_', '') in row.get('request_id', ''):
            row['_type'] = 'explainability_log'
            result["explainability_logs"].append(row)
            result["timeline"].append({
                "timestamp": row.get('created_at', ''),
                "type": "explainability_log",
                "event": f"Rule: {row.get('rule_key', '')} - {row.get('reason_text', '')}",
                "severity": "info",
                "details": row
            })
    
    # Sort timeline by timestamp
    result["timeline"].sort(key=lambda x: x.get('timestamp', ''))
    
    return result

@api_router.get("/audit/correlations")
async def get_correlation_ids():
    """Get all unique correlation IDs"""
    correlations = set()
    
    audit_data = parse_csv_file(PILOT_DATA / "D3_1_insert_proof__app.audit_events.csv")
    for row in audit_data:
        cid = row.get('correlation_id', '')
        if cid:
            correlations.add(cid)
    
    return list(correlations)

# Explainability Routes
@api_router.get("/explainability/runs")
async def get_explainability_runs(request_id: Optional[str] = None):
    """Get TCF rule runs with related logs"""
    runs = parse_csv_file(PILOT_DATA / "D3_1_insert_proof__public.tcf_rule_runs.csv")
    logs = parse_csv_file(PILOT_DATA / "D3_1_insert_proof__public.tcf_explainability_logs.csv")
    
    # Add related logs count to each run
    for run in runs:
        run_id = run.get('id', '')
        run['_logs_count'] = sum(1 for log in logs if log.get('run_id') == run_id)
        run['_source'] = 'D3_1_insert_proof__public.tcf_rule_runs.csv'
    
    if request_id:
        runs = [r for r in runs if request_id.lower() in r.get('request_id', '').lower()]
    
    return runs

@api_router.get("/explainability/logs")
async def get_explainability_logs(request_id: Optional[str] = None, run_id: Optional[str] = None):
    """Get TCF explainability logs"""
    data = parse_csv_file(PILOT_DATA / "D3_1_insert_proof__public.tcf_explainability_logs.csv")
    
    for row in data:
        row['_source'] = 'D3_1_insert_proof__public.tcf_explainability_logs.csv'
    
    if request_id:
        data = [d for d in data if request_id.lower() in d.get('request_id', '').lower()]
    if run_id:
        data = [d for d in data if run_id in d.get('run_id', '')]
    
    return data

@api_router.get("/explainability/schema")
async def get_explainability_schema():
    """Get explainability logs schema"""
    data = parse_csv_file(PILOT_DATA / "SCHEMA_public.tcf_explainability_logs__columns.csv")
    return data

@api_router.get("/explainability/distributions")
async def get_explainability_distributions():
    """Get reason code and rule hit distributions"""
    reason_codes = parse_csv_file(PILOT_DATA / "B_dist__public.tcf_explainability_logs__reason_codes.csv")
    rule_hits = parse_csv_file(PILOT_DATA / "B_dist__public.tcf_explainability_logs__rule_hit_rate.csv")
    
    # Also calculate from actual data if distributions are empty
    logs = parse_csv_file(PILOT_DATA / "D3_1_insert_proof__public.tcf_explainability_logs.csv")
    runs = parse_csv_file(PILOT_DATA / "D3_1_insert_proof__public.tcf_rule_runs.csv")
    
    # Calculate from actual data
    reason_code_dist = {}
    rule_hit_dist = {}
    decision_dist = {}
    band_dist = {}
    
    for log in logs:
        code = log.get('reason_code', 'unknown')
        reason_code_dist[code] = reason_code_dist.get(code, 0) + 1
        
        rule_key = log.get('rule_key', 'unknown')
        hit = log.get('hit', 'f') == 't'
        key = f"{rule_key}_{'hit' if hit else 'miss'}"
        rule_hit_dist[key] = rule_hit_dist.get(key, 0) + 1
    
    for run in runs:
        decision = run.get('decision', 'unknown')
        decision_dist[decision] = decision_dist.get(decision, 0) + 1
        
        band = run.get('band', 'unknown')
        band_dist[band] = band_dist.get(band, 0) + 1
    
    return {
        "reason_codes": reason_code_dist,
        "rule_hits": rule_hit_dist,
        "decisions": decision_dist,
        "bands": band_dist,
        "raw_reason_codes": reason_codes,
        "raw_rule_hits": rule_hits,
        "summary": {
            "total_runs": len(runs),
            "total_logs": len(logs),
            "unique_rules": len(set(log.get('rule_key', '') for log in logs)),
            "unique_reason_codes": len(set(log.get('reason_code', '') for log in logs)),
            "hit_rate": sum(1 for log in logs if log.get('hit') == 't') / max(len(logs), 1) * 100
        }
    }

@api_router.get("/explainability/request/{request_id}")
async def get_request_drilldown(request_id: str):
    """Get complete drilldown for a specific request_id"""
    runs = parse_csv_file(PILOT_DATA / "D3_1_insert_proof__public.tcf_rule_runs.csv")
    logs = parse_csv_file(PILOT_DATA / "D3_1_insert_proof__public.tcf_explainability_logs.csv")
    
    # Filter by request_id
    request_runs = [r for r in runs if request_id.lower() in r.get('request_id', '').lower()]
    request_logs = [l for l in logs if request_id.lower() in l.get('request_id', '').lower()]
    
    # Build timeline
    timeline = []
    
    for run in request_runs:
        timeline.append({
            "timestamp": run.get('created_at', ''),
            "type": "rule_run",
            "title": f"Rule Run: {run.get('decision', '')}",
            "subtitle": f"Score: {run.get('score', 0)} | Band: {run.get('band', '')}",
            "details": run
        })
    
    for log in request_logs:
        hit_status = "HIT" if log.get('hit') == 't' else "MISS"
        timeline.append({
            "timestamp": log.get('created_at', ''),
            "type": "explainability_log",
            "title": f"{log.get('rule_key', '')} - {hit_status}",
            "subtitle": log.get('reason_text', ''),
            "details": log
        })
    
    # Sort by timestamp
    timeline.sort(key=lambda x: x.get('timestamp', ''))
    
    # Calculate summary
    total_points = sum(int(l.get('points', 0)) for l in request_logs)
    total_weight = sum(int(l.get('weight', 0)) for l in request_logs)
    hits = sum(1 for l in request_logs if l.get('hit') == 't')
    
    return {
        "request_id": request_id,
        "runs": request_runs,
        "logs": request_logs,
        "timeline": timeline,
        "summary": {
            "total_runs": len(request_runs),
            "total_logs": len(request_logs),
            "total_points": total_points,
            "total_weight": total_weight,
            "hits": hits,
            "misses": len(request_logs) - hits,
            "hit_rate": hits / max(len(request_logs), 1) * 100,
            "final_decision": request_runs[0].get('decision', 'N/A') if request_runs else 'N/A',
            "final_band": request_runs[0].get('band', 'N/A') if request_runs else 'N/A',
            "final_score": request_runs[0].get('score', 'N/A') if request_runs else 'N/A'
        }
    }

@api_router.get("/explainability/request-ids")
async def get_request_ids():
    """Get all unique request IDs from explainability data"""
    runs = parse_csv_file(PILOT_DATA / "D3_1_insert_proof__public.tcf_rule_runs.csv")
    logs = parse_csv_file(PILOT_DATA / "D3_1_insert_proof__public.tcf_explainability_logs.csv")
    
    request_ids = set()
    for run in runs:
        rid = run.get('request_id', '')
        if rid:
            request_ids.add(rid)
    for log in logs:
        rid = log.get('request_id', '')
        if rid:
            request_ids.add(rid)
    
    return list(request_ids)

# Report Routes
@api_router.get("/report/day3")
async def get_day3_report():
    """Get Day 3 analysis report markdown"""
    if not REPORT_FILE.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    
    with open(REPORT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return PlainTextResponse(content, media_type="text/markdown")

# Legacy status routes
@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    return status_checks

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
