from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import copy
import hashlib
import json


@dataclass
class AuditBundleVerifyResult:
    ok: bool
    errors: List[str]
    bundle_checksum_ok: bool
    signature_present: bool
    signature_ok: bool
    tenant_id: Optional[str]
    event_count: int
    first_sequence: Optional[int]
    last_sequence: Optional[int]


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _strip_signature_fields(bundle: Dict[str, Any]) -> Dict[str, Any]:
    b = copy.deepcopy(bundle)

    for k in [
        "_signature",
        "signature",
        "signature_b64",
        "_signer",
        "signer",
        "signing_public_key_b64",
        "signing_key_fingerprint",
        "signed_at_utc",
        "_signature_algorithm",
        "_signature_key_id",
        "signature_algorithm",
    ]:
        if k in b:
            del b[k]

    if "bundle_checksum" in b:
        del b["bundle_checksum"]

    if isinstance(b.get("bundle_meta"), dict):
        meta = b["bundle_meta"]
        for k in [
            "bundle_checksum",
            "_signature",
            "signature",
            "signature_b64",
            "_signer",
            "signer",
            "signing_public_key_b64",
            "signing_key_fingerprint",
            "signed_at_utc",
            "_signature_algorithm",
            "_signature_key_id",
            "signature_algorithm",
        ]:
            if k in meta:
                del meta[k]

    return b


