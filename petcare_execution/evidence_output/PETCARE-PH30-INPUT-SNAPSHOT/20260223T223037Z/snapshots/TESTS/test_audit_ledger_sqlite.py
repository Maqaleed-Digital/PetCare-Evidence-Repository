"""
PH26 SQLite Audit Ledger Tests (pytest)

Covers:
- Append-only behavior (via API behavior)
- Tenant isolation (per-tenant DB files)
- Sequence monotonicity (per-tenant)
- Hash-chain integrity verification
- Export determinism
- Optional compatibility with audit_export_adapter (skips if module not present)
"""

import os
import shutil
import sys
import tempfile
import asyncio

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from FND.CODE_SCAFFOLD.storage.audit_ledger_sqlite import (
    SqliteAuditLedger,
    TenantRequiredError,
    get_sqlite_audit_ledger,
    reset_sqlite_audit_ledger,
)
from FND.CODE_SCAFFOLD.interfaces.audit_interface import AuditEvent, AuditQuery, AuditExport


@pytest.fixture()
def temp_dir():
    d = tempfile.mkdtemp(prefix="audit_test_")
    try:
        yield d
    finally:
        if os.path.exists(d):
            shutil.rmtree(d)


@pytest.fixture()
def ledger(temp_dir):
    l = SqliteAuditLedger(data_dir=temp_dir)
    try:
        yield l
    finally:
        l.close()


def run(coro):
    return asyncio.run(coro)


def test_append_creates_event(ledger):
    tenant_id = "tenant-001"
    event = run(
        ledger.append(
            tenant_id=tenant_id,
            event_name="data.created",
            category="data",
            severity="INFO",
            actor_id="user-001",
            actor_type="user",
            action="create",
            payload={"entity": "pet", "name": "Fluffy"},
        )
    )
    assert isinstance(event, AuditEvent)
    assert event.tenant_id == tenant_id
    assert event.event_name == "data.created"
    assert event.sequence == 1

    retrieved = run(ledger.get_by_id(tenant_id, event.event_id))
    assert retrieved is not None
    assert retrieved.event_id == event.event_id


def test_append_increments_sequence(ledger):
    tenant_id = "tenant-seq"
    events = []
    for i in range(5):
        events.append(
            run(
                ledger.append(
                    tenant_id=tenant_id,
                    event_name=f"event.{i}",
                    category="data",
                    severity="INFO",
                    actor_id="user",
                    actor_type="user",
                    action="create",
                    payload={"index": i},
                )
            )
        )
    assert [e.sequence for e in events] == [1, 2, 3, 4, 5]


def test_append_creates_hash_chain(ledger):
    tenant_id = "tenant-chain"
    event1 = run(
        ledger.append(
            tenant_id=tenant_id,
            event_name="event.one",
            category="data",
            severity="INFO",
            actor_id="user",
            actor_type="user",
            action="create",
            payload={},
        )
    )
    event2 = run(
        ledger.append(
            tenant_id=tenant_id,
            event_name="event.two",
            category="data",
            severity="INFO",
            actor_id="user",
            actor_type="user",
            action="create",
            payload={},
        )
    )
    assert event1.prev_checksum is None
    assert event2.prev_checksum == event1.checksum


def test_append_requires_tenant_id(ledger):
    with pytest.raises(TenantRequiredError):
        run(
            ledger.append(
                tenant_id="",
                event_name="test",
                category="data",
                severity="INFO",
                actor_id="user",
                actor_type="user",
                action="test",
                payload={},
            )
        )


def test_persists_across_instances(temp_dir):
    tenant_id = "tenant-persist"
    ledger1 = SqliteAuditLedger(data_dir=temp_dir)

    event = run(
        ledger1.append(
            tenant_id=tenant_id,
            event_name="persistent.event",
            category="data",
            severity="INFO",
            actor_id="user",
            actor_type="user",
            action="create",
            payload={"key": "value"},
        )
    )
    ledger1.close()

    ledger2 = SqliteAuditLedger(data_dir=temp_dir)
    try:
        retrieved = run(ledger2.get_by_id(tenant_id, event.event_id))
        assert retrieved is not None
        assert retrieved.payload["key"] == "value"
    finally:
        ledger2.close()


def test_tenants_have_separate_databases(ledger):
    tenant_a = "tenant-alpha"
    tenant_b = "tenant-beta"

    run(
        ledger.append(
            tenant_id=tenant_a,
            event_name="event.a",
            category="data",
            severity="INFO",
            actor_id="user",
            actor_type="user",
            action="create",
            payload={},
        )
    )
    run(
        ledger.append(
            tenant_id=tenant_b,
            event_name="event.b",
            category="data",
            severity="INFO",
            actor_id="user",
            actor_type="user",
            action="create",
            payload={},
        )
    )

    db_a = ledger._get_db_path(tenant_a)
    db_b = ledger._get_db_path(tenant_b)
    assert os.path.exists(db_a)
    assert os.path.exists(db_b)
    assert os.path.basename(db_a) != os.path.basename(db_b)


