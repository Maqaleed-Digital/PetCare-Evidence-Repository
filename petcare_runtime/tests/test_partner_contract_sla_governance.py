from petcare.partner_network.contracts_repository import PartnerContractsRepository
from petcare.partner_network.contracts_service import (
    create_contract,
    define_sla,
    record_breach_signal,
    transition_contract_state,
)
from petcare.partner_network.contracts_query import (
    get_active_contracts,
    get_contract_breach_signals,
    get_contract_slas,
)


def test_contract_state_and_active_query():
    repo = PartnerContractsRepository()

    create_contract(
        repo=repo,
        contract_id="c1",
        partner_id="p1",
        tenant_id="t1",
        effective_from="2026-03-30T00:00:00Z",
        effective_to=None,
        service_scope=["emergency", "referral"],
    )

    transition_contract_state(repo, "c1", "active")

    active_contracts = get_active_contracts(repo)

    assert len(active_contracts) == 1
    assert active_contracts[0].contract_id == "c1"
    assert active_contracts[0].contract_state == "active"


def test_define_sla_and_query_by_contract():
    repo = PartnerContractsRepository()

    create_contract(
        repo=repo,
        contract_id="c2",
        partner_id="p2",
        tenant_id="t1",
        effective_from="2026-03-30T00:00:00Z",
        effective_to=None,
        service_scope=["pharmacy"],
    )

    define_sla(
        repo=repo,
        sla_id="sla1",
        contract_id="c2",
        metric_type="response_time",
        target_value=15,
        threshold_operator="lte",
        monitoring_enabled=True,
    )

    slas = get_contract_slas(repo, "c2")

    assert len(slas) == 1
    assert slas[0].sla_id == "sla1"
    assert slas[0].metric_type == "response_time"
    assert slas[0].target_value == 15


def test_record_breach_signal_and_query():
    repo = PartnerContractsRepository()

    create_contract(
        repo=repo,
        contract_id="c3",
        partner_id="p3",
        tenant_id="t1",
        effective_from="2026-03-30T00:00:00Z",
        effective_to=None,
        service_scope=["diagnostics"],
    )

    define_sla(
        repo=repo,
        sla_id="sla2",
        contract_id="c3",
        metric_type="availability",
        target_value=99,
        threshold_operator="gte",
        monitoring_enabled=True,
    )

    record_breach_signal(
        repo=repo,
        signal_id="sig1",
        contract_id="c3",
        sla_id="sla2",
        signal_state="warning",
        observed_value=95,
        notes="temporary degradation only; no enforcement action executed",
    )

    signals = get_contract_breach_signals(repo, "c3")

    assert len(signals) == 1
    assert signals[0].signal_id == "sig1"
    assert signals[0].signal_state == "warning"
    assert signals[0].target_value == 99


def test_invalid_contract_state_rejected():
    repo = PartnerContractsRepository()

    create_contract(
        repo=repo,
        contract_id="c4",
        partner_id="p4",
        tenant_id="t1",
        effective_from="2026-03-30T00:00:00Z",
        effective_to=None,
        service_scope=["logistics"],
    )

    try:
        transition_contract_state(repo, "c4", "invalid_state")
        assert False
    except ValueError:
        assert True


def test_invalid_sla_operator_rejected():
    repo = PartnerContractsRepository()

    create_contract(
        repo=repo,
        contract_id="c5",
        partner_id="p5",
        tenant_id="t1",
        effective_from="2026-03-30T00:00:00Z",
        effective_to=None,
        service_scope=["marketplace_service"],
    )

    try:
        define_sla(
            repo=repo,
            sla_id="sla3",
            contract_id="c5",
            metric_type="fulfillment_time",
            target_value=60,
            threshold_operator="eq",
            monitoring_enabled=True,
        )
        assert False
    except ValueError:
        assert True
