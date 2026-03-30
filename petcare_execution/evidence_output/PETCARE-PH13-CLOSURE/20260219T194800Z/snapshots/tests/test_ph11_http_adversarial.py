import json
import os
import tempfile
import unittest

ACTOR_OK = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
TENANT = "33333333-3333-3333-3333-333333333333"

def _fastapi_available() -> bool:
    try:
        import fastapi  # noqa: F401
        return True
    except Exception:
        return False

def _testclient_available() -> bool:
    try:
        from fastapi.testclient import TestClient  # noqa: F401
        return True
    except Exception:
        return False

def _write_policy(path: str) -> None:
    obj = {
        "schema": "PETCARE_SECURITY_POLICY_V1",
        "mode": "TRUST",
        "deny_by_default": True,
        "auth": {
            "require_auth_token": True,
            "expected_token": "secret",
            "actor_header": "X-Actor-Id",
            "token_header": "X-Auth-Token"
        },
        "evidence_export": {
            "pii_requires_watermark": True,
            "pii_requires_encryption": True
        }
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)

class TestPH11HTTPAdversarial(unittest.TestCase):
    def setUp(self):
        if not _fastapi_available():
            self.skipTest("fastapi not available")
        if not _testclient_available():
            self.skipTest("fastapi.testclient not available")

    def test_missing_token_denied_in_trust(self):
        from fastapi.testclient import TestClient
        from FND.CODE_SCAFFOLD.app import create_app

        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "policy.json")
            _write_policy(p)
            os.environ["PETCARE_POLICY_PATH"] = p

            app = create_app()
            c = TestClient(app)
            r = c.post(
                "/api/platform-admin/storage/list",
                headers={"X-Tenant-ID": TENANT, "X-Actor-Id": ACTOR_OK},
                json={"prefix": ""},
            )
            self.assertIn(r.status_code, [401, 403])

    def test_pii_export_requires_flags(self):
        from fastapi.testclient import TestClient
        from FND.CODE_SCAFFOLD.app import create_app

        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "policy.json")
            _write_policy(p)
            os.environ["PETCARE_POLICY_PATH"] = p

            app = create_app()
            c = TestClient(app)

            headers = {
                "X-Tenant-ID": TENANT,
                "X-Actor-Id": ACTOR_OK,
                "X-Auth-Token": "secret",
            }

            r = c.post(
                "/api/platform-admin/storage/export",
                headers=headers,
                json={"prefix": "", "include_pii": True, "watermark": False, "encryption": True},
            )
            self.assertEqual(r.status_code, 400)

            r2 = c.post(
                "/api/platform-admin/storage/export",
                headers=headers,
                json={"prefix": "", "include_pii": True, "watermark": True, "encryption": False},
            )
            self.assertEqual(r2.status_code, 400)

            r3 = c.post(
                "/api/platform-admin/storage/export",
                headers=headers,
                json={"prefix": "", "include_pii": True, "watermark": True, "encryption": True},
            )
            self.assertEqual(r3.status_code, 200)

if __name__ == "__main__":
    unittest.main()
