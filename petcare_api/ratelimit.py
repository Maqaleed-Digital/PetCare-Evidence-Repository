"""NFR-15 — API rate limiting (MVC-BUILD-RUNNER-001 v1.2 U24).

Ratified NFR-15: AUTHENTICATED_DEFAULT = 100 requests/minute per principal; ANONYMOUS_DEFAULT = 30 requests/minute per
client IP; excess -> HTTP 429 (with Retry-After); endpoint-specific stricter limits permitted; limits configurable and
auditable. The principal comes from the validated session, never from a header. The client IP is the TCP peer;
X-Forwarded-For is honoured only when the peer is on an explicit trusted-proxy list (default empty). Counters live in the
persistence layer (PostgreSQL in production: one row per (bucket, minute), incremented atomically), so every worker and
process shares one count.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

from repositories import RepositoryDenied

DEFAULT_PRINCIPAL_PER_MIN = 100
DEFAULT_ANONYMOUS_PER_MIN = 30
WINDOW_SECONDS = 60
ENV_PRINCIPAL = "PETCARE_RATE_LIMIT_PRINCIPAL_PER_MIN"
ENV_ANONYMOUS = "PETCARE_RATE_LIMIT_ANONYMOUS_PER_MIN"
ENV_TRUSTED_PROXIES = "PETCARE_TRUSTED_PROXIES"


@dataclass(frozen=True)
class Policy:
    principal_per_min: int = DEFAULT_PRINCIPAL_PER_MIN
    anonymous_per_min: int = DEFAULT_ANONYMOUS_PER_MIN
    trusted_proxies: frozenset = frozenset()
    source: str = "default"

    @classmethod
    def from_env(cls, env) -> "Policy":
        """Configurable (ratified): invalid values fail closed at startup rather than silently disabling limits."""
        def num(key, default):
            raw = env.get(key)
            if raw in (None, ""):
                return default
            if not str(raw).isdigit() or int(raw) <= 0:
                raise RepositoryDenied(f"{key} must be a positive integer")
            return int(raw)
        p, a = num(ENV_PRINCIPAL, DEFAULT_PRINCIPAL_PER_MIN), num(ENV_ANONYMOUS, DEFAULT_ANONYMOUS_PER_MIN)
        proxies = frozenset(x.strip() for x in (env.get(ENV_TRUSTED_PROXIES) or "").split(",") if x.strip())
        configured = any(env.get(k) not in (None, "") for k in (ENV_PRINCIPAL, ENV_ANONYMOUS, ENV_TRUSTED_PROXIES))
        return cls(p, a, proxies, "configured" if configured else "default")


def client_ip(peer: Optional[str], forwarded_for: Optional[str], trusted: frozenset) -> str:
    """The TCP peer, unless the peer is a trusted proxy: then the right-most X-Forwarded-For hop that is not itself a
    trusted proxy. An untrusted peer's X-Forwarded-For is ignored entirely (it is client-controlled)."""
    peer = peer or "unknown"
    if peer not in trusted or not forwarded_for:
        return peer
    for hop in reversed([h.strip() for h in forwarded_for.split(",") if h.strip()]):
        if hop not in trusted:
            return hop
    return peer


@dataclass(frozen=True)
class Decision:
    allowed: bool
    bucket: str
    limit: int
    count: int
    retry_after: int

    @property
    def first_excess(self) -> bool:
        return self.count == self.limit + 1


@dataclass
class Limiter:
    repo: object
    policy: Policy

    def hit(self, *, principal: Optional[str], peer: Optional[str], forwarded_for: Optional[str], now: float) -> Decision:
        if principal:
            bucket, limit = f"principal:{principal}", self.policy.principal_per_min
        else:
            bucket = f"ip:{client_ip(peer, forwarded_for, self.policy.trusted_proxies)}"
            limit = self.policy.anonymous_per_min
        window = int(now // WINDOW_SECONDS) * WINDOW_SECONDS
        count = self.repo.increment(bucket, window)
        retry = max(1, math.ceil(window + WINDOW_SECONDS - now))
        return Decision(allowed=count <= limit, bucket=bucket, limit=limit, count=count, retry_after=retry)


@dataclass
class InMemoryRateLimitRepository:
    """Memory-mode (non-production) counter. Production runs PETCARE_PERSISTENCE_MODE=postgres."""
    _counts: dict = field(default_factory=dict)

    def increment(self, bucket: str, window_start: int) -> int:
        k = (bucket, window_start)
        self._counts[k] = self._counts.get(k, 0) + 1
        return self._counts[k]
