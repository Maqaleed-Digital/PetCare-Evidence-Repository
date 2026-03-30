from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from FND.CODE_SCAFFOLD.storage.sqlite_store import SqliteStore, SCHEMA_VERSION
from FND.CODE_SCAFFOLD.storage.sqlite_lifecycle import backup_tenant_db, restore_tenant_db, integrity_check


TENANT = "33333333-3333-3333-3333-333333333333"


class TestSqliteGovernance(unittest.TestCase):
    def test_meta_schema_version_present(self):
        with tempfile.TemporaryDirectory() as td:
            s = SqliteStore(base_dir=td)
            s.put(tenant_id=TENANT, key="k", value="v", actor_id="a")

            db = Path(td).resolve() / f"{TENANT}.sqlite"
            self.assertTrue(db.exists())

            conn = sqlite3.connect(str(db))
            try:
                r = conn.execute("SELECT value FROM meta WHERE key='schema_version';").fetchone()
                self.assertIsNotNone(r)
                self.assertEqual(int(r[0]), int(SCHEMA_VERSION))
            finally:
                conn.close()

    def test_integrity_check_ok(self):
        with tempfile.TemporaryDirectory() as td:
            s = SqliteStore(base_dir=td)
            s.put(tenant_id=TENANT, key="k1", value={"a": 1}, actor_id="a")
            rep = integrity_check(tenant_id=TENANT, base_dir=td)
            self.assertTrue(len(rep["results"]) >= 1)
            self.assertEqual(rep["results"][0], "ok")

    def test_backup_restore_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            s = SqliteStore(base_dir=td)
            s.put(tenant_id=TENANT, key="k1", value="v1", actor_id="a")

            out = Path(td).resolve() / "backups"
            b = backup_tenant_db(tenant_id=TENANT, out_dir=str(out), base_dir=td)
            self.assertTrue(Path(b["backup_path"]).exists())

            s.put(tenant_id=TENANT, key="k1", value="v2", actor_id="a")
            self.assertEqual(s.get(tenant_id=TENANT, key="k1"), "v2")

            r = restore_tenant_db(tenant_id=TENANT, backup_path=b["backup_path"], base_dir=td)
            self.assertTrue(Path(r["db_path"]).exists())

            s2 = SqliteStore(base_dir=td)
            self.assertEqual(s2.get(tenant_id=TENANT, key="k1"), "v1")
