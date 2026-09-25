"""FR-06 — HD video consultation with screen sharing: signalling and quality records (MVC-BUILD-RUNNER-001 U22).

Built BEHIND the REG-02 telemedicine gate (AC-FR-06-05): nothing here is reachable unless the consultation is
REMOTE_VIDEO, which the served app refuses to create until a LAWFUL counsel determination is recorded.
AC-FR-06-01: peer-to-peer WebRTC between the consultation's two participants; the served app relays the session
description / ICE messages (offer, answer, candidates, and the screen-share renegotiation) and nothing else.
AC-FR-06-02 (NFR-03, 720p minimum with adaptive bitrate): the call page reports the rendered resolution and the
browser's quality-limitation reason; a sample below 720p is compliant only when it carries an ABR step-down reason.
SPONSOR_QUEUE SQ-2 decides how AC-FR-06-01/02 are accepted; TURN relays and multi-instance signalling fan-out are
PRODUCTION infrastructure.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from repositories import RepositoryDenied

SIGNAL_KINDS = ("OFFER", "ANSWER", "ICE", "SCREEN_OFFER", "SCREEN_ANSWER", "BYE")
HD_MIN_HEIGHT = 720
STEP_DOWN_REASONS = ("bandwidth", "cpu")
MAX_PAYLOAD = 20_000


@dataclass(frozen=True)
class Signal:
    seq: int
    consultation_id: str
    tenant_id: str
    sender_id: str
    kind: str
    payload: dict
    at: datetime


@dataclass(frozen=True)
class QualitySample:
    consultation_id: str
    tenant_id: str
    reporter_id: str
    frame_width: int
    frame_height: int
    bitrate_kbps: int
    limitation_reason: Optional[str]
    at: datetime

    @property
    def hd(self) -> bool:
        return self.frame_height >= HD_MIN_HEIGHT

    @property
    def step_down(self) -> bool:
        return self.limitation_reason in STEP_DOWN_REASONS

    @property
    def compliant(self) -> bool:
        """NFR-03: HD, or below HD only with an adaptive-bitrate step-down record."""
        return self.hd or self.step_down


@dataclass
class SignallingHub:
    """Ephemeral relay (signalling is transient by nature). One process; fan-out across instances is PRODUCTION."""
    _signals: list = field(default_factory=list)
    _quality: list = field(default_factory=list)

    def post(self, *, consultation_id, tenant_id, sender_id, kind, payload, at) -> Signal:
        if kind not in SIGNAL_KINDS:
            raise RepositoryDenied(f"kind must be one of {SIGNAL_KINDS}")
        if not isinstance(payload, dict) or len(repr(payload)) > MAX_PAYLOAD:
            raise RepositoryDenied("a signal payload is an object of bounded size")
        s = Signal(seq=len(self._signals) + 1, consultation_id=consultation_id, tenant_id=tenant_id,
                   sender_id=sender_id, kind=kind, payload=payload, at=at)
        self._signals.append(s)
        return s

    def inbox(self, *, consultation_id, tenant_id, recipient_id, after: int) -> list:
        return [s for s in self._signals if s.consultation_id == consultation_id and s.tenant_id == tenant_id
                and s.sender_id != recipient_id and s.seq > after]

    def record_quality(self, q: QualitySample) -> QualitySample:
        if q.frame_width <= 0 or q.frame_height <= 0 or q.bitrate_kbps < 0:
            raise RepositoryDenied("a quality sample carries a positive resolution and a bitrate")
        self._quality.append(q)
        return q

    def quality(self, *, consultation_id, tenant_id) -> list:
        return [q for q in self._quality if q.consultation_id == consultation_id and q.tenant_id == tenant_id]
