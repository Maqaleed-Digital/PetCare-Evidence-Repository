from petcare.partner_network.repository import PartnerRepository
from petcare.partner_network.service import create_partner, transition_state
from petcare.partner_network.query import get_verified_partners


def test_partner_creation_and_state_transition():
    repo = PartnerRepository()

    create_partner(
        repo,
        partner_id="p1",
        tenant_id="t1",
        partner_type="clinic",
        name="Clinic A",
        capabilities=["emergency"],
    )

    transition_state(repo, "p1", "submitted")
    transition_state(repo, "p1", "under_review")
    transition_state(repo, "p1", "verified")

    verified = get_verified_partners(repo)

    assert len(verified) == 1
    assert verified[0].partner_id == "p1"
    assert verified[0].verification_state == "verified"


def test_invalid_state_rejected():
    repo = PartnerRepository()

    create_partner(
        repo,
        partner_id="p2",
        tenant_id="t1",
        partner_type="clinic",
        name="Clinic B",
        capabilities=[],
    )

    try:
        transition_state(repo, "p2", "invalid_state")
        assert False
    except ValueError:
        assert True
