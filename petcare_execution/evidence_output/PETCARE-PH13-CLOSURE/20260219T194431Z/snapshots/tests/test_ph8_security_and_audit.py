import os
import tempfile
import unittest

from FND.security.auth_stub import evaluate_request_auth
from FND.audit.immutable_audit import ImmutableAuditLog

class TestPH8Security(unittest.TestCase):
    def test_missing_actor_id_fails(self):
        d = evaluate_request_auth(headers={}, require_auth_token=False)
        self.assertFalse(d.ok)
        self.assertEqual(d.status_code, 400)

    def test_invalid_actor_id_fails(self):
        d = evaluate_request_auth(headers={"X-Actor-Id": "not-a-uuid"}, require_auth_token=False)
        self.assertFalse(d.ok)
        self.assertEqual(d.status_code, 400)

    def test_valid_actor_id_passes(self):
        d = evaluate_request_auth(
            headers={"X-Actor-Id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"},
            require_auth_token=False,
        )
        self.assertTrue(d.ok)
        self.assertEqual(d.status_code, 200)

    def test_bypass_attempt_wrong_header_fails(self):
        d = evaluate_request_auth(
            headers={"ActorId": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"},
            require_auth_token=False,
        )
        self.assertFalse(d.ok)
        self.assertEqual(d.status_code, 400)

class TestPH8Audit(unittest.TestCase):
    def test_audit_append_and_verify_ok(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "audit.jsonl")
            log = ImmutableAuditLog(p, enable_hash_chain=True)
            r1 = log.append({"action": "x"}, actor_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
            r2 = log.append({"action": "y"}, actor_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
            self.assertTrue(r1.ok)
            self.assertTrue(r2.ok)
            ok, msg = log.verify_chain()
            self.assertTrue(ok, msg)

    def test_audit_tamper_detected(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "audit.jsonl")
            log = ImmutableAuditLog(p, enable_hash_chain=True)
            log.append({"action": "x"}, actor_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
            log.append({"action": "y"}, actor_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")

            with open(p, "rb") as f:
                lines = f.readlines()

            lines[1] = lines[1].replace(b'"y"', b'"tampered"')

            with open(p, "wb") as f:
                f.writelines(lines)

            ok, msg = log.verify_chain()
            self.assertFalse(ok)
            self.assertTrue("mismatch" in msg)

if __name__ == "__main__":
    unittest.main()
