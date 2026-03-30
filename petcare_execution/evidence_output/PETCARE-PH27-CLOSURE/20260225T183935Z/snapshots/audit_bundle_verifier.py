"""
Audit Bundle Verifier — PH27 (Service/API compatible)

Compatibility exports (hard):
- AuditBundleVerifyResult
- verify_audit_bundle(bundle, signer=None, require_signature=False, strict_sequence=True)
- _fallback_bundle_checksum(bundle)

Deterministic checksum:
- bundle_checksum == sha256(canonical_json(bundle minus excluded fields))
- excluded fields include bundle_checksum + signature metadata fields (legacy + PH26)

Signature rules:
- If require_signature=True: must have signature metadata AND must verify via signer (if signer provided)
- If signature metadata present but signer is None: FAIL with error containing "no signer provided"
- If signature metadata absent and require_signature=False: OK

Sequence rules:
- If strict_sequence=True and integer sequence fields exist: must be strictly increasing AND contiguous
- If strict_sequence=False and integer sequence fields exist: must be strictly increasing only
- If no integer sequence fields: do not fail
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple


LEGACY_SIGNATURE_FIELDS = frozenset(
    {
        "_signature",
        "_signature_algorithm",
        "_signature_key_id",
        "_signature_timestamp",
        "_signature_version",
    }
)

PH26_SIGNATURE_FIELDS = frozenset(
    {
        "signature_algorithm",
        "signature_b64",
        "signing_public_key_b64",
        "signing_key_fingerprint",
        "signed_at_utc",
    }
)

SIGNATURE_METADATA_FIELDS = frozenset(set(LEGACY_SIGNATURE_FIELDS) | set(PH26_SIGNATURE_FIELDS))
CHECKSUM_EXCLUDED_FIELDS = frozenset(set(SIGNATURE_METADATA_FIELDS) | {"bundle_checksum"})


def _canonical_json(data: Any) -> str:
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def _strip_fields(bundle: Dict[str, Any], excluded: frozenset) -> Dict[str, Any]:
    return {k: v for k, v in bundle.items() if k not in excluded}


def _bundle_checksum_calc(bundle: Dict[str, Any]) -> str:
    stripped = _strip_fields(bundle, CHECKSUM_EXCLUDED_FIELDS)
    canonical = _canonical_json(stripped)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _fallback_bundle_checksum(bundle: Dict[str, Any]) -> str:
    return _bundle_checksum_calc(bundle)


@dataclass
class AuditBundleVerifyResult:
    ok: bool
    errors: List[str]

    bundle_checksum_ok: bool
    signature_present: bool
    signature_ok: bool

    tenant_id: Optional[str] = None
    event_count: Optional[int] = None
    first_sequence: Optional[int] = None
    last_sequence: Optional[int] = None


def _get_events(bundle: Dict[str, Any]) -> List[Dict[str, Any]]:
    ev = bundle.get("events", [])
    if not isinstance(ev, list):
        return []
    out: List[Dict[str, Any]] = []
    for e in ev:
        if isinstance(e, dict):
            out.append(e)
    return out


def _validate_tenant_isolation(bundle: Dict[str, Any], events: Sequence[Dict[str, Any]], errors: List[str]) -> None:
    tenant_id = bundle.get("tenant_id")
    if tenant_id is None:
        return
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        errors.append("tenant_id missing/invalid")
        return
    for i, e in enumerate(events):
        if "tenant_id" not in e:
            continue
        et = e.get("tenant_id")
        if et != tenant_id:
            errors.append(f"tenant_id mismatch event_index={i} event_tenant_id={et} bundle_tenant_id={tenant_id}")


def _extract_sequences(events: Sequence[Dict[str, Any]]) -> List[int]:
    seqs: List[int] = []
    for e in events:
        s = e.get("sequence")
        if isinstance(s, int):
            seqs.append(s)
    return seqs


def _validate_sequences(seqs: List[int], errors: List[str], strict_sequence: bool) -> Tuple[Optional[int], Optional[int]]:
    if not seqs:
        return None, None

    for i in range(len(seqs) - 1):
        if seqs[i] >= seqs[i + 1]:
            errors.append("sequence not strictly increasing")
            break

    if strict_sequence and len(seqs) >= 2:
        for i in range(len(seqs) - 1):
            if seqs[i + 1] != seqs[i] + 1:
                errors.append("sequence not contiguous")
                break

    return seqs[0], seqs[-1]


def _signature_present(bundle: Dict[str, Any]) -> bool:
    return any((k in bundle) for k in SIGNATURE_METADATA_FIELDS)


def _verify_signature(bundle: Dict[str, Any], signer: Any, errors: List[str]) -> bool:
    """
    signer contract: must expose verify_bundle(bundle) -> bool
    """
    try:
        ok = bool(signer.verify_bundle(bundle))
        if not ok:
            errors.append("signature invalid")
        return ok
    except Exception:
        errors.append("signature invalid")
        return False


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
            errors=["bundle invalid: not an object"],
            bundle_checksum_ok=False,
            signature_present=False,
            signature_ok=False,
        )

    events = _get_events(bundle)
    tenant_id = bundle.get("tenant_id") if isinstance(bundle.get("tenant_id"), str) else None

    _validate_tenant_isolation(bundle, events, errors)

    seqs = _extract_sequences(events)
    first_seq, last_seq = _validate_sequences(seqs, errors, strict_sequence)

    want = bundle.get("bundle_checksum")
    calc = _bundle_checksum_calc(bundle)

    bundle_checksum_ok = isinstance(want, str) and (want == calc)
    if not bundle_checksum_ok:
        errors.append("bundle_checksum mismatch")

    sig_present = _signature_present(bundle)
    signature_ok = True

    if require_signature and not sig_present:
        signature_ok = False
        errors.append("signature required but missing")

    if sig_present and signer is None:
        signature_ok = False
        errors.append("no signer provided")

    if sig_present and signer is not None:
        signature_ok = _verify_signature(bundle, signer, errors)

    ok = (len(errors) == 0)

    return AuditBundleVerifyResult(
        ok=ok,
        errors=errors,
        bundle_checksum_ok=bundle_checksum_ok,
        signature_present=sig_present,
        signature_ok=signature_ok,
        tenant_id=tenant_id,
        event_count=len(events),
        first_sequence=first_seq,
        last_sequence=last_seq,
    )


def main() -> int:
    import sys

    if len(sys.argv) != 2:
        print("USAGE: python audit_bundle_verifier.py <bundle.json>", file=sys.stderr)
        return 2

    path = sys.argv[1]
    try:
        with open(path, "r", encoding="utf-8") as f:
            bundle = json.load(f)

        r = verify_audit_bundle(bundle)

        print("AUDIT_BUNDLE_VERIFY")
        print(f"tenant_id={r.tenant_id}")
        print(f"event_count={r.event_count}")
        print(f"bundle_checksum_ok={r.bundle_checksum_ok}")
        print(f"signature_present={r.signature_present}")
        print(f"signature_ok={r.signature_ok}")
        if r.errors:
            for e in r.errors:
                print(f"error={e}")
        print(f"RESULT={'PASS' if r.ok else 'FAIL'}")

        return 0 if r.ok else 1

    except Exception as e:
        print(f"ERROR={type(e).__name__}: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
