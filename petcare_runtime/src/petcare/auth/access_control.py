from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Set


ROLE_OWNER = "Owner"
ROLE_VETERINARIAN = "Veterinarian"
ROLE_PHARMACY_OPERATOR = "Pharmacy Operator"
ROLE_PARTNER_CLINIC_ADMIN = "Partner Clinic Admin"
ROLE_PLATFORM_ADMIN = "Platform Admin"

PURPOSE_CONSULTATION = "purpose_consultation"
PURPOSE_MEDICATION_FULFILLMENT = "purpose_medication_fulfillment"
PURPOSE_EMERGENCY_REFERRAL = "purpose_emergency_referral"
PURPOSE_OWNER_SELF_SERVICE = "purpose_owner_self_service"
PURPOSE_PLATFORM_AUDIT = "purpose_platform_audit"
PURPOSE_SECURITY_INVESTIGATION = "purpose_security_investigation"

SCOPE_PROFILE = "SCOPE_PROFILE"
SCOPE_CARE_DELIVERY = "SCOPE_CARE_DELIVERY"
SCOPE_MEDICATION_FULFILLMENT = "SCOPE_MEDICATION_FULFILLMENT"
SCOPE_EMERGENCY_PACKET = "SCOPE_EMERGENCY_PACKET"
SCOPE_DOCUMENT_SHARING = "SCOPE_DOCUMENT_SHARING"


@dataclass(frozen=True)
class AccessContext:
    actor_id: str
    actor_role: str
    tenant_id: str
    clinic_id: Optional[str]
    purpose_of_use: str
    consent_scopes: Set[str]
    owner_id: Optional[str] = None
    assigned_veterinarian_id: Optional[str] = None
    assigned_pharmacy_operator_id: Optional[str] = None


@dataclass(frozen=True)
class ResourceContext:
    resource_type: str
    resource_id: str
    tenant_id: str
    clinic_id: Optional[str]
    owner_id: Optional[str]
    assigned_veterinarian_id: Optional[str] = None
    assigned_pharmacy_operator_id: Optional[str] = None
    document_shared: bool = False
    document_visibility_scope: Optional[str] = None
    consent_record_active: bool = False
    consent_granted_role: Optional[str] = None
    consent_purpose_of_use: Optional[str] = None


@dataclass(frozen=True)
class AccessDecision:
    allowed: bool
    reason_code: str


def _tenant_match(access: AccessContext, resource: ResourceContext) -> bool:
    return access.tenant_id == resource.tenant_id


def authorize_view_pet_profile(access: AccessContext, resource: ResourceContext) -> AccessDecision:
    if not _tenant_match(access, resource):
        return AccessDecision(False, "tenant_mismatch")

    if access.actor_role == ROLE_OWNER:
        if access.owner_id == resource.owner_id and access.purpose_of_use == PURPOSE_OWNER_SELF_SERVICE:
            return AccessDecision(True, "owner_self_service")
        return AccessDecision(False, "owner_not_authorized")

    if access.actor_role == ROLE_VETERINARIAN:
        if access.purpose_of_use == PURPOSE_CONSULTATION and SCOPE_CARE_DELIVERY in access.consent_scopes:
            return AccessDecision(True, "vet_care_delivery")
        return AccessDecision(False, "vet_missing_scope_or_purpose")

    if access.actor_role == ROLE_PLATFORM_ADMIN:
        if access.purpose_of_use in {PURPOSE_PLATFORM_AUDIT, PURPOSE_SECURITY_INVESTIGATION}:
            return AccessDecision(True, "platform_admin_purpose_limited")
        return AccessDecision(False, "platform_admin_wrong_purpose")

    return AccessDecision(False, "role_not_authorized")


def authorize_manage_consent(access: AccessContext, resource: ResourceContext) -> AccessDecision:
    if not _tenant_match(access, resource):
        return AccessDecision(False, "tenant_mismatch")

    if access.actor_role == ROLE_OWNER and access.owner_id == resource.owner_id:
        return AccessDecision(True, "owner_manage_consent")

    return AccessDecision(False, "consent_manage_denied")


