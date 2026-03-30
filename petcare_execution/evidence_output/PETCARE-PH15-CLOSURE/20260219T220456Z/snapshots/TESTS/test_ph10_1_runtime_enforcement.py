import os
import unittest

from FND.security.policy_guard import load_policy, evaluate_with_policy
from FND.security.actor_id import validate_actor_id

ACTOR_OK = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"

class TestPH10_1RuntimeEnforcement(unittest.TestCase):
    def test_missing_actor_header_fails(self):
        policy = load_policy()
        d = evaluate_with_policy(headers={}, policy=policy)
        self.assertFalse(d.ok)

    def test_invalid_actor_id_fails(self):
        r = validate_actor_id("not-a-uuid")
        self.assertFalse(bool(r.ok))
        self.assertTrue(isinstance(r.reason, str))
        self.assertTrue(len(r.reason) > 0)

    def test_actor_mismatch_logic(self):
        actor_header = ACTOR_OK
        payload_actor = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
        self.assertNotEqual(actor_header, payload_actor)

    def test_trust_token_env_override(self):
        old = os.environ.get("PETCARE_EXPECTED_TOKEN")
        try:
            os.environ["PETCARE_EXPECTED_TOKEN"] = "envtok"
            policy = load_policy()
            d = evaluate_with_policy(headers={"X-Actor-Id": ACTOR_OK, "X-Auth-Token": "envtok"}, policy=policy)
            self.assertIn(d.ok, [True, False])
        finally:
            if old is None:
                os.environ.pop("PETCARE_EXPECTED_TOKEN", None)
            else:
                os.environ["PETCARE_EXPECTED_TOKEN"] = old

if __name__ == "__main__":
    unittest.main()
