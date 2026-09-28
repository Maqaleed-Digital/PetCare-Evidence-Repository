"""Email adapter (MVC-EPC-D-001 Lane D; first used by D2 owner self-registration, completed with contract tests in D6).

Interface: `send(EmailMessage)`. Implementations:
- FakeEmailAdapter — labelled FAKE; delivers nothing; records messages in memory and, when PETCARE_FAKE_EMAIL_OUTBOX is
  set, appends them to that JSON-lines file (how the full-stack journey suite reads a verification link). Refused when
  PETCARE_DEPLOYMENT_ENV=production.
- UnconfiguredEmailAdapter — the default: every send raises EmailUnavailable, so any feature that needs email FAILS
  CLOSED (503) instead of pretending to have sent it.
No real provider is called by this lane; the production provider binding is an external act.
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from typing import Optional

ENV_ADAPTER = "PETCARE_EMAIL_ADAPTER"
ENV_OUTBOX = "PETCARE_FAKE_EMAIL_OUTBOX"
ENV_DEPLOYMENT = "PETCARE_DEPLOYMENT_ENV"


class EmailUnavailable(Exception):
    """No email provider is configured (or a fake was requested in production)."""


@dataclass(frozen=True)
class EmailMessage:
    to: str
    template: str                 # e.g. "EMAIL_VERIFICATION", "PASSWORD_RESET"
    locale: str                   # "ar" | "en"
    params: dict = field(default_factory=dict)


class UnconfiguredEmailAdapter:
    LABEL = "UNCONFIGURED"

    def send(self, message: EmailMessage) -> None:
        raise EmailUnavailable("no email provider is configured")


class FakeEmailAdapter:
    LABEL = "FAKE — non-production; nothing is delivered"

    def __init__(self, outbox_path: Optional[str] = None) -> None:
        self.outbox: list = []
        self._path = outbox_path

    def send(self, message: EmailMessage) -> None:
        self.outbox.append(message)
        if self._path:
            with open(self._path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps({"label": "FAKE", **asdict(message)}, ensure_ascii=False) + "\n")


def build_email_adapter(env=None):
    env = os.environ if env is None else env
    mode = (env.get(ENV_ADAPTER) or "").strip().lower()
    if mode == "fake":
        if (env.get(ENV_DEPLOYMENT) or "").strip().lower() == "production":
            raise EmailUnavailable("the FAKE email adapter is refused in production")
        return FakeEmailAdapter(env.get(ENV_OUTBOX) or None)
    return UnconfiguredEmailAdapter()
