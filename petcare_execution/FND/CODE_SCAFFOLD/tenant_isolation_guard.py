from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


TENANT_HEADER = "x-tenant-id"
UUID_RE = re.compile(r"^[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}$")


class TenantIsolationError(ValueError):
    pass


class MissingTenantHeader(TenantIsolationError):
    pass


class InvalidTenantHeader(TenantIsolationError):
    pass


def normalize_tenant_id(raw: Optional[str]) -> str:
    if raw is None:
        raise MissingTenantHeader(f"{TENANT_HEADER} is required")
    v = raw.strip()
    if not v:
        raise MissingTenantHeader(f"{TENANT_HEADER} is required")
    if not UUID_RE.match(v):
        raise InvalidTenantHeader(f"{TENANT_HEADER} must be a UUID")
    return v.lower()


@dataclass(frozen=True)
class TenantContext:
    tenant_id: str

    @staticmethod
    def from_header_value(raw: Optional[str]) -> "TenantContext":
        return TenantContext(tenant_id=normalize_tenant_id(raw))


def require_tenant_context(raw: Optional[str]) -> TenantContext:
    return TenantContext.from_header_value(raw)
