"""FR-23 AC-FR-23-01 (U15) — due items, completions and reminders are durable in PostgreSQL, and the database
makes a repeated send of the same (item, kind) a no-op (UNIQUE)."""
import os
import sys
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from pets import PetProfile  # noqa: E402
from reminders import CareCompletion, CareDue, Reminder  # noqa: E402
from repositories import UserIdentity  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

T = "t-fr23-pg"
_ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}


@pytest.fixture()
def pg(clean_postgres):
    p = build_persistence(_ENV, connection_url=clean_postgres)
    p.tenants.create(Tenant(tenant_id=T, display_name=T))
    p.identities.create(UserIdentity(user_id="u-own", email="o@t", password_hash="x", role="owner", full_name="o", tenant_id=T))
    yield clean_postgres, p
    p.pool.close()


def test_due_items_completions_and_reminders_survive_and_a_send_happens_once(pg):
    url, p = pg
    now = datetime.now(timezone.utc)
    pet_id = p.pets.create(PetProfile(pet_id=str(uuid4()), tenant_id=T, owner_id="u-own", name="Luna", species="cat",
                                      created_by_actor_id="u-own", created_at=now, updated_at=now)).pet_id
    d = p.reminders.add_due(CareDue(due_id=str(uuid4()), tenant_id=T, pet_id=pet_id, kind="VACCINATION", title="Rabies",
                                    due_at=now + timedelta(days=5), recorded_by="u-vet", created_at=now))
    r = Reminder(reminder_id=str(uuid4()), due_id=d.due_id, tenant_id=T, owner_id="u-own", kind="REMIND_7D",
                 language="ar", rendered="تذكير", channel="IN_APP", sent_at=now)
    assert p.reminders.record(r) is True
    assert p.reminders.record(Reminder(**{**r.__dict__, "reminder_id": str(uuid4())})) is False  # UNIQUE (due, kind)
    p.reminders.complete(CareCompletion(due_id=d.due_id, tenant_id=T, completed_by="u-vet", completed_at=now))
    q = build_persistence(_ENV, connection_url=url)
    assert [x.title for x in q.reminders.dues(tenant_id=T)] == ["Rabies"]
    assert q.reminders.completed(d.due_id, tenant_id=T) is True
    assert q.reminders.sent_kinds(d.due_id, tenant_id=T) == {"REMIND_7D"}
    assert [x.rendered for x in q.reminders.for_owner("u-own", tenant_id=T)] == ["تذكير"]
    assert q.reminders.dues(tenant_id="t-other") == []
    q.pool.close()
