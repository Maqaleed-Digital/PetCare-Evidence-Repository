"""FR-07 (U7) — messages, attachments metadata and delivery records are durable. Second-instance
read-back against REAL PostgreSQL through the repository the serving path uses."""
import os
import sys
from datetime import datetime, timezone
from uuid import uuid4

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
from messages import ConsultationMessage, DeliveryRecord, MessageAttachment  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from repositories import RepositoryDenied  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

T_A, T_B = "t-msg-pg", "t-msg-pg-b"
_ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}


def _p(url):
    return build_persistence(_ENV, connection_url=url)


@pytest.fixture()
def pg(clean_postgres):
    p = _p(clean_postgres)
    for t in (T_A, T_B):
        p.tenants.create(Tenant(tenant_id=t, display_name=t))
    yield clean_postgres
    p.pool.close()


def test_message_attachment_and_delivery_survive_a_second_instance(pg):
    w = _p(pg)
    now = datetime.now(timezone.utc)
    m = w.messages.add_message(ConsultationMessage(message_id=str(uuid4()), tenant_id=T_A, consultation_id="c1",
                                                   sender_id="u-o", sender_role="owner", body="hi", created_at=now))
    w.messages.add_attachment(MessageAttachment(attachment_id=str(uuid4()), message_id=m.message_id, tenant_id=T_A,
                                                filename="cbc.png", content_type="image/png", byte_size=72,
                                                sha256="a" * 64, storage_key="k", created_at=now))
    w.messages.record_delivery(DeliveryRecord(record_id=str(uuid4()), tenant_id=T_A, message_id=m.message_id,
                                              recipient_id="u-v", channel="IN_APP", attempt_no=1,
                                              status="DELIVERED", rendered_body="New message: hi", occurred_at=now))
    r = _p(pg)
    assert [x.body for x in r.messages.messages_for("c1", tenant_id=T_A)] == ["hi"]
    assert r.messages.messages_for("c1", tenant_id=T_B) == []
    assert [a.filename for a in r.messages.attachments_for(m.message_id, tenant_id=T_A)] == ["cbc.png"]
    recs = r.messages.deliveries_for(m.message_id, tenant_id=T_A)
    assert [(x.recipient_id, x.rendered_body) for x in recs] == [("u-v", "New message: hi")]
    for p in (w, r):
        p.pool.close()


def test_empty_message_and_orphan_attachment_are_refused(pg):
    w = _p(pg)
    now = datetime.now(timezone.utc)
    with pytest.raises(RepositoryDenied):
        w.messages.add_message(ConsultationMessage(message_id=str(uuid4()), tenant_id=T_A, consultation_id="c",
                                                   sender_id="u", sender_role="owner", body="  ", created_at=now))
    with pytest.raises(RepositoryDenied):
        w.messages.add_attachment(MessageAttachment(attachment_id=str(uuid4()), message_id="nope", tenant_id=T_A,
                                                    filename="x", content_type="image/png", byte_size=1,
                                                    sha256="a" * 64, storage_key="k", created_at=now))
    w.pool.close()
