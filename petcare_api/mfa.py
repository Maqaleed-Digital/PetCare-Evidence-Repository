"""NFR-08 — MFA step-up for sensitive operations: the MECHANISM (MVC-BUILD-RUNNER-001 v1.2 U25).

Factor: TOTP (RFC 6238, HMAC-SHA1, 30-second steps, 6 digits), one step of clock tolerance, and no code accepted twice
(the last used step is stored). No SMS factor (EXTERNAL:SMS_GATEWAY). The TOTP secret is stored only as AES-256-GCM
ciphertext under a key resolved through the governed secret provider; it is never logged.

What the runner does NOT choose (the ratified NFR-08 evidence_definition does not fix it — SPONSOR_QUEUE SQ-3):
- WHICH operations are sensitive: `PETCARE_MFA_SENSITIVE_OPERATIONS` ("METHOD /route/template", comma-separated),
  default EMPTY — nothing is enforced until the Sponsor names them;
- the step-up freshness window: `PETCARE_MFA_STEP_UP_MAX_AGE_SECONDS`, NO default — sensitive operations configured
  without a window fail closed at startup;
- recovery (lost factor): not built.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import struct
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from repositories import RepositoryDenied

STEP_SECONDS, DIGITS, TOLERANCE_STEPS = 30, 6, 1
ENV_OPERATIONS = "PETCARE_MFA_SENSITIVE_OPERATIONS"
ENV_MAX_AGE = "PETCARE_MFA_STEP_UP_MAX_AGE_SECONDS"
ENV_KEY_SECRET_ID = "PETCARE_MFA_KEY_SECRET_ID"
DEFAULT_KEY_SECRET_ID = "PETCARE_MFA_ENCRYPTION_KEY"


def hotp(secret: bytes, counter: int, digits: int = DIGITS) -> str:
    """RFC 4226 HOTP (the RFC 6238 building block)."""
    mac = hmac.new(secret, struct.pack(">Q", counter), hashlib.sha1).digest()
    off = mac[-1] & 0x0F
    code = (struct.unpack(">I", mac[off:off + 4])[0] & 0x7FFFFFFF) % (10 ** digits)
    return str(code).zfill(digits)


def totp(secret: bytes, at: float, digits: int = DIGITS) -> str:
    return hotp(secret, int(at // STEP_SECONDS), digits)


def matching_step(secret: bytes, code: str, at: float) -> Optional[int]:
    """The time step `code` is valid for (within the tolerance), or None. Constant-time comparison."""
    now_step = int(at // STEP_SECONDS)
    for step in range(now_step - TOLERANCE_STEPS, now_step + TOLERANCE_STEPS + 1):
        if hmac.compare_digest(hotp(secret, step), str(code)):
            return step
    return None


@dataclass(frozen=True)
class MfaPolicy:
    sensitive_operations: frozenset = frozenset()
    max_age_seconds: Optional[int] = None

    @classmethod
    def from_env(cls, env) -> "MfaPolicy":
        ops = frozenset(x.strip() for x in (env.get(ENV_OPERATIONS) or "").split(",") if x.strip())
        raw = env.get(ENV_MAX_AGE)
        age = None
        if raw not in (None, ""):
            if not str(raw).isdigit() or int(raw) <= 0:
                raise RepositoryDenied(f"{ENV_MAX_AGE} must be a positive integer")
            age = int(raw)
        if ops and age is None:
            raise RepositoryDenied(f"{ENV_OPERATIONS} is set but {ENV_MAX_AGE} is not: the step-up freshness window is a "
                                   "Sponsor decision (SQ-3) and has no default")
        return cls(ops, age)


def encrypt(key_material: str, plaintext: bytes) -> tuple:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    key = hashlib.sha256(key_material.encode()).digest()
    nonce = os.urandom(12)
    return nonce, AESGCM(key).encrypt(nonce, plaintext, b"petcare-mfa-totp")


def decrypt(key_material: str, nonce: bytes, ciphertext: bytes) -> bytes:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    return AESGCM(hashlib.sha256(key_material.encode()).digest()).decrypt(nonce, ciphertext, b"petcare-mfa-totp")


def otpauth_uri(secret: bytes, account: str) -> str:
    b32 = base64.b32encode(secret).decode().rstrip("=")
    return f"otpauth://totp/PetCare:{account}?secret={b32}&issuer=PetCare&algorithm=SHA1&digits={DIGITS}&period={STEP_SECONDS}"


@dataclass(frozen=True)
class Factor:
    user_id: str
    nonce: bytes
    ciphertext: bytes
    created_at: datetime
    confirmed_at: Optional[datetime] = None
    last_used_step: Optional[int] = None


@dataclass
class InMemoryMfaRepository:
    _factors: dict = field(default_factory=dict)
    _step_ups: dict = field(default_factory=dict)

    def put_factor(self, f: Factor) -> Factor:
        self._factors[f.user_id] = f
        return f

    def factor(self, user_id: str) -> Optional[Factor]:
        return self._factors.get(user_id)

    def use_step(self, user_id: str, step: int, *, confirm_at: Optional[datetime] = None) -> bool:
        """Record `step` as used; False if it (or a later step) was already used — a replay."""
        f = self._factors.get(user_id)
        if f is None or (f.last_used_step is not None and step <= f.last_used_step):
            return False
        from dataclasses import replace
        self._factors[user_id] = replace(f, last_used_step=step, confirmed_at=f.confirmed_at or confirm_at)
        return True

    def record_step_up(self, session_id: str, user_id: str, at: datetime) -> None:
        self._step_ups[session_id] = (user_id, at)

    def step_up_at(self, session_id: str, user_id: str) -> Optional[datetime]:
        v = self._step_ups.get(session_id)
        return v[1] if v and v[0] == user_id else None
