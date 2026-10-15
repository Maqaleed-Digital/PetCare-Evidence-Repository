"""CO-13 — rate visit (MVC-EPC-D-001 Lane D, D2r; R21.4 remaining owner screens).

The owner rates ONE of their own COMPLETED consultations once: a score of 1..5 and an optional comment. Insert-only — a rating is
what the owner said at the time, never silently edited. Owner, tenant, consultation and veterinarian are written from the session
and the consultation by petcare_api/main.py, never from the request. The consultation's veterinarian and the clinic's
administrator may read it; nothing here publishes or aggregates ratings (a public rating is PUB-02/PUB-03 work, not this screen).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Protocol

from repositories import RepositoryDenied

SCORES = range(1, 6)
MAX_COMMENT = 500


@dataclass(frozen=True)
class VisitRating:
    session_id: str
    tenant_id: str
    owner_id: str
    veterinarian_id: str
    score: int
    comment: str
    rated_at: datetime

    def to_read_model(self) -> dict:
        return {"session_id": self.session_id, "score": self.score, "comment": self.comment,
                "rated_at": self.rated_at.isoformat()}


def validate_rating(r: VisitRating) -> None:
    if not isinstance(r.score, int) or isinstance(r.score, bool) or r.score not in SCORES:
        raise RepositoryDenied("a score is a whole number from 1 to 5")
    if len(r.comment) > MAX_COMMENT:
        raise RepositoryDenied(f"a comment is at most {MAX_COMMENT} characters")
    if not (r.owner_id and r.veterinarian_id and r.tenant_id):
        raise RepositoryDenied("a rating names its owner, veterinarian and tenant")


class RatingExists(Exception):
    """The consultation is already rated (once, insert-only)."""


class VisitRatingRepository(Protocol):
    def create(self, r: VisitRating) -> VisitRating: ...
    def for_session(self, session_id: str, *, tenant_id: str) -> Optional[VisitRating]: ...


@dataclass
class InMemoryVisitRatingRepository:
    _rows: dict = field(default_factory=dict)

    def create(self, r):
        validate_rating(r)
        if (r.tenant_id, r.session_id) in self._rows:
            raise RatingExists(r.session_id)
        self._rows[(r.tenant_id, r.session_id)] = r
        return r

    def for_session(self, session_id, *, tenant_id):
        return self._rows.get((tenant_id, session_id))
