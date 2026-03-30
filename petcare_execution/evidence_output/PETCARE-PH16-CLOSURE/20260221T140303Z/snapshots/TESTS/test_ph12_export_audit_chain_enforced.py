import unittest

from FND.CODE_SCAFFOLD.storage.export_bundle import build_export_bundle

TENANT = "33333333-3333-3333-3333-333333333333"

class TestPH12ExportAuditChainEnforced(unittest.TestCase):
    def test_invalid_chain_rejected(self):
        items = [{"k": "a", "v": 1}]
        bad_audit = [
            {"op": "put", "hash": "aaa", "prev_hash": "bbb"},
            {"op": "put", "hash": "ccc", "prev_hash": "ddd"}
        ]
        with self.assertRaises(ValueError) as ctx:
            build_export_bundle(tenant_id=TENANT, items=items, audit=bad_audit, enforce_audit_chain=True)
        self.assertIn("invalid_audit_hash_chain", str(ctx.exception))

    def test_none_audit_allowed(self):
        items = [{"k": "a", "v": 1}]
        b = build_export_bundle(tenant_id=TENANT, items=items, audit=None, enforce_audit_chain=True)
        self.assertEqual(b["tenant_id"], TENANT)
        self.assertIn("items", b)
        self.assertIn("audit", b)

if __name__ == "__main__":
    unittest.main()
