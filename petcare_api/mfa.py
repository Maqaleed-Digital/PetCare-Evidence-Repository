"""NFR-08 — MFA step-up for sensitive operations (U25 mechanism; U28 applies Sponsor act SQ-3).

Factor: TOTP (RFC 6238, HMAC-SHA1, 30-second steps, 6 digits), one step of clock tolerance, and no code accepted twice
(the last used step is stored). SMS is NOT a factor (SQ-3). The TOTP secret is stored only as AES-256-GCM ciphertext
under a key resolved through the governed secret provider; it is never logged.

Policy — governance/sponsor_acts/MVC-SQ3-NFR08-STEP-UP-001.md (MVC-BUILD-RUNNER-001 v1.3 U28). Fixed by the act, so
nothing here is read from the environment: the sensitive operations (`SQ3_OPERATIONS`), the 15-minute freshness window,
the always-fresh class, enrolment by per-operation primary re-authentication when no factor is active, ten single-use
hashed recovery codes (one redemption = one step-up for exactly one operation), and the two-admin assisted reset.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
import struct
from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Optional

STEP_SECONDS, DIGITS, TOLERANCE_STEPS = 30, 6, 1
ENV_KEY_SECRET_ID = "PETCARE_MFA_KEY_SECRET_ID"
DEFAULT_KEY_SECRET_ID = "PETCARE_MFA_ENCRYPTION_KEY"

SQ3_ACT_ID = "MVC-SQ3-NFR08-STEP-UP-001"
STEP_UP_FRESHNESS_SECONDS = 15 * 60
FACTORS = ("totp",)                     # SQ-3: SMS is not an MFA factor
RECOVERY_CODE_COUNT = 10

#: Operations enforced inside their route rather than by the middleware: the supply route only when the supply class
#: is prescription-only; enrolment because SQ-3 gives it its own rule (re-authentication when no factor is active).
SUPPLY_OF_PRESCRIPTION_CLASS = "POST /api/inventory/supplies"
ENROL = "POST /api/me/mfa/enrol"
RESET_REQUEST = "POST /api/admin/mfa-resets"
RESET_APPROVE = "POST /api/admin/mfa-resets/{reset_id}/approve"

#: SQ-3 item -> (text, served operations "METHOD /route/template"). An empty tuple is NOT_CURRENTLY_SERVED: the product
#: has no such capability, and none is invented to create a test target.
SQ3_OPERATIONS = {
    1: ("dispensing a POM product", ("POST /api/prescriptions/{prescription_id}/dispense", SUPPLY_OF_PRESCRIPTION_CLASS)),
    2: ("prescribing a POM product", ("POST /api/prescriptions",)),
    3: ("signing consultation notes", ("POST /api/consultations/notes/{note_id}/sign",)),
    4: ("signing medical records", ("POST /api/pets/{pet_id}/medical-records/{record_id}/sign",)),
    5: ("changing roles", ("POST /api/admin/identities/{user_id}/role",)),
    6: ("changing permissions", ("POST /api/admin/practitioners/{user_id}/authority",
                                 "POST /api/admin/practitioners/authority/{grant_id}/revoke",
                                 "POST /api/admin/practitioners/licences/{licence_id}/verify")),
    7: ("changing tenant membership", ("POST /api/admin/identities/{user_id}/tenant",)),
    8: ("enrolling MFA", (ENROL,)),
    9: ("resetting MFA", (RESET_REQUEST, RESET_APPROVE)),
    10: ("bulk export of any data", ("GET /audit/events", "GET /audit/events/tenant",
                                     "GET /api/admin/platform-identity-audit",
                                     "POST /api/compliance/reports/controlled-substances",
                                     "GET /api/compliance/reports/{report_id}")),
    11: ("export of personal data", ("GET /api/me/export",)),
    12: ("changing payout details", ("PUT /api/admin/tenant/payout-details",)),
    13: ("changing bank details", ("PUT /api/admin/tenant/bank-details",)),
    14: ("issuing credentials", ("POST /api/admin/credentials",)),
    15: ("issuing API keys", ("POST /api/admin/api-keys",)),
}
#: SQ-3 ALWAYS-FRESH: role changes, MFA enrolment/reset, payout or bank-detail changes.
ALWAYS_FRESH_ITEMS = frozenset({5, 8, 9, 12, 13})

ALL_OPERATIONS = frozenset(op for _t, ops in SQ3_OPERATIONS.values() for op in ops)
ALWAYS_FRESH_OPERATIONS = frozenset(op for i in ALWAYS_FRESH_ITEMS for op in SQ3_OPERATIONS[i][1])
MIDDLEWARE_OPERATIONS = ALL_OPERATIONS - {SUPPLY_OF_PRESCRIPTION_CLASS, ENROL}
NOT_CURRENTLY_SERVED = tuple(f"{i}. {t}" for i, (t, ops) in SQ3_OPERATIONS.items() if not ops)
#: Served routes whose NAMES touch an SQ-3 subject but which are NOT one of the fifteen sensitive operations, each with
#: the reason (MVC-EPC-D-001 D1). The route-name guard in test_nfr08_sq3 accepts a route only if it is mapped above or
#: declared here — a new sensitive-sounding route can never be left silently unprotected.
DECLARED_NOT_SENSITIVE = {
    "GET /api/admin/tenant/payout-details": "read of the tenant's payout settings; changing them is #12",
    "GET /api/admin/tenant/bank-details": "read of the MASKED bank details; changing them is #13",
    "GET /api/admin/api-keys": "list of key metadata (prefix only, never a key); issuing is #15",
    "POST /api/admin/api-keys/{key_id}/revoke": "revocation removes access; issuing is #15",
}


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


# ---------------------------------------------------------------------------------------------------- recovery codes
@dataclass(frozen=True)
class RecoveryCode:
    """A recovery code as stored: a salted SHA-256 digest only. The plaintext exists once, in the issuing response."""
    user_id: str
    code_id: str
    salt: bytes
    digest: bytes
    used_at: Optional[datetime] = None


def _normalise(code: str) -> str:
    return "".join(ch for ch in str(code).upper() if ch.isalnum())


def code_digest(salt: bytes, code: str) -> bytes:
    return hashlib.sha256(salt + _normalise(code).encode()).digest()


def issue_recovery_codes(user_id: str) -> tuple:
    """(plaintext codes shown once, stored records). 80 random bits per code from the OS CSPRNG."""
    plain, stored = [], []
    for _ in range(RECOVERY_CODE_COUNT):
        raw = base64.b32encode(secrets.token_bytes(10)).decode()
        code = "-".join(raw[i:i + 4] for i in range(0, 16, 4))
        salt = secrets.token_bytes(16)
        plain.append(code)
        stored.append(RecoveryCode(user_id=user_id, code_id=secrets.token_hex(8), salt=salt,
                                   digest=code_digest(salt, code)))
    return plain, stored


def matching_code(stored: list, code: str) -> Optional[RecoveryCode]:
    """The unused stored code `code` matches, or None. Every candidate is compared (constant time each)."""
    hit = None
    for rc in stored:
        if rc.used_at is None and hmac.compare_digest(code_digest(rc.salt, code), rc.digest):
            hit = rc
    return hit


# ------------------------------------------------------------------------------------------------------------ records
@dataclass(frozen=True)
class Factor:
    user_id: str
    nonce: bytes
    ciphertext: bytes
    created_at: datetime
    confirmed_at: Optional[datetime] = None
    last_used_step: Optional[int] = None


@dataclass(frozen=True)
class StepUp:
    session_id: str
    user_id: str
    verified_at: datetime
    single_use: bool = False     # a recovery-code redemption: authorizes exactly one operation
    used: bool = False           # has authorized an operation already (so it is no longer "new" for always-fresh)


@dataclass(frozen=True)
class ResetRequest:
    reset_id: str
    tenant_id: str
    subject_user_id: str
    requested_by: str
    requested_at: datetime
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None


def authorizes(s: Optional[StepUp], user_id: str, now: datetime, always_fresh: bool) -> bool:
    """SQ-3 step-up rule for one operation (the repositories apply it atomically)."""
    if s is None or s.user_id != user_id or (now - s.verified_at).total_seconds() > STEP_UP_FRESHNESS_SECONDS:
        return False
    return not (always_fresh and s.used)


@dataclass
class InMemoryMfaRepository:
    _factors: dict = field(default_factory=dict)
    _step_ups: dict = field(default_factory=dict)
    _codes: dict = field(default_factory=dict)
    _resets: dict = field(default_factory=dict)

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
        self._factors[user_id] = replace(f, last_used_step=step, confirmed_at=f.confirmed_at or confirm_at)
        return True

    def record_step_up(self, session_id: str, user_id: str, at: datetime, *, single_use: bool = False) -> None:
        self._step_ups[session_id] = StepUp(session_id, user_id, at, single_use=single_use)

    def step_up(self, session_id: str) -> Optional[StepUp]:
        return self._step_ups.get(session_id)

    def authorize(self, session_id: str, user_id: str, *, now: datetime, always_fresh: bool) -> bool:
        """Spend the session's step-up on one operation: always-fresh and single-use step-ups are consumed; a normal
        step-up is marked used and stays valid for further normal operations within the freshness window."""
        s = self._step_ups.get(session_id)
        if not authorizes(s, user_id, now, always_fresh):
            return False
        if always_fresh or s.single_use:
            del self._step_ups[session_id]
        else:
            self._step_ups[session_id] = replace(s, used=True)
        return True

    def replace_recovery_codes(self, user_id: str, codes: list) -> None:
        self._codes[user_id] = list(codes)

    def recovery_codes(self, user_id: str) -> list:
        return list(self._codes.get(user_id, []))

    def use_recovery_code(self, user_id: str, code_id: str, at: datetime) -> bool:
        codes = self._codes.get(user_id, [])
        for i, rc in enumerate(codes):
            if rc.code_id == code_id and rc.used_at is None:
                codes[i] = replace(rc, used_at=at)
                return True
        return False

    def clear_user(self, user_id: str) -> None:
        """Assisted reset: the factor, the recovery codes and every step-up of the user are removed."""
        self._factors.pop(user_id, None)
        self._codes.pop(user_id, None)
        for sid in [k for k, v in self._step_ups.items() if v.user_id == user_id]:
            del self._step_ups[sid]

    def create_reset(self, r: ResetRequest) -> ResetRequest:
        self._resets[r.reset_id] = r
        return r

    def get_reset(self, reset_id: str, *, tenant_id: str) -> Optional[ResetRequest]:
        r = self._resets.get(reset_id)
        return r if r is not None and r.tenant_id == tenant_id else None

    def approve_reset(self, reset_id: str, *, tenant_id: str, approver: str, at: datetime) -> bool:
        r = self.get_reset(reset_id, tenant_id=tenant_id)
        if r is None or r.approved_at is not None:
            return False
        self._resets[reset_id] = replace(r, approved_by=approver, approved_at=at)
        return True