def test_tenant_data_is_isolated(ledger):
    tenant_a = "tenant-iso-a"
    tenant_b = "tenant-iso-b"

    event_a = run(
        ledger.append(
            tenant_id=tenant_a,
            event_name="secret.event",
            category="data",
            severity="INFO",
            actor_id="user",
            actor_type="user",
            action="create",
            payload={"secret": "alpha"},
        )
    )

    retrieved = run(ledger.get_by_id(tenant_b, event_a.event_id))
    assert retrieved is None


def test_sequences_are_per_tenant(ledger):
    tenant_a = "tenant-seq-a"
    tenant_b = "tenant-seq-b"

    event_a = run(
        ledger.append(
            tenant_id=tenant_a,
            event_name="event",
            category="data",
            severity="INFO",
            actor_id="user",
            actor_type="user",
            action="create",
            payload={},
        )
    )
    event_b = run(
        ledger.append(
            tenant_id=tenant_b,
            event_name="event",
            category="data",
            severity="INFO",
            actor_id="user",
            actor_type="user",
            action="create",
            payload={},
        )
    )
    assert event_a.sequence == 1
    assert event_b.sequence == 1


def test_query_returns_only_tenant_events(ledger):
    tenant_a = "tenant-query-a"
    tenant_b = "tenant-query-b"

    run(
        ledger.append(
            tenant_id=tenant_a,
            event_name="event.a",
            category="data",
            severity="INFO",
            actor_id="user",
            actor_type="user",
            action="create",
            payload={"marker": "A"},
        )
    )
    run(
        ledger.append(
            tenant_id=tenant_b,
            event_name="event.b",
            category="data",
            severity="INFO",
            actor_id="user",
            actor_type="user",
            action="create",
            payload={"marker": "B"},
        )
    )

    events = run(ledger.query(AuditQuery(tenant_id=tenant_a)))
    assert len(events) == 1
    assert events[0].payload["marker"] == "A"


def test_export_creates_bundle(ledger):
    tenant_id = "tenant-export"
    run(
        ledger.append(
            tenant_id=tenant_id,
            event_name="test.event",
            category="data",
            severity="INFO",
            actor_id="user",
            actor_type="user",
            action="create",
            payload={"key": "value"},
        )
    )

    export = run(ledger.export(tenant_id))
    assert isinstance(export, AuditExport)
    assert export.tenant_id == tenant_id
    assert export.event_count == 1
    assert isinstance(export.checksum, str)
    assert len(export.checksum) > 0


def test_export_deterministic_checksum(ledger):
    tenant_id = "tenant-det-export"
    run(
        ledger.append(
            tenant_id=tenant_id,
            event_name="event",
            category="data",
            severity="INFO",
            actor_id="user",
            actor_type="user",
            action="create",
            payload={"data": "test"},
        )
    )
    export1 = run(ledger.export(tenant_id))
    export2 = run(ledger.export(tenant_id))
    assert export1.checksum == export2.checksum


def test_count_all(ledger):
    tenant_id = "tenant-count"
    for i in range(5):
        run(
            ledger.append(
                tenant_id=tenant_id,
                event_name=f"event.{i}",
                category="data",
                severity="INFO",
                actor_id="user",
                actor_type="user",
                action="create",
                payload={},
            )
        )
    assert run(ledger.count(tenant_id)) == 5


def test_factory_singleton(temp_dir):
    reset_sqlite_audit_ledger()
    l1 = get_sqlite_audit_ledger(temp_dir)
    l2 = get_sqlite_audit_ledger(temp_dir)
    assert l1 is l2


def test_export_adapter_compatibility_optional(ledger):
    adapter = pytest.importorskip("FND.CODE_SCAFFOLD.storage.audit_export_adapter")

    export_audit_ledger_bundle = getattr(adapter, "export_audit_ledger_bundle", None)
    verify_bundle_checksum = getattr(adapter, "verify_bundle_checksum", None)

    if export_audit_ledger_bundle is None or verify_bundle_checksum is None:
        pytest.skip("audit_export_adapter missing expected functions")

    tenant_id = "tenant-adapter-compat"
    run(
        ledger.append(
            tenant_id=tenant_id,
            event_name="test.event",
            category="data",
            severity="INFO",
            actor_id="user",
            actor_type="user",
            action="create",
            payload={"test": "data"},
        )
    )

    bundle = run(export_audit_ledger_bundle(ledger, tenant_id))
    assert bundle["tenant_id"] == tenant_id
    assert bundle["event_count"] == 1
    assert verify_bundle_checksum(bundle) is True
