"""The STORAGE role catalogue — an explicit allowlist, not a convention.

W0-F's identity migration requires that "no migrated identity may hold a role it
did not hold in the source" and that role mapping is an **explicit allowlist**
with no fuzzy matching. Neither was expressible before, because nothing
enumerated which roles may be STORED: `seed_user` and `register` accepted any
string, and the schema had no catalogue to check against.

## This is not the authorization catalogue, and the difference is the point

`main.py` already holds `VALID_ROLES`, the set `require_role()` will accept from
a session. That set is untouched by this module and must stay untouched: widening
it would change who may do what, which is an authorization change wearing a
persistence change's clothes.

This module answers a different question — **which role strings may be written to
the identity store** — and the two answers currently differ:

```
authorization (main.py)   display spellings only:  "Owner", "Veterinarian", ...
storage       (here)      display spellings AND the serving spellings that
                          seed_user/register actually mint: "owner", ...
```

That divergence is **recorded authority conflict CONF-01**, and it is live rather
than theoretical: `main.py` seeds its pilot identities with `"platform_admin"`,
`"veterinarian"` and `"owner"`, while `require_role()` accepts only
`"Platform Admin"`, `"Veterinarian"` and `"Owner"` — so those seeded identities
authenticate and are then refused by every protected route with
`403 Unknown role`. Tests that need a working session seed the display spelling
instead, which is why the suite does not show it.

**CONF-01 is NOT resolved here.** Picking one vocabulary changes authorization
outcomes for existing identities and is a Sponsor product decision, not a
persistence one. This module therefore admits exactly what the serving layer
already mints — no more, no less — so that adding a catalogue changes no
behaviour, and the conflict stays visible instead of being silently absorbed into
a storage constraint.

## Why the set is written positively

The retired role is refused by being ABSENT, never by being named. A denylist has
to name the value it forbids, which would put that literal back into the live
source tree `MVC-RETIRED-ROLE-CUSTODY-001` requires to hold zero occurrences of
it — the guard and the defect would look identical to a scanner. An allowlist
forbids it, and every other unforeseen value, without naming any of them.

This is a SECOND refusal, not a replacement for the first: `main.py` keeps the
retired role out of `VALID_ROLES`, so it could never be honoured as authority.
Now it cannot be stored either, so it cannot reach authorization at all.

## Why there is a privilege order

`MIG-03` requires that a migration can never increase privilege. "Did the role
change" is not enough to check that: a mapping between two spellings of the same
role would fail an equality check while being perfectly safe, and a mapping that
quietly promoted would pass any check that only compared strings. Ranking
CONCEPTS rather than spellings makes the real claim — *no identity ends with
authority it did not start with* — checkable.

The order is a statement about authority over OTHER identities and their data,
not about clinical seniority. A veterinarian outranks an owner here because a
veterinarian reads records across the owners of a tenant; it says nothing about
professional standing, which W0-I models separately and time-boundedly.
"""
from __future__ import annotations

import os
import sys
from typing import Mapping, Optional

# The display spellings are imported rather than re-typed. A second literal copy
# would drift from the canonical one, and the drift would be invisible: both
# copies would still look like "the role names".
_RUNTIME_SRC = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "petcare_runtime", "src",
)
if os.path.isdir(_RUNTIME_SRC) and _RUNTIME_SRC not in sys.path:
    sys.path.insert(0, _RUNTIME_SRC)

from petcare.auth.access_control import (  # noqa: E402
    ROLE_OWNER as DISPLAY_OWNER,
    ROLE_PARTNER_CLINIC_ADMIN as DISPLAY_PARTNER_CLINIC_ADMIN,
    ROLE_PLATFORM_ADMIN as DISPLAY_PLATFORM_ADMIN,
    ROLE_VETERINARIAN as DISPLAY_VETERINARIAN,
)

#: Concepts. Spelling-independent, so privilege comparisons cannot be fooled by
#: a vocabulary difference in either direction.
CONCEPT_OWNER = "OWNER"
CONCEPT_VETERINARIAN = "VETERINARIAN"
CONCEPT_PARTNER_CLINIC_ADMIN = "PARTNER_CLINIC_ADMIN"
CONCEPT_PLATFORM_ADMIN = "PLATFORM_ADMIN"

#: The spellings the serving layer mints today: `seed_user` in main.py and the
#: `role` field of an invite-gated registration.
SERVING_OWNER = "owner"
SERVING_VETERINARIAN = "veterinarian"
SERVING_PARTNER_CLINIC_ADMIN = "partner_clinic_admin"
SERVING_PLATFORM_ADMIN = "platform_admin"

#: Every storable spelling, and the concept it denotes. Both vocabularies appear
#: because both are in live use (CONF-01, above). The retired role appears in
#: neither.
CONCEPT_BY_SPELLING: Mapping[str, str] = {
    SERVING_OWNER: CONCEPT_OWNER,
    DISPLAY_OWNER: CONCEPT_OWNER,
    SERVING_VETERINARIAN: CONCEPT_VETERINARIAN,
    DISPLAY_VETERINARIAN: CONCEPT_VETERINARIAN,
    SERVING_PARTNER_CLINIC_ADMIN: CONCEPT_PARTNER_CLINIC_ADMIN,
    DISPLAY_PARTNER_CLINIC_ADMIN: CONCEPT_PARTNER_CLINIC_ADMIN,
    SERVING_PLATFORM_ADMIN: CONCEPT_PLATFORM_ADMIN,
    DISPLAY_PLATFORM_ADMIN: CONCEPT_PLATFORM_ADMIN,
}

#: Every role string that may be STORED. Anything else is refused.
VALID_ROLES = frozenset(CONCEPT_BY_SPELLING)

CONCEPT_PRIVILEGE_RANK: Mapping[str, int] = {
    CONCEPT_OWNER: 1,
    CONCEPT_VETERINARIAN: 2,
    CONCEPT_PARTNER_CLINIC_ADMIN: 3,
    CONCEPT_PLATFORM_ADMIN: 4,
}


def is_valid_role(role: object) -> bool:
    return isinstance(role, str) and role in CONCEPT_BY_SPELLING


def concept_of(role: str) -> Optional[str]:
    return CONCEPT_BY_SPELLING.get(role)


def privilege_rank(role: str) -> int:
    """Rank, or raise. An unknown role has no rank and is never given one:
    defaulting it to the lowest would make an unrecognised role look safe."""
    concept = CONCEPT_BY_SPELLING.get(role)
    if concept is None:
        raise ValueError(f"role {role!r} is not in the catalogue and has no rank")
    return CONCEPT_PRIVILEGE_RANK[concept]


def is_privilege_elevation(*, source_role: str, target_role: str) -> bool:
    """Whether mapping source -> target would raise authority.

    An unknown role on either side is not "not an elevation" — it is
    unanswerable, and is reported as an elevation so the caller fails closed on
    a question that was never decided rather than proceeding as though it had
    been answered "no".
    """
    try:
        return privilege_rank(target_role) > privilege_rank(source_role)
    except ValueError:
        return True
