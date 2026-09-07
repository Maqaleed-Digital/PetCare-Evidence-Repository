"""Professional authority — human clinical authority, held by a person.

W0-I / BRD V3.2 §28 / PRD-14. Kept in its own package precisely because §28's
first requirement is that this authority is **separate from device sealing
authority and must not be conflated**. Two concepts that must not merge should
not share a module.
"""
from .authority import (
    ProfessionalAuthorityGrant,
    ProfessionalAuthorityRegistry,
    ProfessionalClass,
    AuthorityDenied,
    DeviceSealingAuthority,
)

__all__ = [
    "ProfessionalAuthorityGrant",
    "ProfessionalAuthorityRegistry",
    "ProfessionalClass",
    "AuthorityDenied",
    "DeviceSealingAuthority",
]
