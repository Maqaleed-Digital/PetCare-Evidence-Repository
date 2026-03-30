from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Dict, List, Optional

from FND.security.audit_chain import verify_hash_chain

SCHEMA_VERSION = 1

def _env_truthy(name: str) -> bool:
    v = os.environ.get(name)
    if v is None:
        return False
    return str(v).strip().lower() in ["1", "true", "yes", "y", "on"]

def _canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def _sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()

def _sha256_obj(obj: Any) -> str:
    return _sha256_bytes(_canonical_json_bytes(obj))

def _normalize_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    def k(it: Dict[str, Any]) -> str:
        if "key" in it:
            return str(it.get("key", ""))
        if "k" in it:
            return str(it.get("k", ""))
        return ""
    return sorted(items, key=k)

def _require_valid_audit_chain(audit: Any) -> None:
    if audit is None:
        return
    if not isinstance(audit, list):
        raise ValueError("invalid_audit_type:not_list")
    res = verify_hash_chain(audit)
    if not res.ok:
        raise ValueError(f"invalid_audit_hash_chain:{res.reason}")

def build_export_bundle(
    tenant_id: str,
    items: List[Dict[str, Any]],
    audit: Optional[List[Dict[str, Any]]] = None,
    *,
    generated_at: Optional[str] = None,
    include_pii: bool = False,
    watermark: bool = False,
    encryption: bool = False,
    enforce_audit_chain: bool = False
) -> Dict[str, Any]:
    tenant_ok = isinstance(tenant_id, str) and bool(tenant_id.strip())
    if not tenant_ok:
        from FND.CODE_SCAFFOLD.tenant_isolation_guard import MissingTenantHeader
        raise MissingTenantHeader("X-Tenant-ID header required for export bundle")

    norm_items = _normalize_items(items if items is not None else [])
    norm_audit = audit if audit is not None else []

    enforce = bool(enforce_audit_chain) or _env_truthy("PETCARE_ENFORCE_AUDIT_CHAIN")
    if enforce:
        _require_valid_audit_chain(norm_audit)

    items_sha = _sha256_obj(norm_items)
    audit_sha = _sha256_obj(norm_audit)

    bundle: Dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "tenant_id": tenant_id,
        "generated_at": generated_at if generated_at is not None else "",
        "items": norm_items,
        "audit": norm_audit,
        "counts": {
            "items": int(len(norm_items)),
            "audit": int(len(norm_audit))
        },
        "export_controls": {
            "include_pii": bool(include_pii),
            "watermark": bool(watermark),
            "encryption": bool(encryption)
        },
        "hashes": {
            "items_sha256": items_sha,
            "audit_sha256": audit_sha
        }
    }

    bundle_sha = _sha256_obj(bundle)
    bundle["hashes"]["bundle_sha256"] = bundle_sha

    return bundle
