"""W0-I — T-PROF-01..04, BRD V3.2 §28.

> Human/professional authority is separate from device sealing authority and
> must not be conflated. Sole-practitioner initial authority grant is specified
> (PRD-14): a one-vet practice must be able to bootstrap without a second
> PRINCIPAL, and the bootstrap is a recorded act, never a silent exception.

`T-PROF-01`, `T-PROF-02` and `T-PROF-04` are ARMED negative controls: each
asserts that a specific attempt is DENIED. `T-PROF-03` asserts the inverse — the
bootstrap must be ALLOWED, and must leave a record.
"""
from datetime import datetime, timedelta, timezone

import pytest

from petcare.professional_authority import (
    AuthorityDenied,
    DeviceSealingAuthority,
    ProfessionalAuthorityGrant,
    ProfessionalAuthorityRegistry,
    ProfessionalClass,
)

T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
T1 = T0 + timedelta(days=30)
T2 = T0 + timedelta(days=60)


@pytest.fixture
def audit():
    return []


@pytest.fixture
def registry(audit):
    return ProfessionalAuthorityRegistry(audit_sink=audit.append)


def test_baseline_a_granted_vet_can_attest(registry):
    """Without this the denials below could pass because nothing ever works."""
    registry.grant(
        actor_id="vet1", tenant_id="t1",
        professional_class=ProfessionalClass.VETERINARIAN,
        granted_by="principal1", grant_reason="employment",
        effective_from=T0,
    )
    att = registry.attest_clinical_record(
        actor_id="vet1", record_id="r1", occurred_at=T1
    )
    assert att["professional_class"] == ProfessionalClass.VETERINARIAN


def test_t_prof_01_attesting_without_authority_at_that_time_is_denied(registry):
    """T-PROF-01 (ARMED) — authority is evaluated at the time of the act.

    The subtle case is the second half: a vet granted authority TODAY must not be
    able to attest a record from BEFORE the grant. A naive `is_authorised(actor)`
    check passes that case, because it only ever asks about now.
    """
    with pytest.raises(AuthorityDenied):
        registry.attest_clinical_record(actor_id="nobody", record_id="r1", occurred_at=T1)

    registry.grant(
        actor_id="vet1", tenant_id="t1",
        professional_class=ProfessionalClass.VETERINARIAN,
        granted_by="principal1", grant_reason="employment",
        effective_from=T1,
    )
    # Holds now...
    assert registry.held_at("vet1", T2) is True
    # ...but did not hold before the grant, and cannot attest back across it.
    with pytest.raises(AuthorityDenied):
        registry.attest_clinical_record(actor_id="vet1", record_id="r0", occurred_at=T0)


def test_t_prof_01b_revoked_authority_does_not_erase_the_past(registry):
    """Revocation is forward-looking. Records attested while authority was held
    stay verifiable, and acts after revocation are denied."""
    g = registry.grant(
        actor_id="vet1", tenant_id="t1",
        professional_class=ProfessionalClass.VETERINARIAN,
        granted_by="principal1", grant_reason="employment",
        effective_from=T0,
    )
    registry.revoke(g.grant_id, revoked_at=T1)

    assert registry.held_at("vet1", T0 + timedelta(days=1)) is True, "the past must survive"
    assert registry.held_at("vet1", T1) is False, "revocation instant denies"
    assert registry.held_at("vet1", T2) is False

    with pytest.raises(AuthorityDenied):
        registry.attest_clinical_record(actor_id="vet1", record_id="r2", occurred_at=T2)


def test_t_prof_02_device_sealing_authority_confers_no_professional_authority(registry):
    """T-PROF-02 (ARMED) — the two are separate and must not be conflated.

    Enforced by shape, not by rule: DeviceSealingAuthority carries no actor and
    no professional class, so there is no derivation to write. This test asserts
    the type stays that way — the moment someone adds `actor_id` to it, the
    conflation becomes expressible and this fails.
    """
    seal = DeviceSealingAuthority(device_id="dev-1", seal_key_id="key-1")

    for forbidden in ("actor_id", "professional_class", "grant", "to_grant"):
        assert not hasattr(seal, forbidden), (
            f"DeviceSealingAuthority.{forbidden} makes professional authority "
            "derivable from a device — §28 forbids conflating them"
        )

    # A sealing device is not an actor, so it holds nothing at any time.
    assert registry.held_at("dev-1", T1) is False
    with pytest.raises(AuthorityDenied):
        registry.attest_clinical_record(actor_id="dev-1", record_id="r1", occurred_at=T1)


