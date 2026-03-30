import json
import os
import tempfile
import unittest

from FND.security.policy_guard import load_policy, evaluate_with_policy

class TestPH9PolicyGuard(unittest.TestCase):
    def test_policy_load_and_eval_regulated(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "policy.json")
            obj = {
                "schema": "PETCARE_SECURITY_POLICY_V1",
                "mode": "REGULATED",
                "auth": {
                    "require_auth_token": False,
                    "expected_token": None,
                    "actor_header": "X-Actor-Id",
                    "token_header": "X-Auth-Token"
                },
                "deny_by_default": False
            }
            with open(p, "w", encoding="utf-8") as f:
                json.dump(obj, f)

            pol = load_policy(p)
            d = evaluate_with_policy({"X-Actor-Id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"}, pol)
            self.assertTrue(d.ok)

    def test_deny_by_default_requires_token(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "policy.json")
            obj = {
                "schema": "PETCARE_SECURITY_POLICY_V1",
                "mode": "TRUST",
                "auth": {
                    "require_auth_token": True,
                    "expected_token": "secret",
                    "actor_header": "X-Actor-Id",
                    "token_header": "X-Auth-Token"
                },
                "deny_by_default": True
            }
            with open(p, "w", encoding="utf-8") as f:
                json.dump(obj, f)

            pol = load_policy(p)
            d1 = evaluate_with_policy({"X-Actor-Id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"}, pol)
            self.assertFalse(d1.ok)
            self.assertEqual(d1.status_code, 401)

            d2 = evaluate_with_policy(
                {"X-Actor-Id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", "X-Auth-Token": "wrong"},
                pol
            )
            self.assertFalse(d2.ok)
            self.assertEqual(d2.status_code, 403)

            d3 = evaluate_with_policy(
                {"X-Actor-Id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", "X-Auth-Token": "secret"},
                pol
            )
            self.assertTrue(d3.ok)

if __name__ == "__main__":
    unittest.main()
