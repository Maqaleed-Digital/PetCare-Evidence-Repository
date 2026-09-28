"""One-time account tokens and email-verification state (MVC-EPC-D-001 Lane D, D2 — owner self-registration).

Tokens are 256-bit random strings shown ONLY in the message sent to the owner; the store keeps sha256(token). A token
is single use (`consume` succeeds once) and expires. Email verification: an identity with a pending row must verify
before it may sign in; identities without a row (seeded, invited) are unaffected.
"""
from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from typing import Optional

#: Token purposes (the DB CHECK in migration 0056 lists the same two values).
PURPOSE_VERIFY = "EMAIL_VERIFICATION"
PURPOSE_RESET = "PASSWORD_RESET"
TTL = {PURPOSE_VERIFY: timedelta(hours=24), PURPOSE_RESET: timedelta(minutes=30)}


def digest(token: str) -> str:
    return hashlib.sha256(str(token).encode()).hexdigest()


def new_token() -> str:
    return secrets.token_urlsafe(32)


@dataclass(frozen=True)
class AccountToken:
    token_sha256: str
    user_id: str
    purpose: str
    created_at: datetime
    expires_at: datetime
    used_at: Optional[datetime] = None


@dataclass
class InMemoryAccountTokenRepository:
    _tokens: dict = field(default_factory=dict)
    _verification: dict = field(default_factory=dict)       # user_id -> (required_since, verified_at)

    def issue(self, user_id: str, purpose: str, *, now: datetime) -> str:
        raw = new_token()
        self._tokens[digest(raw)] = AccountToken(digest(raw), user_id, purpose, now, now + TTL[purpose])
        return raw

    def consume(self, raw: str, purpose: str, *, now: datetime) -> Optional[str]:
        """The user_id the token belongs to, once; None if unknown, wrong purpose, expired or already used."""
        t = self._tokens.get(digest(raw))
        if t is None or t.purpose != purpose or t.used_at is not None or now >= t.expires_at:
            return None
        self._tokens[t.token_sha256] = replace(t, used_at=now)
        return t.user_id

    def require_verification(self, user_id: str, *, now: datetime) -> None:
        self._verification[user_id] = (now, None)

    def mark_verified(self, user_id: str, *, now: datetime) -> None:
        since, _ = self._verification.get(user_id, (now, None))
        self._verification[user_id] = (since, now)

    def verification_pending(self, user_id: str) -> bool:
        v = self._verification.get(user_id)
        return v is not None and v[1] is None
