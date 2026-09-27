"""SQ-3 operations completed by MVC-EPC-D-001 Lane D, unit D1 (Sponsor act MVC-SQ3-NFR08-STEP-UP-001).

#12 tenant payout details and #13 tenant bank details (both always-fresh), #14 staff invitation credentials, #15 API
keys. Every secret is shown ONCE and stored one-way (credentials, API keys) or encrypted (IBAN). Nothing here decides
step-up: the served app enforces it for every operation mapped in mfa.SQ3_OPERATIONS.
"""
from __future__ import annotations

import hashlib
import re
import secrets
from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Optional

from repositories import RepositoryDenied

PAYOUT_METHODS = ("BANK_TRANSFER",)
PAYOUT_SCHEDULES = ("WEEKLY", "BIWEEKLY", "MONTHLY")
#: Saudi IBAN: "SA" + 2 check digits + 20 characters (ISO 13616; mod-97 verified below).
SA_IBAN = re.compile(r"^SA\d{2}[0-9A-Z]{20}$")
CREDENTIAL_PREFIX = "sha256:"
API_KEY_PREFIX = "pck_"


def normalise_iban(value: str) -> str:
    return re.sub(r"\s+", "", str(value)).upper()


def iban_valid(iban: str) -> bool:
    """ISO 13616 mod-97 check for a Saudi IBAN."""
    if not SA_IBAN.match(iban):
        return False
    moved = iban[4:] + iban[:4]
    digits = "".join(str(int(c, 36)) for c in moved)
    return int(digits) % 97 == 1


def mask_iban(last4: str) -> str:
    return f"SA** **** **** **** **** {last4}"


def credential_key(raw: str) -> str:
    """How an issued credential is stored and looked up: one-way, never the credential itself."""
    return CREDENTIAL_PREFIX + hashlib.sha256(raw.strip().encode()).hexdigest()


def new_credential() -> str:
    raw = secrets.token_urlsafe(18).replace("-", "").replace("_", "")[:20].upper()
    return "-".join(raw[i:i + 5] for i in range(0, 20, 5))


def new_api_key() -> tuple:
    """(key shown once, key_id, prefix, sha256). 256 random bits."""
    key = API_KEY_PREFIX + secrets.token_urlsafe(32)
    return key, secrets.token_hex(8), key[:12], hashlib.sha256(key.encode()).hexdigest()


@dataclass(frozen=True)
class PayoutDetails:
    tenant_id: str
    payout_method: str
    payout_schedule: str
    minimum_payout_halalas: int
    updated_by: str
    updated_at: datetime

    def read_model(self) -> dict:
        return {"payout_method": self.payout_method, "payout_schedule": self.payout_schedule,
                "minimum_payout_halalas": self.minimum_payout_halalas, "updated_by": self.updated_by,
                "updated_at": self.updated_at.isoformat()}


@dataclass(frozen=True)
class BankDetails:
    tenant_id: str
    bank_name: str
    account_holder: str
    iban_nonce: bytes
    iban_ciphertext: bytes
    iban_last4: str
    updated_by: str
    updated_at: datetime

    def read_model(self) -> dict:
        """Never the IBAN: the masked form only."""
        return {"bank_name": self.bank_name, "account_holder": self.account_holder, "iban_masked": mask_iban(self.iban_last4),
                "updated_by": self.updated_by, "updated_at": self.updated_at.isoformat()}


@dataclass(frozen=True)
class ApiKey:
    key_id: str
    tenant_id: str
    name: str
    prefix: str
    key_sha256: str
    created_by: str
    created_at: datetime
    revoked_at: Optional[datetime] = None

    def read_model(self) -> dict:
        return {"key_id": self.key_id, "name": self.name, "prefix": self.prefix, "created_by": self.created_by,
                "created_at": self.created_at.isoformat(),
                "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None}


def validate_payout(p: PayoutDetails) -> None:
    if p.payout_method not in PAYOUT_METHODS or p.payout_schedule not in PAYOUT_SCHEDULES or p.minimum_payout_halalas < 0:
        raise RepositoryDenied("payout details are not valid")


@dataclass
class InMemorySq3OpsRepository:
    _payout: dict = field(default_factory=dict)
    _bank: dict = field(default_factory=dict)
    _keys: dict = field(default_factory=dict)

    def set_payout(self, p: PayoutDetails) -> PayoutDetails:
        validate_payout(p)
        self._payout[p.tenant_id] = p
        return p

    def payout(self, *, tenant_id: str) -> Optional[PayoutDetails]:
        return self._payout.get(tenant_id)

    def set_bank(self, b: BankDetails) -> BankDetails:
        self._bank[b.tenant_id] = b
        return b

    def bank(self, *, tenant_id: str) -> Optional[BankDetails]:
        return self._bank.get(tenant_id)

    def add_api_key(self, k: ApiKey) -> ApiKey:
        if any(x.key_sha256 == k.key_sha256 for x in self._keys.values()):
            raise RepositoryDenied("duplicate key")
        self._keys[k.key_id] = k
        return k

    def api_keys(self, *, tenant_id: str) -> list:
        return sorted((k for k in self._keys.values() if k.tenant_id == tenant_id), key=lambda k: (k.created_at, k.key_id))

    def revoke_api_key(self, key_id: str, *, tenant_id: str, at: datetime) -> bool:
        k = self._keys.get(key_id)
        if k is None or k.tenant_id != tenant_id or k.revoked_at is not None:
            return False
        self._keys[key_id] = replace(k, revoked_at=at)
        return True