def _fallback_bundle_checksum(bundle: Dict[str, Any]) -> str:
    payload = _strip_signature_fields(bundle)
    raw = _canonical_json(payload).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _verify_bundle_checksum(bundle: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    declared = bundle.get("bundle_checksum")
    if declared is None:
        return True, None
    if not isinstance(declared, str) or not declared:
        return False, "bundle checksum invalid"
    calc = _fallback_bundle_checksum(bundle)
    if declared != calc:
        return False, "bundle checksum mismatch"
    return True, None


def _signature_present(bundle: Dict[str, Any]) -> bool:
    if isinstance(bundle.get("_signature"), str) and bundle.get("_signature"):
        return True
    if isinstance(bundle.get("signature"), str) and bundle.get("signature"):
        return True
    if isinstance(bundle.get("signature_b64"), str) and bundle.get("signature_b64"):
        return True
    return False


def _get_signature_payload(bundle: Dict[str, Any]) -> str:
    if isinstance(bundle.get("_signature"), str) and bundle.get("_signature"):
        return bundle["_signature"]
    if isinstance(bundle.get("signature"), str) and bundle.get("signature"):
        return bundle["signature"]
    if isinstance(bundle.get("signature_b64"), str) and bundle.get("signature_b64"):
        return bundle["signature_b64"]
    return ""


def _verify_prev_checksum_link(events: List[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
    if not events:
        return True, None
    for i in range(1, len(events)):
        prev = events[i - 1].get("checksum")
        got = events[i].get("prev_checksum")
        if prev is None or got is None:
            return False, "hash-chain broken: missing checksum/prev_checksum"
        if got != prev:
            return False, "hash-chain broken: prev_checksum mismatch"
    return True, None


def _verify_event_count(bundle: Dict[str, Any], events: List[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
    declared = bundle.get("event_count")
    if declared is None:
        return True, None
    if not isinstance(declared, int):
        return False, "event_count must be int"
    actual = len(events)
    if declared != actual:
        return False, "event_count mismatch"
    return True, None


def _verify_tenant_isolation(bundle: Dict[str, Any], events: List[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
    bundle_tenant = bundle.get("tenant_id")
    if not isinstance(bundle_tenant, str) or not bundle_tenant:
        return True, None
    for i, e in enumerate(events):
        et = e.get("tenant_id")
        if isinstance(et, str) and et and et != bundle_tenant:
            return False, f"tenant_id mismatch at index={i}"
    return True, None


def _verify_sequence(events: List[Dict[str, Any]], strict_contiguous: bool) -> Tuple[Optional[int], Optional[int], bool, Optional[str]]:
    if not events:
        return None, None, True, None

    seqs: List[int] = []
    for i, e in enumerate(events):
        s = e.get("sequence")
        if not isinstance(s, int):
            return None, None, False, "sequence missing/invalid"
        seqs.append(s)

    first = seqs[0]
    last = seqs[-1]

    if strict_contiguous:
        for i, s in enumerate(seqs):
            if s != first + i:
                return first, last, False, "sequence not contiguous"

    for i in range(1, len(seqs)):
        if seqs[i] <= seqs[i - 1]:
            return first, last, False, "sequence not strictly increasing"

    return first, last, True, None


def _call_signer_verify(signer: Any, bundle: Dict[str, Any], signature: str) -> bool:
    if hasattr(signer, "verify"):
        fn = getattr(signer, "verify")
        try:
            return bool(fn(bundle=bundle, signature=signature))
        except TypeError:
            pass
        try:
            return bool(fn(bundle, signature))
        except TypeError:
            pass
        return bool(fn(bundle))

    if hasattr(signer, "verify_bundle"):
        fn = getattr(signer, "verify_bundle")
        try:
            return bool(fn(bundle=bundle, signature=signature))
        except TypeError:
            pass
        try:
            return bool(fn(bundle, signature))
        except TypeError:
            pass
        return bool(fn(bundle))

    raise TypeError("signer has no verify/verify_bundle")


def verify_audit_bundle(
    bundle: Dict[str, Any],
    signer: Any = None,
    require_signature: bool = False,
    strict_sequence: bool = True,
) -> AuditBundleVerifyResult:
    errors: List[str] = []

    if not isinstance(bundle, dict):
        return AuditBundleVerifyResult(
            ok=False,
            errors=["bundle must be dict"],
            bundle_checksum_ok=True,
            signature_present=False,
            signature_ok=True,
            tenant_id=None,
            event_count=0,
            first_sequence=None,
            last_sequence=None,
        )

    events_raw = bundle.get("events")
    if not isinstance(events_raw, list):
        errors.append("bundle.events must be list")
        events: List[Dict[str, Any]] = []
    else:
        if any(not isinstance(e, dict) for e in events_raw):
            errors.append("bundle.events must contain only objects")
        events = [e for e in events_raw if isinstance(e, dict)]

    tenant_id = bundle.get("tenant_id") if isinstance(bundle.get("tenant_id"), str) else None
    event_count_actual = len(events)

    first_seq, last_seq, seq_ok, seq_err = _verify_sequence(events, strict_sequence)
    if not seq_ok and seq_err:
        errors.append(seq_err)

    chain_ok, chain_err = _verify_prev_checksum_link(events)
    if not chain_ok and chain_err:
        errors.append(chain_err)

    tenant_ok, tenant_err = _verify_tenant_isolation(bundle, events)
    if not tenant_ok and tenant_err:
        errors.append(tenant_err)

    count_ok, count_err = _verify_event_count(bundle, events)
    if not count_ok and count_err:
        errors.append(count_err)

    checksum_ok, checksum_err = _verify_bundle_checksum(bundle)
    if not checksum_ok and checksum_err:
        errors.append(checksum_err)
    bundle_checksum_ok = checksum_ok

    sig_present = _signature_present(bundle)
    signature_ok = True

    if require_signature and not sig_present:
        signature_ok = False
        errors.append("signature required but missing")

    if sig_present and signer is None:
        signature_ok = False
        errors.append("no signer provided")

    if sig_present and signer is not None and require_signature:
        sig = _get_signature_payload(bundle)
        try:
            ok = _call_signer_verify(signer, bundle, sig)
            if not ok:
                signature_ok = False
                errors.append("signature invalid")
        except Exception as e:
            signature_ok = False
            errors.append(f"raised exception: {e}")

    ok = (len(errors) == 0) and bundle_checksum_ok and signature_ok

    return AuditBundleVerifyResult(
        ok=ok,
        errors=errors,
        bundle_checksum_ok=bundle_checksum_ok,
        signature_present=sig_present,
        signature_ok=signature_ok,
        tenant_id=tenant_id,
        event_count=event_count_actual,
        first_sequence=first_seq,
        last_sequence=last_seq,
    )
