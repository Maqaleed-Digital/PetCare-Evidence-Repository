"""
PH26 Track B — Cryptographic Export Hardening + Verifiable Bundle Signatures

Purpose:
- Sign an existing audit export bundle (dict) deterministically
- Verify signature deterministically
- Preserve compatibility with existing audit_export_adapter bundle structure

Modes:
- Preferred: Ed25519 (asymmetric) if 'cryptography' is available
- Fallback: HMAC-SHA256 (symmetric) if 'cryptography' is not available

No protected paths touched. Pure library module.

Signature coverage:
- Signature is computed over canonical JSON of the bundle WITHOUT signature fields
  (so signatures are stable and verification is unambiguous)

Bundle fields added on signing:
- signature_algorithm: "ed25519" or "hmac-sha256"
- signature_b64: base64(signature bytes)
- signing_public_key_b64: base64(public key) for ed25519 only
- signing_key_fingerprint: sha256(public_key_bytes) hex for ed25519,
                           sha256(secret_key_bytes) hex for hmac (key id)
- signed_at_utc: ISO-8601 UTC timestamp

Verification:
- For ed25519: uses embedded public key
- For hmac: requires caller to provide secret_key_bytes
"""

import base64
import hashlib
import hmac
import json
from dataclasses import is_dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple


SIGNATURE_FIELDS = {
    "signature_algorithm",
    "signature_b64",
    "signing_public_key_b64",
    "signing_key_fingerprint",
    "signed_at_utc",
}

DEFAULT_HASH_ALG = "sha256"

CRYPTOGRAPHY_AVAILABLE = False
try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
        Ed25519PublicKey,
    )
    from cryptography.hazmat.primitives import serialization

    CRYPTOGRAPHY_AVAILABLE = True
except Exception:
    CRYPTOGRAPHY_AVAILABLE = False


def _now_iso_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _canonicalize(obj: Any) -> Any:
    if is_dataclass(obj):
        return _canonicalize(asdict(obj))

    if isinstance(obj, dict):
        return {str(k): _canonicalize(v) for k, v in sorted(obj.items(), key=lambda kv: str(kv[0]))}

    if isinstance(obj, (list, tuple)):
        return [_canonicalize(v) for v in obj]

    return obj


