import json
import os
import unittest

class TestPH12PolicyDigestArtifact(unittest.TestCase):
    def test_policy_digest_exists_and_has_sha(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        p = os.path.join(root, "ops", "ph12_policy_digest.json")
        self.assertTrue(os.path.exists(p), f"missing {p}")
        with open(p, "r", encoding="utf-8") as f:
            obj = json.load(f)
        self.assertIn("policy_sha256_canonical", obj)
        self.assertTrue(isinstance(obj["policy_sha256_canonical"], str))
        self.assertEqual(len(obj["policy_sha256_canonical"]), 64)

if __name__ == "__main__":
    unittest.main()
