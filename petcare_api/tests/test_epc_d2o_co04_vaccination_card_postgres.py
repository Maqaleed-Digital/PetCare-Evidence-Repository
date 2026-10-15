"""MVC-EPC-D-001 D2o — PostgreSQL: the CO-04 vaccination card is built from durable FR-23 records. After a second instance reads
the due items and their completions back, `reminders.vaccination_card` reports the given vaccination at the STORED completion
date (Asia/Riyadh) with the recording veterinarian, keeps the outstanding one due, and omits the treatment."""
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
import reminders as rmd  # noqa: E402
from pets import PetProfile  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from repositories import UserIdentity  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

T = "t-d2o-pg"
ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}


def test_the_card_is_built_from_the_stored_dues_and_completions(clean_postgres):
    p = build_persistence(ENV, connection_url=clean_postgres)
    p.tenants.create(Tenant(tenant_id=T, display_name=T))
    p.identities.create(UserIdentity(user_id="u-own", email="o@t", password_hash="x", role="owner", full_name="o", tenant_id=T))
    t0 = datetime(2031, 3, 1, 6, 0, tzinfo=timezone.utc)
    p.pets.create(PetProfile(pet_id="pet-1", tenant_id=T, owner_id="u-own", name="Luna", species="cat",
                             created_by_actor_id="u-own", created_at=t0, updated_at=t0))
    mk = lambda i, kind, title, at: rmd.CareDue(due_id=i, tenant_id=T, pet_id="pet-1", kind=kind, title=title, due_at=at,
                                                recorded_by="u-vet", created_at=t0)
    p.reminders.add_due(mk("d-rab", rmd.VACCINATION, "Rabies", t0))
    p.reminders.add_due(mk("d-flv", rmd.VACCINATION, "FeLV booster", t0 + timedelta(days=40)))
    p.reminders.add_due(mk("d-wrm", rmd.TREATMENT, "Deworming", t0))
    done_at = datetime(2031, 3, 2, 22, 15, tzinfo=timezone.utc)                        # 2031-03-03 in Riyadh
    p.reminders.complete(rmd.CareCompletion(due_id="d-rab", tenant_id=T, completed_by="u-vet", completed_at=done_at))
    p.reminders.complete(rmd.CareCompletion(due_id="d-wrm", tenant_id=T, completed_by="u-vet", completed_at=done_at))

    q = build_persistence(ENV, connection_url=clean_postgres)
    c = q.reminders.completion("d-rab", tenant_id=T)
    assert (c.completed_by, c.completed_at) == ("u-vet", done_at)
    assert q.reminders.completion("d-flv", tenant_id=T) is None
    assert q.reminders.completion("d-rab", tenant_id="t-other") is None                 # tenant-scoped
    card = rmd.vaccination_card(q.reminders.dues(tenant_id=T), lambda i: q.reminders.completion(i, tenant_id=T),
                                {"u-vet": "Dr Salma"}.get)
    assert card["given"] == [{"due_id": "d-rab", "title": "Rabies", "given_on": "2031-03-03", "given_by": "Dr Salma"}]
    assert card["due"] == [{"due_id": "d-flv", "title": "FeLV booster", "due_on": "2031-04-10"}]
    p.pool.close(); q.pool.close()
