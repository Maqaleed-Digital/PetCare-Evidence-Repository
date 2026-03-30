import json
import os
import tempfile
import unittest

from FND.security.policy_guard import load_policy, evaluate_with_policy

ACTOR_OK = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"

class TestPH10TrustEnforcement(unittest.TestCase):
    def test_trust_mode_denies_missing_token(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "policy.json")
            obj = {
                "schema": "PETCARE_SECURITY_POLICY_V1",
                "mode": "TRUST",
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
            d = evaluate_with_policy({"X-Actor-Id": ACTOR_OK}, pol)
            self.assertFalse(d.ok)
            self.assertEqual(d.status_code, 401)

    def test_trust_mode_wrong_token_forbidden(self):
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
            d = evaluate_with_policy({"X-Actor-Id": ACTOR_OK, "X-Auth-Token": "wrong"}, pol)
            self.assertFalse(d.ok)
            self.assertEqual(d.status_code, 403)

    def test_env_expected_token_is_used_when_policy_null(self):
        old = os.environ.get("PETCARE_EXPECTED_TOKEN")
        try:
            os.environ["PETCARE_EXPECTED_TOKEN"] = "envtok"
            with tempfile.TemporaryDirectory() as td:
                p = os.path.join(td, "policy.json")
                obj = {
                    "schema": "PETCARE_SECURITY_POLICY_V1",
                    "mode": "TRUST",
                    "auth": {
                        "require_auth_token": True,
                        "expected_token": None,
                        "actor_header": "X-Actor-Id",
                        "token_header": "X-Auth-Token"
                    },
                    "deny_by_default": True
                }
                with open(p, "w", encoding="utf-8") as f:
                    json.dump(obj, f)

                pol = load_policy(p)
                d = evaluate_with_policy({"X-Actor-Id": ACTOR_OK, "X-Auth-Token": "envtok"}, pol)
                self.assertTrue(d.ok)
        finally:
            if old is None:
                os.environ.pop("PETCARE_EXPECTED_TOKEN", None)
            else:
                os.environ["PETCARE_EXPECTED_TOKEN"] = old

if __name__ == "__main__":
    unittest.main()