def test_t_prof_03_sole_practitioner_bootstrap_is_allowed_and_recorded(registry, audit):
    """T-PROF-03 — ALLOWED and RECORDED in the audit trail; never silent.

    Both halves matter. Refusing would make one-vet practices unusable; allowing
    it silently would make a self-grant indistinguishable from one a second
    principal conferred.
    """
    g = registry.bootstrap_sole_practitioner(
        actor_id="vet1", tenant_id="t1",
        professional_class=ProfessionalClass.VETERINARIAN,
        grant_reason="single-veterinarian practice, no second principal",
        effective_from=T0,
    )

    assert g.sole_practitioner_bootstrap is True
    assert g.granted_by is None, "the absence of a second principal is the recorded fact"
    assert registry.held_at("vet1", T1) is True

    events = [e["event_name"] for e in audit]
    assert "professional_authority.sole_practitioner_bootstrap" in events, (
        "the bootstrap was silent — §28 requires it to be recorded"
    )
    ev = next(e for e in audit if e["event_name"].endswith("sole_practitioner_bootstrap"))
    assert ev["sole_practitioner_bootstrap"] is True
    assert ev["grant_reason"]

    # It must be distinguishable from an ordinary grant, not merely present.
    assert "professional_authority.granted" not in events


def test_t_prof_03b_bootstrap_requires_a_recorded_reason(registry):
    """A bootstrap with no reason is a silent exception wearing a flag."""
    with pytest.raises(AuthorityDenied):
        registry.bootstrap_sole_practitioner(
            actor_id="vet1", tenant_id="t1",
            professional_class=ProfessionalClass.VETERINARIAN,
            grant_reason="",
        )


def test_t_prof_04_professional_class_is_never_taken_from_a_caller(registry):
    """T-PROF-04 (ARMED) — professional class is established server-side.

    The registry is the only source of class, and it cannot read a request: it
    has no access to one. This asserts that the answer comes from the grant
    record and that an unknown class cannot be introduced by asking for it.
    """
    registry.grant(
        actor_id="vet1", tenant_id="t1",
        professional_class=ProfessionalClass.VETERINARIAN,
        granted_by="principal1", grant_reason="employment", effective_from=T0,
    )

    # Class comes from the grant, whatever a caller might claim elsewhere.
    assert registry.professional_class_at("vet1", T1) == ProfessionalClass.VETERINARIAN
    # An identity with no grant has no class — never a default.
    assert registry.professional_class_at("stranger", T1) is None

    # A class outside the closed set cannot be granted at all.
    with pytest.raises(AuthorityDenied):
        registry.grant(
            actor_id="vet2", tenant_id="t1",
            professional_class="SURGEON_GENERAL",
            granted_by="principal1", grant_reason="invented",
        )


def test_grant_requires_a_granting_principal(registry):
    """An ordinary grant needs a principal. Omitting one is the sole-practitioner
    case, which has its own recorded path — it must not be reachable by simply
    leaving the field blank."""
    with pytest.raises(AuthorityDenied):
        registry.grant(
            actor_id="vet1", tenant_id="t1",
            professional_class=ProfessionalClass.VETERINARIAN,
            granted_by="", grant_reason="no principal",
        )


def test_grants_are_immutable(registry):
    """Authority history must not be editable in place."""
    g = registry.grant(
        actor_id="vet1", tenant_id="t1",
        professional_class=ProfessionalClass.VETERINARIAN,
        granted_by="p1", grant_reason="employment", effective_from=T0,
    )
    with pytest.raises(Exception):
        g.professional_class = ProfessionalClass.VETERINARY_NURSE  # type: ignore[misc]
