"""Derive a role the catalogue refuses, without ever naming one.

`petcare_api` is a live source tree under `MVC-RETIRED-ROLE-CUSTODY-001`, which
requires zero occurrences of the retired literal — tests included. A test that
typed it would need a registered exemption, and an exemption whose reason is
"this file is a guard" is indistinguishable, to a scanner, from the defect.

So the value is derived: every `ROLE_*` constant the estate defines anywhere,
minus the canonical authority catalogue. That also covers roles nobody has
retired yet — a constant added to the estate and not added to the catalogue is
caught here rather than the next time somebody remembers to look.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from roles import ALLOWED_ROLES  # noqa: E402


def roles_the_catalogue_refuses() -> list[str]:
    """Every role token the estate defines that is NOT an authority token."""
    from petcare.auth import access_control

    defined = {
        getattr(access_control, name)
        for name in dir(access_control)
        if name.startswith("ROLE_") and isinstance(getattr(access_control, name), str)
    }
    return sorted(defined - set(ALLOWED_ROLES))


def a_role_the_catalogue_refuses() -> str:
    """One such role. Raises if there is none, rather than returning a value
    that would let a control pass having tested nothing."""
    refused = roles_the_catalogue_refuses()
    if not refused:
        raise AssertionError(
            "the estate defines no role outside the canonical catalogue, so a "
            "control using this helper would pass having tested nothing"
        )
    return refused[0]
