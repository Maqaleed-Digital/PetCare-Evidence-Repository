from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from FND.CODE_SCAFFOLD.tenant_isolation_guard import normalize_tenant_id


SCHEMA_VERSION = "PH4_EXPORT_BUNDLE_V1"


def _utc_ts_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _json_default(o: Any) -> Any:
    try:
        return str(o)
    except Exception:
        return "<unserializable>"


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=_json_default)


def _sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _stable_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    xs = list(items or [])
    xs.sort(key=lambda x: str(x.get("key", "")))
    return xs


def _stable_audit(audit: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    xs = list(audit or [])
    xs.sort(
        key=lambda x: (
            str(x.get("ts", "")),
            str(x.get("action", "")),
            str(x.get("key", "")),
            str(x.get("actor_id", "")),
        )
    )
    return xs


@dataclass(frozen=True)
class ExportBundle:
    schema_version: str
    tenant_id: str
    generated_at: str
    items: List[Dict[str, Any]]
    audit: List[Dict[str, Any]]
    counts: Dict[str, int]
    hashes: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["items"] = list(self.items)
        d["audit"] = list(self.audit)
        d["counts"] = dict(self.counts)
        d["hashes"] = dict(self.hashes)
        return d


def build_export_bundle(
    tenant_id: str,
    items: List[Dict[str, Any]],
    audit: List[Dict[str, Any]],
    generated_at: Optional[str] = None,
) -> Dict[str, Any]:
    t = normalize_tenant_id(tenant_id)
    ga = generated_at or _utc_ts_compact()

    si = _stable_items(items)
    sa = _stable_audit(audit)

    items_json = _canonical_json(si)
    audit_json = _canonical_json(sa)

    items_sha = _sha256_text(items_json)
    audit_sha = _sha256_text(audit_json)

    counts = {"items": int(len(si)), "audit": int(len(sa))}

    core = {
        "schema_version": SCHEMA_VERSION,
        "tenant_id": t,
        "generated_at": ga,
        "items": si,
        "audit": sa,
        "counts": counts,
    }

    bundle_sha = _sha256_text(_canonical_json(core))

    b = ExportBundle(
        schema_version=SCHEMA_VERSION,
        tenant_id=t,
        generated_at=ga,
        items=si,
        audit=sa,
        counts=counts,
        hashes={
            "items_sha256": items_sha,
            "audit_sha256": audit_sha,
            "bundle_sha256": bundle_sha,
        },
    )
    return b.to_dict()