def authorize_view_document(access: AccessContext, resource: ResourceContext) -> AccessDecision:
    if not _tenant_match(access, resource):
        return AccessDecision(False, "tenant_mismatch")

    if access.actor_role == ROLE_OWNER and access.owner_id == resource.owner_id:
        return AccessDecision(True, "owner_document_access")

    if access.actor_role == ROLE_VETERINARIAN:
        if access.purpose_of_use != PURPOSE_CONSULTATION:
            return AccessDecision(False, "vet_wrong_purpose")
        if SCOPE_DOCUMENT_SHARING not in access.consent_scopes:
            return AccessDecision(False, "vet_missing_document_scope")
        if not resource.document_shared:
            return AccessDecision(False, "document_not_shared")
        if not resource.consent_record_active:
            return AccessDecision(False, "document_missing_active_consent")
        if resource.consent_granted_role != ROLE_VETERINARIAN:
            return AccessDecision(False, "document_wrong_consent_role")
        if resource.consent_purpose_of_use != PURPOSE_CONSULTATION:
            return AccessDecision(False, "document_wrong_consent_purpose")
        return AccessDecision(True, "vet_document_shared")

    if access.actor_role == ROLE_PLATFORM_ADMIN:
        if access.purpose_of_use in {PURPOSE_PLATFORM_AUDIT, PURPOSE_SECURITY_INVESTIGATION}:
            return AccessDecision(True, "platform_admin_document_purpose_limited")
        return AccessDecision(False, "platform_admin_wrong_purpose")

    return AccessDecision(False, "document_access_denied")


def authorize_view_timeline(access: AccessContext, resource: ResourceContext) -> AccessDecision:
    if not _tenant_match(access, resource):
        return AccessDecision(False, "tenant_mismatch")

    if access.actor_role == ROLE_OWNER:
        if access.owner_id == resource.owner_id and access.purpose_of_use == PURPOSE_OWNER_SELF_SERVICE:
            return AccessDecision(True, "owner_timeline_access")
        return AccessDecision(False, "owner_timeline_denied")

    if access.actor_role == ROLE_VETERINARIAN:
        if access.purpose_of_use == PURPOSE_CONSULTATION and SCOPE_CARE_DELIVERY in access.consent_scopes:
            return AccessDecision(True, "vet_timeline_access")
        return AccessDecision(False, "vet_timeline_denied")

    if access.actor_role == ROLE_PLATFORM_ADMIN:
        if access.purpose_of_use in {PURPOSE_PLATFORM_AUDIT, PURPOSE_SECURITY_INVESTIGATION}:
            return AccessDecision(True, "platform_admin_timeline_purpose_limited")
        return AccessDecision(False, "platform_admin_wrong_purpose")

    return AccessDecision(False, "timeline_access_denied")


def authorize_upload_document(access: AccessContext, resource: ResourceContext) -> AccessDecision:
    if not _tenant_match(access, resource):
        return AccessDecision(False, "tenant_mismatch")

    if access.actor_role == ROLE_OWNER:
        if access.owner_id == resource.owner_id and access.purpose_of_use == PURPOSE_OWNER_SELF_SERVICE:
            return AccessDecision(True, "owner_upload_document")
        return AccessDecision(False, "owner_not_authorized")

    if access.actor_role == ROLE_VETERINARIAN:
        if access.purpose_of_use == PURPOSE_CONSULTATION and SCOPE_CARE_DELIVERY in access.consent_scopes:
            return AccessDecision(True, "vet_upload_document")
        return AccessDecision(False, "vet_missing_scope_or_purpose")

    return AccessDecision(False, "upload_access_denied")


# --- EP-03: Tele-Vet and Care Delivery ---

def authorize_request_consultation(access: AccessContext, resource: ResourceContext) -> AccessDecision:
    """Owner may request a consultation session for their own pet."""
    if not _tenant_match(access, resource):
        return AccessDecision(False, "tenant_mismatch")
    if access.actor_role == ROLE_OWNER:
        if access.owner_id == resource.owner_id and access.purpose_of_use == PURPOSE_OWNER_SELF_SERVICE:
            return AccessDecision(True, "owner_request_consultation")
        return AccessDecision(False, "owner_not_authorized")
    return AccessDecision(False, "consultation_request_denied")


def authorize_manage_consultation(access: AccessContext, resource: ResourceContext) -> AccessDecision:
    """Veterinarian may manage (start, complete, sign, escalate) a consultation session."""
    if not _tenant_match(access, resource):
        return AccessDecision(False, "tenant_mismatch")
    if access.actor_role == ROLE_VETERINARIAN:
        if access.purpose_of_use == PURPOSE_CONSULTATION:
            return AccessDecision(True, "vet_manage_consultation")
        return AccessDecision(False, "vet_wrong_purpose")
    return AccessDecision(False, "consultation_manage_denied")
