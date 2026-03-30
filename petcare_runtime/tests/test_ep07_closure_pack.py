from scripts.petcare_ep07_closure_verify import verify_ep07_closure


def test_ep07_closure_pack() -> None:
    result = verify_ep07_closure()

    assert result["pack_id"] == "PETCARE-PHASE-1-BUILD-EP07-CLOSURE"
    assert result["status"] == "CLOSED"
    assert result["governance_seal"] == "ACTIVE"
    assert result["wave_count"] == 9
    assert result["inventory_count"] >= 63
