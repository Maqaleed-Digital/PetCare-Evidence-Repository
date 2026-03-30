import unittest

from FND.CODE_SCAFFOLD.tenant_isolation_guard import (
    TENANT_HEADER,
    normalize_tenant_id,
    require_tenant_context,
    TenantContext,
    MissingTenantHeader,
    InvalidTenantHeader,
)
from FND.CODE_SCAFFOLD.storage.memory_store import MemoryStore
from FND.CODE_SCAFFOLD.storage.export_bundle import build_export_bundle


T1 = "11111111-1111-1111-1111-111111111111"
T2 = "22222222-2222-2222-2222-222222222222"


class TestTenantHeaderValidation(unittest.TestCase):
    def test_header_constant(self):
        self.assertEqual(TENANT_HEADER, "x-tenant-id")

    def test_missing(self):
        with self.assertRaises(MissingTenantHeader):
            normalize_tenant_id(None)

    def test_empty(self):
        with self.assertRaises(MissingTenantHeader):
            normalize_tenant_id("  ")

    def test_invalid_uuid(self):
        with self.assertRaises(InvalidTenantHeader):
            normalize_tenant_id("not-a-uuid")

    def test_normalizes_lower(self):
        self.assertEqual(normalize_tenant_id(T1.upper()), T1)

    def test_require_context_ok(self):
        ctx = require_tenant_context(T1.upper())
        self.assertIsInstance(ctx, TenantContext)
        self.assertEqual(ctx.tenant_id, T1)

    def test_require_context_missing(self):
        with self.assertRaises(MissingTenantHeader):
            require_tenant_context(None)


class TestStorageIsolation(unittest.TestCase):
    def setUp(self):
        self.s = MemoryStore()

    def test_put_requires_tenant(self):
        with self.assertRaises(MissingTenantHeader):
            self.s.put("", "k", "v", "a")

    def test_put_requires_uuid_tenant(self):
        with self.assertRaises(InvalidTenantHeader):
            self.s.put("not-a-uuid", "k", "v", "a")

    def test_put_normalizes_tenant_lower(self):
        self.s.put(T1.upper(), "k1", "v1", "a")
        self.assertEqual(self.s.get(T1, "k1"), "v1")

    def test_put_get_same_tenant(self):
        self.s.put(T1, "k1", "v1", "a")
        self.assertEqual(self.s.get(T1, "k1"), "v1")

    def test_cross_tenant_read_blocked_by_scope(self):
        self.s.put(T1, "k1", "v1", "a")
        self.assertIsNone(self.s.get(T2, "k1"))

    def test_list_scoped(self):
        self.s.put(T1, "a/1", 1, "a")
        self.s.put(T2, "a/2", 2, "a")
        self.assertEqual(self.s.list_keys(T1, "a/"), ["a/1"])
        self.assertEqual(self.s.list_keys(T2, "a/"), ["a/2"])

    def test_delete_scoped(self):
        self.s.put(T1, "k", "v", "a")
        self.assertFalse(self.s.delete(T2, "k", "a"))
        self.assertTrue(self.s.delete(T1, "k", "a"))


class TestExportBundle(unittest.TestCase):
    def test_bundle_requires_valid_tenant(self):
        with self.assertRaises(MissingTenantHeader):
            build_export_bundle("", ["k"], 1)

    def test_bundle_sorts_keys(self):
        b = build_export_bundle(T1, ["b", "a"], 2)
        self.assertEqual(b["tenant_id"], T1)
        self.assertEqual(b["keys"], ["a", "b"])
        self.assertEqual(b["records"], 2)

    def test_bundle_records_non_negative(self):
        with self.assertRaises(ValueError):
            build_export_bundle(T1, ["a"], -1)


if __name__ == "__main__":
    unittest.main()
