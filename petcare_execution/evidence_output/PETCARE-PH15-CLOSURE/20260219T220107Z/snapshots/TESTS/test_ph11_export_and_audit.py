import unittest

from FND.security.policy_guard import Policy, enforce_evidence_export
from FND.security.audit_chain import compute_event_hash, verify_hash_chain

class TestPH11EvidenceExport(unittest.TestCase):
    def test_pii_requires_watermark_and_encryption(self):
        p = Policy(
            schema="S",
            mode="TRUST",
            require_auth_token=True,
            expected_token="x",
            actor_header="X-Actor-Id",
            token_header="X-Auth-Token",
            deny_by_default=True,
            pii_requires_watermark=True,
            pii_requires_encryption=True,
        )

        ok, reason, code = enforce_evidence_export(p, include_pii=True, watermark=False, encryption=True)
        self.assertFalse(ok)
        self.assertEqual(code, 400)
        self.assertEqual(reason, "pii_requires_watermark")

        ok, reason, code = enforce_evidence_export(p, include_pii=True, watermark=True, encryption=False)
        self.assertFalse(ok)
        self.assertEqual(code, 400)
        self.assertEqual(reason, "pii_requires_encryption")

        ok, reason, code = enforce_evidence_export(p, include_pii=True, watermark=True, encryption=True)
        self.assertTrue(ok)
        self.assertEqual(code, 200)

    def test_non_pii_always_ok(self):
        p = Policy(
            schema="S",
            mode="TRUST",
            require_auth_token=True,
            expected_token="x",
            actor_header="X-Actor-Id",
            token_header="X-Auth-Token",
            deny_by_default=True,
            pii_requires_watermark=True,
            pii_requires_encryption=True,
        )
        ok, _, code = enforce_evidence_export(p, include_pii=False, watermark=False, encryption=False)
        self.assertTrue(ok)
        self.assertEqual(code, 200)

class TestPH11AuditChain(unittest.TestCase):
    def test_chain_ok_then_tamper_detected(self):
        genesis = "GENESIS"
        core1 = {"action": "put", "k": "k1", "v": "v1"}
        h1 = compute_event_hash(genesis, core1)
        ev1 = {"prev_hash": genesis, "hash": h1, **core1}

        core2 = {"action": "put", "k": "k1", "v": "v2"}
        h2 = compute_event_hash(h1, core2)
        ev2 = {"prev_hash": h1, "hash": h2, **core2}

        r_ok = verify_hash_chain([ev1, ev2], genesis=genesis)
        self.assertTrue(r_ok.ok)

        tampered = dict(ev2)
        tampered["v"] = "EVIL"
        r_bad = verify_hash_chain([ev1, tampered], genesis=genesis)
        self.assertFalse(r_bad.ok)
        self.assertIn(r_bad.reason, ["hash_mismatch", "prev_hash_mismatch"])

if __name__ == "__main__":
    unittest.main()
