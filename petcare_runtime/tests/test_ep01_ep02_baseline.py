from petcare.api.routes_ep01_ep02 import create_consent, create_pet_profile, get_pet_profile
from petcare.auth.access_control import (
    AccessContext,
    ResourceContext,
    PURPOSE_OWNER_SELF_SERVICE,
    PURPOSE_CONSULTATION,
    ROLE_OWNER,
    ROLE_VETERINARIAN,
    SCOPE_CARE_DELIVERY,
)


def test_owner_can_view_own_pet_profile() -> None:
    access = AccessContext(
        actor_id="owner-1",
        actor_role=ROLE_OWNER,
        tenant_id="tenant-1",
        clinic_id=None,
        purpose_of_use=PURPOSE_OWNER_SELF_SERVICE,
        consent_scopes=set(),
        owner_id="owner-1",
    )
    resource = ResourceContext(
        resource_type="pet",
        resource_id="pet-1",
        tenant_id="tenant-1",
        clinic_id=None,
        owner_id="owner-1",
    )
    result = get_pet_profile(access, resource, correlation_id="corr-1")
    assert result["allowed"] is True


def test_vet_denied_without_scope() -> None:
    access = AccessContext(
        actor_id="vet-1",
        actor_role=ROLE_VETERINARIAN,
        tenant_id="tenant-1",
        clinic_id="clinic-1",
        purpose_of_use=PURPOSE_CONSULTATION,
        consent_scopes=set(),
    )
    resource = ResourceContext(
        resource_type="pet",
        resource_id="pet-1",
        tenant_id="tenant-1",
        clinic_id="clinic-1",
        owner_id="owner-1",
    )
    result = get_pet_profile(access, resource, correlation_id="corr-2")
    assert result["allowed"] is False
    assert result["reason_code"] == "vet_missing_scope_or_purpose"


def test_vet_allowed_with_care_delivery_scope() -> None:
    access = AccessContext(
        actor_id="vet-1",
        actor_role=ROLE_VETERINARIAN,
        tenant_id="tenant-1",
        clinic_id="clinic-1",
        purpose_of_use=PURPOSE_CONSULTATION,
        consent_scopes={SCOPE_CARE_DELIVERY},
    )
    resource = ResourceContext(
        resource_type="pet",
        resource_id="pet-1",
        tenant_id="tenant-1",
        clinic_id="clinic-1",
        owner_id="owner-1",
    )
    result = get_pet_profile(access, resource, correlation_id="corr-3")
    assert result["allowed"] is True


def test_owner_can_create_consent() -> None:
    access = AccessContext(
        actor_id="owner-1",
        actor_role=ROLE_OWNER,
        tenant_id="tenant-1",
        clinic_id=None,
        purpose_of_use=PURPOSE_OWNER_SELF_SERVICE,
        consent_scopes=set(),
        owner_id="owner-1",
    )
    resource = ResourceContext(
        resource_type="pet",
        resource_id="pet-1",
        tenant_id="tenant-1",
        clinic_id=None,
        owner_id="owner-1",
    )
    result = create_consent(
        access,
        resource,
        consent_scope="SCOPE_CARE_DELIVERY",
        purpose_of_use="purpose_consultation",
        correlation_id="corr-4",
    )
    assert result["allowed"] is True
    assert result["consent_record"].status == "active"


def test_create_pet_profile_returns_created() -> None:
    result = create_pet_profile(
        tenant_id="tenant-1",
        owner_id="owner-1",
        name="Bella",
        species="dog",
    )
    assert result["status"] == "created"
    assert result["pet_id"]