def canonical_json_bytes(bundle_like: Dict[str, Any]) -> bytes:
    canon = _canonicalize(bundle_like)
    s = json.dumps(canon, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return s.encode("utf-8")


def strip_signature_fields(bundle: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in bundle.items() if k not in SIGNATURE_FIELDS}


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _b64e(b: bytes) -> str:
    return base64.b64encode(b).decode("ascii")


def _b64d(s: str) -> bytes:
    return base64.b64decode(s.encode("ascii"))


def generate_ed25519_keypair_bytes() -> Tuple[bytes, bytes]:
    if not CRYPTOGRAPHY_AVAILABLE:
        raise RuntimeError("cryptography not available; cannot generate ed25519 keypair")

    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()

    priv_raw = priv.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pub_raw = pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return priv_raw, pub_raw


def ed25519_sign(message: bytes, private_key_raw: bytes) -> bytes:
    if not CRYPTOGRAPHY_AVAILABLE:
        raise RuntimeError("cryptography not available; cannot ed25519 sign")

    priv = Ed25519PrivateKey.from_private_bytes(private_key_raw)
    return priv.sign(message)


def ed25519_verify(message: bytes, signature: bytes, public_key_raw: bytes) -> bool:
    if not CRYPTOGRAPHY_AVAILABLE:
        raise RuntimeError("cryptography not available; cannot ed25519 verify")

    pub = Ed25519PublicKey.from_public_bytes(public_key_raw)
    try:
        pub.verify(signature, message)
        return True
    except Exception:
        return False


def hmac_sign(message: bytes, secret_key_bytes: bytes) -> bytes:
    return hmac.new(secret_key_bytes, message, hashlib.sha256).digest()


def hmac_verify(message: bytes, signature: bytes, secret_key_bytes: bytes) -> bool:
    expected = hmac_sign(message, secret_key_bytes)
    return hmac.compare_digest(expected, signature)


def sign_bundle(
    bundle: Dict[str, Any],
    algorithm: str = "ed25519",
    ed25519_private_key_raw: Optional[bytes] = None,
    ed25519_public_key_raw: Optional[bytes] = None,
    hmac_secret_key_bytes: Optional[bytes] = None,
) -> Dict[str, Any]:
    """
    Returns a NEW dict that includes signature fields.

    Rules:
    - Signs the bundle content excluding signature fields
    - Does not mutate input dict
    """
    base = strip_signature_fields(dict(bundle))
    payload = canonical_json_bytes(base)

    signed = dict(base)
    signed_at = _now_iso_utc()

    if algorithm == "ed25519":
        if not CRYPTOGRAPHY_AVAILABLE:
            raise RuntimeError("cryptography not available; ed25519 signing unavailable")

        if ed25519_private_key_raw is None or ed25519_public_key_raw is None:
            raise ValueError("ed25519_private_key_raw and ed25519_public_key_raw are required for ed25519")

        sig = ed25519_sign(payload, ed25519_private_key_raw)
        fp = sha256_hex(ed25519_public_key_raw)

        signed["signature_algorithm"] = "ed25519"
        signed["signature_b64"] = _b64e(sig)
        signed["signing_public_key_b64"] = _b64e(ed25519_public_key_raw)
        signed["signing_key_fingerprint"] = fp
        signed["signed_at_utc"] = signed_at
        return signed

    if algorithm == "hmac-sha256":
        if hmac_secret_key_bytes is None:
            raise ValueError("hmac_secret_key_bytes is required for hmac-sha256")

        sig = hmac_sign(payload, hmac_secret_key_bytes)
        fp = sha256_hex(hmac_secret_key_bytes)

        signed["signature_algorithm"] = "hmac-sha256"
        signed["signature_b64"] = _b64e(sig)
        signed["signing_public_key_b64"] = ""
        signed["signing_key_fingerprint"] = fp
        signed["signed_at_utc"] = signed_at
        return signed

    raise ValueError(f"Unsupported algorithm: {algorithm}")


def verify_signed_bundle(
    signed_bundle: Dict[str, Any],
    hmac_secret_key_bytes: Optional[bytes] = None,
) -> bool:
    """
    Verify the signature on a signed bundle dict.

    - For ed25519: uses embedded signing_public_key_b64
    - For hmac-sha256: requires hmac_secret_key_bytes to be provided
    """
    algo = signed_bundle.get("signature_algorithm", "")
    sig_b64 = signed_bundle.get("signature_b64", "")

    if not algo or not sig_b64:
        return False

    base = strip_signature_fields(dict(signed_bundle))
    payload = canonical_json_bytes(base)
    sig = _b64d(sig_b64)

    if algo == "ed25519":
        if not CRYPTOGRAPHY_AVAILABLE:
            return False

        pub_b64 = signed_bundle.get("signing_public_key_b64", "")
        if not pub_b64:
            return False
        pub_raw = _b64d(pub_b64)

        fp = signed_bundle.get("signing_key_fingerprint", "")
        if fp and fp != sha256_hex(pub_raw):
            return False

        return ed25519_verify(payload, sig, pub_raw)

    if algo == "hmac-sha256":
        if hmac_secret_key_bytes is None:
            return False

        fp = signed_bundle.get("signing_key_fingerprint", "")
        if fp and fp != sha256_hex(hmac_secret_key_bytes):
            return False

        return hmac_verify(payload, sig, hmac_secret_key_bytes)

    return False


__all__ = [
    "CRYPTOGRAPHY_AVAILABLE",
    "canonical_json_bytes",
    "strip_signature_fields",
    "sha256_hex",
    "generate_ed25519_keypair_bytes",
    "sign_bundle",
    "verify_signed_bundle",
]
