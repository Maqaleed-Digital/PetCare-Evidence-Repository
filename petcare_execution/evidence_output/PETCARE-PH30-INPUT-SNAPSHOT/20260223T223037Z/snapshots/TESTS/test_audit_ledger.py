import pytest

from FND.CODE_SCAFFOLD.storage.audit_ledger import MemoryAuditLedger, TenantRequiredError
from FND.CODE_SCAFFOLD.interfaces.audit_interface import AuditQuery


def test_append_creates_event_and_sequence():
    ledger = MemoryAuditLedger()
    ev = ledger.append(
        tenant_id="tenant-1",
        event_name="data.created",
        category="data",
        severity="INFO",
        actor_id="user-1",
        actor_type="user",
        action="create",
        payload={"k": "v"},
    )
    assert ev.tenant_id == "tenant-1"
    assert ev.sequence == 1
    assert len(ev.event_id) == 32
    assert ev.prev_checksum is None
    assert isinstance(ev.checksum, str) and len(ev.checksum) == 64


def test_append_builds_hash_chain():
    ledger = MemoryAuditLedger()
    ev1 = ledger.append(
        tenant_id="tenant-1",
        event_name="e1",
        category="data",
        severity="INFO",
        actor_id="user-1",
        actor_type="user",
        action="create",
        payload={},
    )
    ev2 = ledger.append(
        tenant_id="tenant-1",
        event_name="e2",
        category="data",
        severity="INFO",
        actor_id="user-1",
        actor_type="user",
        action="create",
        payload={},
    )
    assert ev1.sequence == 1
    assert ev2.sequence == 2
    assert ev2.prev_checksum == ev1.checksum
    assert ledger.verify_chain("tenant-1") is True


def test_tenant_isolation_sequence_resets_per_tenant():
    ledger = MemoryAuditLedger()
    a1 = ledger.append(
        tenant_id="A",
        event_name="x",
        category="data",
        severity="INFO",
        actor_id="u",
        actor_type="user",
        action="create",
        payload={},
    )
    b1 = ledger.append(
        tenant_id="B",
        event_name="x",
        category="data",
        severity="INFO",
        actor_id="u",
        actor_type="user",
        action="create",
        payload={},
    )
    assert a1.sequence == 1
    assert b1.sequence == 1


def test_query_filters_and_pagination():
    ledger = MemoryAuditLedger()
    for i in range(10):
        ledger.append(
            tenant_id="T",
            event_name=f"event.{i}",
            category="data" if i % 2 == 0 else "auth",
            severity="INFO",
            actor_id="u",
            actor_type="user",
            action="create",
            payload={"i": i},
        )

    q_auth = AuditQuery(tenant_id="T", category="auth", limit=100, offset=0)
    auth_events = ledger.query(q_auth)
    assert all(e.category == "auth" for e in auth_events)

    q_page1 = AuditQuery(tenant_id="T", limit=3, offset=0)
    q_page2 = AuditQuery(tenant_id="T", limit=3, offset=3)
    page1 = ledger.query(q_page1)
    page2 = ledger.query(q_page2)
    assert len(page1) == 3
    assert len(page2) == 3
    assert page1[0].event_id != page2[0].event_id


def test_export_bundle_checksum_stable_for_same_events():
    ledger = MemoryAuditLedger()
    ledger.append(
        tenant_id="T",
        event_name="event",
        category="data",
        severity="INFO",
        actor_id="u",
        actor_type="user",
        action="create",
        payload={"a": 1},
    )
    e1 = ledger.export("T")
    e2 = ledger.export("T")
    assert e1.event_count == 1
    assert e2.event_count == 1
    assert e1.first_sequence == 1 and e1.last_sequence == 1
    assert e1.checksum == e2.checksum


def test_requires_tenant_id():
    ledger = MemoryAuditLedger()
    with pytest.raises(TenantRequiredError):
        ledger.append(
            tenant_id="",
            event_name="x",
            category="data",
            severity="INFO",
            actor_id="u",
            actor_type="user",
            action="create",
            payload={},
        )
