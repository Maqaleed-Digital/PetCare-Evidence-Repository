"""The canonical role authority — machine IDs only.

Sponsor ruling `PRE2_RULING=2-C`, recorded in
`MVC-PREPROD-SPONSOR-DECISION-PACK-001`:

> machine role IDs are the sole authorization authority; display/localized
> labels are presentation only.

## What this module is, and what it is not

`ROLE_*` below are **authority tokens**. They are compared for equality by
`require_role()`, constrained by the `user_identity.role` CHECK, minted by
registration, carried in the session, and mapped to UI route categories by the
web middleware. Nothing else is an authority token.

`DISPLAY_LABELS` are **presentation**. They may be translated, renamed, or
replaced by an i18n key without any authorization outcome changing — and
`ROLE-09` asserts exactly that. This module is the only place the two meet, and
they meet as a lookup, never as a comparison.

## Why a display label can never be authority

A token that must be translated into Arabic cannot also be the token
authorization compares. The estate already held the labels in
`petcare_web/lib/strings.ts` with `ar`/`en` pairs; the defect CONF-01 recorded
was that a *second* set of the same names had become the thing `require_role()`
tested.

## The conflict this closes

Before this ruling the estate held three vocabularies. The serving layer minted
machine IDs, `require_role()` accepted only the display forms, and the web
middleware aliased the machine IDs — so **every identity the system created was
refused by every protected route with `403 Unknown role`**. The suite did not
show it because tests that needed a working session seeded the display form
directly, which no production path ever produced.

## The retired role

It is absent, and it is absent by omission rather than by being named. A denylist
would have to write the retired literal into a live source tree that
`MVC-RETIRED-ROLE-CUSTODY-001` requires to hold zero occurrences of it — the
guard and the defect would be indistinguishable to a scanner. `pharmacy` is
likewise not here, per `PHARMACY_ROLE=REMOVE`: it is not an authorization
principal, and this module is where authorization principals are defined.

`petcare_runtime` keeps its own role tokens for its own domain functions. Those
are a different package's vocabulary, not display labels, and the serving layer
does not use them — `main.py` imported four of them and the domain authorizer
they belong to was never called.
"""
from __future__ import annotations

from typing import Mapping

# ---------------------------------------------------------------------------
# Authority tokens. The ONLY values any authorization decision may compare.
# ---------------------------------------------------------------------------

ROLE_PLATFORM_ADMIN = "platform_admin"
ROLE_PARTNER_CLINIC_ADMIN = "partner_clinic_admin"
ROLE_VETERINARIAN = "veterinarian"
ROLE_OWNER = "owner"

#: Every role that may be stored, minted, or presented as authority.
ALLOWED_ROLES = frozenset({
    ROLE_PLATFORM_ADMIN,
    ROLE_PARTNER_CLINIC_ADMIN,
    ROLE_VETERINARIAN,
    ROLE_OWNER,
})

#: Retained as the name the storage layer and the tests already use. Identical
#: to ALLOWED_ROLES by construction rather than by coincidence: two sets that
#: were meant to be equal and drifted is how a role becomes storable but not
#: authorisable, which is the shape of CONF-01.
VALID_ROLES = ALLOWED_ROLES

# ---------------------------------------------------------------------------
# Presentation. NEVER compared, NEVER stored as a role, NEVER authority.
# ---------------------------------------------------------------------------

#: English labels, for surfaces with no i18n catalogue of their own. The web
#: holds the real ar/en pairs in `petcare_web/lib/strings.ts`; these exist so a
#: backend response can carry a human-readable name without any caller being
#: tempted to reuse the authority token as one.
#:
#: `ROLE-03` asserts a label cannot authorize and `ROLE-09` asserts changing a
#: label changes no authorization outcome.
DISPLAY_LABELS: Mapping[str, str] = {
    ROLE_PLATFORM_ADMIN: "Platform Admin",
    ROLE_PARTNER_CLINIC_ADMIN: "Partner Clinic Admin",
    ROLE_VETERINARIAN: "Veterinarian",
    ROLE_OWNER: "Owner",
}


def display_label(role: str) -> str:
    """The label for a role id. Raises for an unknown role.

    Deliberately raises rather than echoing the input: returning the unknown
    value would put an unvalidated string into a rendered surface, and a caller
    that saw its own input come back would reasonably conclude the role was
    recognised.
    """
    if role not in DISPLAY_LABELS:
        raise ValueError(f"role {role!r} is not in the catalogue and has no label")
    return DISPLAY_LABELS[role]


# ---------------------------------------------------------------------------
# Privilege ordering — for migration guards, not for route authorization
# ---------------------------------------------------------------------------

#: Authority over OTHER identities and their data. Not clinical seniority: a
#: veterinarian outranks an owner here because a veterinarian reads records
#: across the owners of a tenant, which says nothing about professional
#: standing. W0-I models that separately and time-boundedly.
ROLE_PRIVILEGE_RANK: Mapping[str, int] = {
    ROLE_OWNER: 1,
    ROLE_VETERINARIAN: 2,
    ROLE_PARTNER_CLINIC_ADMIN: 3,
    ROLE_PLATFORM_ADMIN: 4,
}


def is_valid_role(role: object) -> bool:
    """Exact membership. No case folding, no trimming, no normalisation.

    `ROLE-05` and `ROLE-06`: a comparison that normalised would let
    `"Platform_Admin"` or `" platform_admin "` become authority, and the
    promotion would be invisible at the call site.
    """
    return isinstance(role, str) and role in ALLOWED_ROLES


def privilege_rank(role: str) -> int:
    """Rank, or raise. An unknown role has no rank and is never given one:
    defaulting it to the lowest would make an unrecognised role look safe."""
    if role not in ROLE_PRIVILEGE_RANK:
        raise ValueError(f"role {role!r} is not in the catalogue and has no rank")
    return ROLE_PRIVILEGE_RANK[role]


def is_privilege_elevation(*, source_role: str, target_role: str) -> bool:
    """Whether mapping source -> target would raise authority.

    An unknown role on either side is not "not an elevation" — it is
    unanswerable, and is reported as an elevation so the caller fails closed on
    a question that was never decided.
    """
    try:
        return privilege_rank(target_role) > privilege_rank(source_role)
    except ValueError:
        return True
