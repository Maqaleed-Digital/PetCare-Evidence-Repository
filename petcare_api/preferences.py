"""FR-09 — a language choice that survives a new session (MVC-BUILD-RUNNER-001 U3).

Ratified criterion AC-FR-09-02. The choice is held server-side against the
identity (migration 0038), so it is restored on sign-in from any device, not
only from the browser's local storage. Arabic is the default when nothing is
stored: FR-09 makes Arabic primary.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Protocol

from repositories import RepositoryDenied

LANG_AR = "ar"
LANG_EN = "en"
LANGUAGES = frozenset({LANG_AR, LANG_EN})
DEFAULT_LANGUAGE = LANG_AR


def validate_language(language: str) -> None:
    if language not in LANGUAGES:
        raise RepositoryDenied(f"language {language!r} is not one of {sorted(LANGUAGES)}")


class PreferenceRepository(Protocol):
    def get_language(self, user_id: str) -> Optional[str]: ...
    def set_language(self, user_id: str, *, tenant_id: str, language: str, at: datetime) -> str: ...


@dataclass
class InMemoryPreferenceRepository:
    """Non-production store; refuses an unregistered tenant as the foreign key does."""

    tenants: object
    _rows: dict = field(default_factory=dict)

    def get_language(self, user_id: str) -> Optional[str]:
        row = self._rows.get(user_id)
        return row[1] if row else None

    def set_language(self, user_id: str, *, tenant_id: str, language: str, at: datetime) -> str:
        validate_language(language)
        if self.tenants.get(tenant_id) is None:
            raise RepositoryDenied(f"tenant {tenant_id!r} is not registered")
        self._rows[user_id] = (tenant_id, language, at)
        return language
