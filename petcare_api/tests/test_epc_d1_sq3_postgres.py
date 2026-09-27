"""MVC-EPC-D-001 D1 — PostgreSQL (migration 0055): a signed medical record is immutable in the DATABASE, a record is
signed exactly once under concurrency, and bank details / API keys are stored only as ciphertext / sha256."""
import hashlib
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
import sq3_ops  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from pets import PetMedicalRecord, PetProfile  # noqa: E402
from repositories import UserIdentity  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

_ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}
NOW = datetime(2031, 3, 1, 9, 0, tzinfo=timezone.utc)
IBAN = "SA0380000000608010167519"


def test_signed_records_are_immutable_and_secrets_are_stored_one_way(clean_postgres):
    p = build_persistence(_ENV, connection_url=clean_postgres)
    p.tenants.create(Tenant(tenant_id="t-d1pg", display_name="t"))
    for uid, role in (("u-v", "veterinarian"), ("u-o", "owner"), ("u-a", "platform_admin")):
        p.identities.create(UserIdentity(user_id=uid, email=f"{uid}@t", password_hash="x", role=role, full_name=uid,
                                         tenant_id="t-d1pg"))
    import inspect
    fields = inspect.signature(PetProfile).parameters
    pet_kwargs = {k: v for k, v in dict(pet_id="p-1", tenant_id="t-d1pg", owner_id="u-o", name="Luna", species="cat",
                                        created_at=NOW, updated_at=NOW, created_by_actor_id="u-o").items() if k in fields}
    p.pets.create(PetProfile(**pet_kwargs))
    p.pets.add_medical_record(PetMedicalRecord(record_id="r-1", pet_id="p-1", tenant_id="t-d1pg", record_type="CLINICAL_RECORD",
                                               title="Exam", recorded_by_actor_id="u-v", recorded_at=NOW, detail="ok"))
    with ThreadPoolExecutor(max_workers=8) as ex:
        outcomes = list(ex.map(lambda _: p.pets.sign_medical_record("r-1", tenant_id="t-d1pg", actor_id="u-v", at=NOW), range(8)))
    assert outcomes.count("SIGNED") == 1 and outcomes.count("ALREADY_SIGNED") == 7
    rec = p.pets.medical_records_for("p-1", tenant_id="t-d1pg")[0]
    assert rec.signed_by_actor_id == "u-v" and len(rec.content_sha256) == 64
    with psycopg.connect(clean_postgres, autocommit=True) as conn:
        with pytest.raises(psycopg.errors.RestrictViolation):
            conn.execute("UPDATE pet_medical_record SET title = 'tampered' WHERE record_id = 'r-1'")
        with pytest.raises(psycopg.errors.RestrictViolation):
            conn.execute("DELETE FROM pet_medical_record WHERE record_id = 'r-1'")
    assert p.pets.sign_medical_record("r-missing", tenant_id="t-d1pg", actor_id="u-v", at=NOW) == "NOT_FOUND"

    p.sq3_ops.set_payout(sq3_ops.PayoutDetails("t-d1pg", "BANK_TRANSFER", "MONTHLY", 5000, "u-a", NOW))
    assert p.sq3_ops.payout(tenant_id="t-d1pg").payout_schedule == "MONTHLY"
    p.sq3_ops.set_bank(sq3_ops.BankDetails("t-d1pg", "Bank", "Clinic", os.urandom(12), os.urandom(40), IBAN[-4:], "u-a", NOW))
    key, key_id, prefix, digest = sq3_ops.new_api_key()
    p.sq3_ops.add_api_key(sq3_ops.ApiKey(key_id, "t-d1pg", "k", prefix, digest, "u-a", NOW))
    with psycopg.connect(clean_postgres) as conn:
        bank = conn.execute("SELECT iban_ciphertext, iban_last4 FROM tenant_bank_details").fetchone()
        keys = conn.execute("SELECT key_sha256, prefix FROM api_key").fetchall()
    assert IBAN.encode() not in bytes(bank[0]) and bank[1] == "7519"
    assert keys == [(hashlib.sha256(key.encode()).hexdigest(), key[:12])] and key not in str(keys)
    assert p.sq3_ops.revoke_api_key(key_id, tenant_id="t-d1pg", at=NOW) is True
    assert p.sq3_ops.revoke_api_key(key_id, tenant_id="t-d1pg", at=NOW) is False
    p.pool.close()
