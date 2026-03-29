from petcare.pharmacy.contracts import success_envelope, error_envelope
from petcare.pharmacy.registry import READ_ONLY_ENDPOINT_REGISTRY


def test_success_envelope_contract():
    result = success_envelope(
        surface="test_surface",
        actor_user_id="user_1",
        payload={"x": 1},
    )
    assert result["status"] == "success"
    assert result["contract_version"] == "v1"
    assert result["payload"]["x"] == 1


def test_error_envelope_contract():
    result = error_envelope(
        surface="test_surface",
        actor_user_id="user_1",
        error_code="ERR_001",
        message="failure",
    )
    assert result["status"] == "error"
    assert result["error"]["code"] == "ERR_001"


def test_registry_locked():
    assert len(READ_ONLY_ENDPOINT_REGISTRY) == 11
