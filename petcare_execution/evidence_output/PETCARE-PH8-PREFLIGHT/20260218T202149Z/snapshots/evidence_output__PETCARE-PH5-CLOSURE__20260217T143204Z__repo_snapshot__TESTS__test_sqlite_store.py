from __future__ import annotations

import tempfile
import unittest

from FND.CODE_SCAFFOLD.storage.sqlite_store import SqliteStore


TENANT_A = "11111111-1111-1111-1111-111111111111"
TENANT_B = "22222222-2222-2222-2222-222222222222"


class TestSqliteStore(unittest.TestCase):
    def test_put_get_persists_across_instances(self):
        with tempfile.TemporaryDirectory() as td:
            s1 = SqliteStore(base_dir=td)
            s1.put(tenant_id=TENANT_A, key="k1", value={"a": 1}, actor_id="u1")

            s2 = SqliteStore(base_dir=td)
            v = s2.get(tenant_id=TENANT_A, key="k1")
            self.assertEqual(v, {"a": 1})

    def test_tenant_isolation_by_file(self):
        with tempfile.TemporaryDirectory() as td:
            s = SqliteStore(base_dir=td)
            s.put(tenant_id=TENANT_A, key="shared", value="A", actor_id="u1")
            s.put(tenant_id=TENANT_B, key="shared", value="B", actor_id="u1")

            self.assertEqual(s.get(tenant_id=TENANT_A, key="shared"), "A")
            self.assertEqual(s.get(tenant_id=TENANT_B, key="shared"), "B")

    def test_list_keys_sorted_and_prefix(self):
        with tempfile.TemporaryDirectory() as td:
            s = SqliteStore(base_dir=td)
            s.put(tenant_id=TENANT_A, key="b/2", value=2, actor_id="u1")
            s.put(tenant_id=TENANT_A, key="a/1", value=1, actor_id="u1")
            s.put(tenant_id=TENANT_A, key="a/2", value=2, actor_id="u1")

            self.assertEqual(s.list_keys(tenant_id=TENANT_A), ["a/1", "a/2", "b/2"])
            self.assertEqual(s.list_keys(tenant_id=TENANT_A, prefix="a/"), ["a/1", "a/2"])

    def test_delete_audit_existed_flag(self):
        with tempfile.TemporaryDirectory() as td:
            s = SqliteStore(base_dir=td)
            s.put(tenant_id=TENANT_A, key="k", value=1, actor_id="u1")

            existed_true = s.delete(tenant_id=TENANT_A, key="k", actor_id="u2")
            existed_false = s.delete(tenant_id=TENANT_A, key="k", actor_id="u3")

            self.assertTrue(existed_true)
            self.assertFalse(existed_false)

            audit = s.audit_log(tenant_id=TENANT_A)
            deletes = [e for e in audit if e.get("action") == "delete"]
            self.assertEqual(len(deletes), 2)
            self.assertEqual(deletes[0].get("existed"), True)
            self.assertEqual(deletes[1].get("existed"), False)

    def test_export_items_stable(self):
        with tempfile.TemporaryDirectory() as td:
            s = SqliteStore(base_dir=td)
            s.put(tenant_id=TENANT_A, key="b", value=2, actor_id="u1")
            s.put(tenant_id=TENANT_A, key="a", value=1, actor_id="u1")
            items = s.export_items(tenant_id=TENANT_A)
            self.assertEqual([x["key"] for x in items], ["a", "b"])
            self.assertEqual(items[0]["value"], 1)
            self.assertEqual(items[1]["value"], 2)
