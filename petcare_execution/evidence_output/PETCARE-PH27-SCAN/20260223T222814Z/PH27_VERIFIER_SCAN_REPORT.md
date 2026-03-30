# PETCARE-PH27 Verifier Scan Report

This report is generated from the local repository contents (grep-based scan), not from chat history.

## Repo baseline
- Captured in PACK.txt

## Findings
See PH27_VERIFIER_SCAN_RAW.txt for the raw scan output.

## Raw scan (first 200 lines)
```
=== SCAN: verifier keywords in repo ===
./evidence_output/PETCARE-PH29B-CLOSURE/20260223T212656Z/snapshots/TESTS/test_audit_verify_http_endpoint.py:10:    Minimal bundle compatible with existing PH27/PH28 contract patterns.
./evidence_output/PETCARE-PH29B-CLOSURE/20260223T212656Z/snapshots/TESTS/test_audit_verify_http_endpoint.py:12:    We avoid signing requirements because the verifier/service supports
./evidence_output/PETCARE-PH29B-CLOSURE/20260223T212656Z/snapshots/TESTS/test_audit_verify_http_endpoint.py:13:    signature skips when cryptography isn't available (and signer=None in HTTP wiring).
./evidence_output/PETCARE-PH29B-CLOSURE/20260223T212656Z/snapshots/TESTS/test_audit_verify_http_endpoint.py:40:        "bundle_checksum": "00",
./evidence_output/PETCARE-PH29B-CLOSURE/20260223T212656Z/snapshots/TESTS/test_audit_verify_http_endpoint.py:41:        "signature": None,
./evidence_output/PETCARE-PH29B-CLOSURE/20260223T212656Z/snapshots/TESTS/test_audit_verify_http_endpoint.py:42:        "signature_alg": None,
./evidence_output/PETCARE-PH5-INPUT-SNAPSHOT/20260217T135809Z/07_hashes.sha256:712:f049633c97b8a529daa6e8ab1b90e4040803d618201f1100cb314f1fef47d331  ./.venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH15-CLOSURE/20260219T220456Z/snapshots/TESTS/test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
Binary file ./evidence_output/PETCARE-PH15-CLOSURE/20260219T220456Z/snapshots/TESTS/__pycache__/test_tenant_isolation.cpython-314.pyc matches
./evidence_output/PETCARE-PH15-CLOSURE/20260219T220107Z/snapshots/TESTS/test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
Binary file ./evidence_output/PETCARE-PH15-CLOSURE/20260219T220107Z/snapshots/TESTS/__pycache__/test_tenant_isolation.cpython-314.pyc matches
./evidence_output/PETCARE-PH15-CLOSURE/20260219T221746Z/snapshots/TESTS/test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
Binary file ./evidence_output/PETCARE-PH15-CLOSURE/20260219T221746Z/snapshots/TESTS/__pycache__/test_tenant_isolation.cpython-314.pyc matches
./evidence_output/PETCARE-PH15-CLOSURE/20260219T220759Z/snapshots/TESTS/test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
Binary file ./evidence_output/PETCARE-PH15-CLOSURE/20260219T220759Z/snapshots/TESTS/__pycache__/test_tenant_isolation.cpython-314.pyc matches
./evidence_output/PETCARE-PH15-CLOSURE/20260221T135550Z/snapshots/TESTS/test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
Binary file ./evidence_output/PETCARE-PH15-CLOSURE/20260221T135550Z/snapshots/TESTS/__pycache__/test_tenant_isolation.cpython-314.pyc matches
./evidence_output/PETCARE-PH15-CLOSURE/20260219T221325Z/snapshots/TESTS/test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
Binary file ./evidence_output/PETCARE-PH15-CLOSURE/20260219T221325Z/snapshots/TESTS/__pycache__/test_tenant_isolation.cpython-314.pyc matches
./evidence_output/PETCARE-PH23-CLOSURE/20260221T214311Z/closure_sha256.txt:2387:6af34b457c72f1353b476d523b70377947b1c1050480a89f030586c6281610d3  .venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH23-CLOSURE/20260221T214311Z/closure_sha256.txt:2415:f049633c97b8a529daa6e8ab1b90e4040803d618201f1100cb314f1fef47d331  .venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH23-CLOSURE/20260221T214311Z/file_listing.txt:2387:.venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH23-CLOSURE/20260221T214311Z/file_listing.txt:2415:.venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH22-CLOSURE/20260221T211822Z/closure_sha256.txt:2387:6af34b457c72f1353b476d523b70377947b1c1050480a89f030586c6281610d3  .venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH22-CLOSURE/20260221T211822Z/closure_sha256.txt:2415:f049633c97b8a529daa6e8ab1b90e4040803d618201f1100cb314f1fef47d331  .venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH22-CLOSURE/20260221T211822Z/file_listing.txt:2387:.venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH22-CLOSURE/20260221T211822Z/file_listing.txt:2415:.venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH22-CLOSURE/20260221T212340Z/closure_sha256.txt:2387:6af34b457c72f1353b476d523b70377947b1c1050480a89f030586c6281610d3  .venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH22-CLOSURE/20260221T212340Z/closure_sha256.txt:2415:f049633c97b8a529daa6e8ab1b90e4040803d618201f1100cb314f1fef47d331  .venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH22-CLOSURE/20260221T212340Z/file_listing.txt:2387:.venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH22-CLOSURE/20260221T212340Z/file_listing.txt:2415:.venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH14-CLOSURE/20260219T201247Z/snapshots/TESTS/test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
Binary file ./evidence_output/PETCARE-PH14-CLOSURE/20260219T201247Z/snapshots/TESTS/__pycache__/test_tenant_isolation.cpython-314.pyc matches
./evidence_output/PETCARE-PH20-CLOSURE/20260221T193027Z/closure_sha256.txt:2387:6af34b457c72f1353b476d523b70377947b1c1050480a89f030586c6281610d3  .venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH20-CLOSURE/20260221T193027Z/closure_sha256.txt:2415:f049633c97b8a529daa6e8ab1b90e4040803d618201f1100cb314f1fef47d331  .venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH20-CLOSURE/20260221T193027Z/file_listing.txt:2387:.venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH20-CLOSURE/20260221T193027Z/file_listing.txt:2415:.venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH20-CLOSURE/20260221T191718Z/closure_sha256.txt:2387:6af34b457c72f1353b476d523b70377947b1c1050480a89f030586c6281610d3  .venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH20-CLOSURE/20260221T191718Z/closure_sha256.txt:2415:f049633c97b8a529daa6e8ab1b90e4040803d618201f1100cb314f1fef47d331  .venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH20-CLOSURE/20260221T191718Z/file_listing.txt:2387:.venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH20-CLOSURE/20260221T191718Z/file_listing.txt:2415:.venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH20-CLOSURE/20260221T191307Z/closure_sha256.txt:2387:6af34b457c72f1353b476d523b70377947b1c1050480a89f030586c6281610d3  .venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH20-CLOSURE/20260221T191307Z/closure_sha256.txt:2415:f049633c97b8a529daa6e8ab1b90e4040803d618201f1100cb314f1fef47d331  .venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH20-CLOSURE/20260221T191307Z/file_listing.txt:2387:.venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH20-CLOSURE/20260221T191307Z/file_listing.txt:2415:.venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH20-CLOSURE/20260221T192332Z/closure_sha256.txt:2387:6af34b457c72f1353b476d523b70377947b1c1050480a89f030586c6281610d3  .venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH20-CLOSURE/20260221T192332Z/closure_sha256.txt:2415:f049633c97b8a529daa6e8ab1b90e4040803d618201f1100cb314f1fef47d331  .venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH20-CLOSURE/20260221T192332Z/file_listing.txt:2387:.venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH20-CLOSURE/20260221T192332Z/file_listing.txt:2415:.venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH20-CLOSURE/20260221T192724Z/closure_sha256.txt:2387:6af34b457c72f1353b476d523b70377947b1c1050480a89f030586c6281610d3  .venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH20-CLOSURE/20260221T192724Z/closure_sha256.txt:2415:f049633c97b8a529daa6e8ab1b90e4040803d618201f1100cb314f1fef47d331  .venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH20-CLOSURE/20260221T192724Z/file_listing.txt:2387:.venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH20-CLOSURE/20260221T192724Z/file_listing.txt:2415:.venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/repo_files_sha256.txt:710:f049633c97b8a529daa6e8ab1b90e4040803d618201f1100cb314f1fef47d331  ./.venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/repo_files_sha256.txt:710:f049633c97b8a529daa6e8ab1b90e4040803d618201f1100cb314f1fef47d331  ./.venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH16-CLOSURE/20260221T141548Z/snapshots/TESTS/test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
Binary file ./evidence_output/PETCARE-PH16-CLOSURE/20260221T141548Z/snapshots/TESTS/__pycache__/test_tenant_isolation.cpython-314.pyc matches
./evidence_output/PETCARE-PH16-CLOSURE/20260221T140303Z/snapshots/TESTS/test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
Binary file ./evidence_output/PETCARE-PH16-CLOSURE/20260221T140303Z/snapshots/TESTS/__pycache__/test_tenant_isolation.cpython-314.pyc matches
./evidence_output/PETCARE-PH17-CLOSURE/20260221T184712Z/closure_sha256.txt:2403:6af34b457c72f1353b476d523b70377947b1c1050480a89f030586c6281610d3  .venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH17-CLOSURE/20260221T184712Z/closure_sha256.txt:2431:f049633c97b8a529daa6e8ab1b90e4040803d618201f1100cb314f1fef47d331  .venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH17-CLOSURE/20260221T184712Z/file_listing.txt:2403:.venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH17-CLOSURE/20260221T184712Z/file_listing.txt:2431:.venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH21-CLOSURE/20260221T203503Z/closure_sha256.txt:2387:6af34b457c72f1353b476d523b70377947b1c1050480a89f030586c6281610d3  .venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH21-CLOSURE/20260221T203503Z/closure_sha256.txt:2415:f049633c97b8a529daa6e8ab1b90e4040803d618201f1100cb314f1fef47d331  .venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH21-CLOSURE/20260221T203503Z/file_listing.txt:2387:.venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH21-CLOSURE/20260221T203503Z/file_listing.txt:2415:.venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH24-CLOSURE/20260221T220403Z/closure_sha256.txt:2387:6af34b457c72f1353b476d523b70377947b1c1050480a89f030586c6281610d3  .venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH24-CLOSURE/20260221T220403Z/closure_sha256.txt:2415:f049633c97b8a529daa6e8ab1b90e4040803d618201f1100cb314f1fef47d331  .venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH24-CLOSURE/20260221T220403Z/file_listing.txt:2387:.venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH24-CLOSURE/20260221T220403Z/file_listing.txt:2415:.venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH24-CLOSURE/20260221T220702Z/closure_sha256.txt:2387:6af34b457c72f1353b476d523b70377947b1c1050480a89f030586c6281610d3  .venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH24-CLOSURE/20260221T220702Z/closure_sha256.txt:2415:f049633c97b8a529daa6e8ab1b90e4040803d618201f1100cb314f1fef47d331  .venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH24-CLOSURE/20260221T220702Z/file_listing.txt:2387:.venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH24-CLOSURE/20260221T220702Z/file_listing.txt:2415:.venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH12-CLOSURE/20260218T222446Z/snapshots/TESTS/test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
Binary file ./evidence_output/PETCARE-PH12-CLOSURE/20260218T222446Z/snapshots/TESTS/__pycache__/test_tenant_isolation.cpython-314.pyc matches
./evidence_output/_archive_failed_runs/PETCARE-PH29B-CLOSURE/20260223T212126Z/snapshots/TESTS/test_audit_verify_http_endpoint.py:10:    Minimal bundle compatible with existing PH27/PH28 contract patterns.
./evidence_output/_archive_failed_runs/PETCARE-PH29B-CLOSURE/20260223T212126Z/snapshots/TESTS/test_audit_verify_http_endpoint.py:12:    We avoid signing requirements because the verifier/service supports
./evidence_output/_archive_failed_runs/PETCARE-PH29B-CLOSURE/20260223T212126Z/snapshots/TESTS/test_audit_verify_http_endpoint.py:13:    signature skips when cryptography isn't available (and signer=None in HTTP wiring).
./evidence_output/_archive_failed_runs/PETCARE-PH29B-CLOSURE/20260223T212126Z/snapshots/TESTS/test_audit_verify_http_endpoint.py:40:        "bundle_checksum": "00",
./evidence_output/_archive_failed_runs/PETCARE-PH29B-CLOSURE/20260223T212126Z/snapshots/TESTS/test_audit_verify_http_endpoint.py:41:        "signature": None,
./evidence_output/_archive_failed_runs/PETCARE-PH29B-CLOSURE/20260223T212126Z/snapshots/TESTS/test_audit_verify_http_endpoint.py:42:        "signature_alg": None,
./evidence_output/PETCARE-PH7-CLOSURE/20260217T185855Z/unittest.log:11:test_bundle_schema_and_hashes_present (test_tenant_isolation.TestExportBundleHardening) ... ok
./evidence_output/PETCARE-PH7-CLOSURE/20260217T185855Z/closure.log:25:test_bundle_schema_and_hashes_present (test_tenant_isolation.TestExportBundleHardening) ... ok
./evidence_output/PETCARE-PH7-CLOSURE/20260217T190106Z/unittest.log:11:test_bundle_schema_and_hashes_present (test_tenant_isolation.TestExportBundleHardening) ... ok
./evidence_output/PETCARE-PH7-CLOSURE/20260217T190106Z/closure.log:25:test_bundle_schema_and_hashes_present (test_tenant_isolation.TestExportBundleHardening) ... ok
./evidence_output/PETCARE-PH7-CLOSURE/20260217T181431Z/unittest.log:9:test_bundle_schema_and_hashes_present (test_tenant_isolation.TestExportBundleHardening) ... ok
./evidence_output/PETCARE-PH7-CLOSURE/20260217T181431Z/closure.log:23:test_bundle_schema_and_hashes_present (test_tenant_isolation.TestExportBundleHardening) ... ok
./evidence_output/PETCARE-PH7-CLOSURE/20260217T185521Z/unittest.log:11:test_bundle_schema_and_hashes_present (test_tenant_isolation.TestExportBundleHardening) ... ok
./evidence_output/PETCARE-PH7-CLOSURE/20260217T185521Z/closure.log:25:test_bundle_schema_and_hashes_present (test_tenant_isolation.TestExportBundleHardening) ... ok
./evidence_output/PETCARE-PH7-CLOSURE/20260217T185109Z/unittest.log:11:test_bundle_schema_and_hashes_present (test_tenant_isolation.TestExportBundleHardening) ... ok
./evidence_output/PETCARE-PH7-CLOSURE/20260217T185109Z/closure.log:25:test_bundle_schema_and_hashes_present (test_tenant_isolation.TestExportBundleHardening) ... ok
./evidence_output/PETCARE-PH7-CLOSURE/20260217T190409Z/unittest.log:11:test_bundle_schema_and_hashes_present (test_tenant_isolation.TestExportBundleHardening) ... ok
./evidence_output/PETCARE-PH7-CLOSURE/20260217T190409Z/repo_snapshot/TESTS/test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
Binary file ./evidence_output/PETCARE-PH7-CLOSURE/20260217T190409Z/repo_snapshot/TESTS/__pycache__/test_tenant_isolation.cpython-314.pyc matches
./evidence_output/PETCARE-PH7-CLOSURE/20260217T190409Z/closure.log:25:test_bundle_schema_and_hashes_present (test_tenant_isolation.TestExportBundleHardening) ... ok
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/snapshots/evidence_output__PETCARE-PH8-PREFLIGHT__20260218T202149Z__snapshots__evidence_output__PETCARE-PH5-CLOSURE__20260217T143204Z__repo_snapshot__TESTS__test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/snapshots/evidence_output__PETCARE-PH8-PREFLIGHT__20260218T202149Z__snapshots__evidence_output__PETCARE-PH6-CLOSURE__20260217T145345Z__repo_snapshot__TESTS__test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/snapshots/TESTS__test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/snapshots/evidence_output__PETCARE-PH4-CLOSURE__20260217T133616Z__repo_snapshot__TESTS__test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/snapshots/evidence_output__PETCARE-PH8-PREFLIGHT__20260218T202149Z__snapshots__evidence_output__PETCARE-PH7-CLOSURE__20260217T190409Z__repo_snapshot__TESTS__test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
Binary file ./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/snapshots/__pycache__/evidence_output__PETCARE-PH8-PREFLIGHT__20260218T202149Z__snapshots__evidence_output__PETCARE-PH4-CLOSURE__20260217T133616Z__repo_snapshot__TESTS__test_tenant_isolation.cpython-314.pyc matches
Binary file ./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/snapshots/__pycache__/evidence_output__PETCARE-PH7-CLOSURE__20260217T190409Z__repo_snapshot__TESTS__test_tenant_isolation.cpython-314.pyc matches
Binary file ./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/snapshots/__pycache__/evidence_output__PETCARE-PH8-PREFLIGHT__20260218T202149Z__snapshots__evidence_output__PETCARE-PH5-CLOSURE__20260217T143204Z__repo_snapshot__TESTS__test_tenant_isolation.cpython-314.pyc matches
Binary file ./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/snapshots/__pycache__/evidence_output__PETCARE-PH6-CLOSURE__20260217T145345Z__repo_snapshot__TESTS__test_tenant_isolation.cpython-314.pyc matches
Binary file ./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/snapshots/__pycache__/.venv__lib__python3.9__site-packages__starlette__authentication.cpython-314.pyc matches
Binary file ./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/snapshots/__pycache__/evidence_output__PETCARE-PH8-PREFLIGHT__20260218T202149Z__snapshots__TESTS__test_tenant_isolation.cpython-314.pyc matches
Binary file ./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/snapshots/__pycache__/evidence_output__PETCARE-PH8-PREFLIGHT__20260218T202149Z__snapshots__evidence_output__PETCARE-PH4-CLOSURE__20260217T134016Z__repo_snapshot__TESTS__test_tenant_isolation.cpython-314.pyc matches
Binary file ./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/snapshots/__pycache__/TESTS__test_tenant_isolation.cpython-314.pyc matches
Binary file ./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/snapshots/__pycache__/evidence_output__PETCARE-PH4-CLOSURE__20260217T133616Z__repo_snapshot__TESTS__test_tenant_isolation.cpython-314.pyc matches
Binary file ./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/snapshots/__pycache__/evidence_output__PETCARE-PH8-PREFLIGHT__20260218T202149Z__snapshots__evidence_output__PETCARE-PH7-CLOSURE__20260217T190409Z__repo_snapshot__TESTS__test_tenant_isolation.cpython-314.pyc matches
Binary file ./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/snapshots/__pycache__/evidence_output__PETCARE-PH5-CLOSURE__20260217T143204Z__repo_snapshot__TESTS__test_tenant_isolation.cpython-314.pyc matches
Binary file ./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/snapshots/__pycache__/evidence_output__PETCARE-PH8-PREFLIGHT__20260218T202149Z__snapshots__evidence_output__PETCARE-PH6-CLOSURE__20260217T145345Z__repo_snapshot__TESTS__test_tenant_isolation.cpython-314.pyc matches
Binary file ./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/snapshots/__pycache__/evidence_output__PETCARE-PH8-PREFLIGHT__20260218T202149Z__snapshots__.venv__lib__python3.9__site-packages__starlette__authentication.cpython-314.pyc matches
Binary file ./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/snapshots/__pycache__/evidence_output__PETCARE-PH4-CLOSURE__20260217T134016Z__repo_snapshot__TESTS__test_tenant_isolation.cpython-314.pyc matches
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/snapshots/evidence_output__PETCARE-PH8-PREFLIGHT__20260218T202149Z__snapshots__evidence_output__PETCARE-PH4-CLOSURE__20260217T134016Z__repo_snapshot__TESTS__test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/snapshots/evidence_output__PETCARE-PH8-PREFLIGHT__20260218T202149Z__snapshots__evidence_output__PETCARE-PH4-CLOSURE__20260217T133616Z__repo_snapshot__TESTS__test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/snapshots/evidence_output__PETCARE-PH7-CLOSURE__20260217T190409Z__repo_snapshot__TESTS__test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/snapshots/evidence_output__PETCARE-PH4-CLOSURE__20260217T134016Z__repo_snapshot__TESTS__test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/snapshots/evidence_output__PETCARE-PH8-PREFLIGHT__20260218T202149Z__snapshots__TESTS__test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/snapshots/evidence_output__PETCARE-PH8-PREFLIGHT__20260218T202149Z__snapshots__.venv__lib__python3.9__site-packages__starlette__authentication.py:40:        sig = inspect.signature(func)
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/snapshots/evidence_output__PETCARE-PH5-CLOSURE__20260217T143204Z__repo_snapshot__TESTS__test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/snapshots/.venv__lib__python3.9__site-packages__starlette__authentication.py:40:        sig = inspect.signature(func)
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/snapshots/evidence_output__PETCARE-PH6-CLOSURE__20260217T145345Z__repo_snapshot__TESTS__test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202351Z/PH5_ARCHITECTURE_SCAN.md:269:./TESTS/test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/snapshots/TESTS__test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/snapshots/evidence_output__PETCARE-PH4-CLOSURE__20260217T133616Z__repo_snapshot__TESTS__test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
Binary file ./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/snapshots/__pycache__/evidence_output__PETCARE-PH7-CLOSURE__20260217T190409Z__repo_snapshot__TESTS__test_tenant_isolation.cpython-314.pyc matches
Binary file ./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/snapshots/__pycache__/evidence_output__PETCARE-PH6-CLOSURE__20260217T145345Z__repo_snapshot__TESTS__test_tenant_isolation.cpython-314.pyc matches
Binary file ./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/snapshots/__pycache__/.venv__lib__python3.9__site-packages__starlette__authentication.cpython-314.pyc matches
Binary file ./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/snapshots/__pycache__/TESTS__test_tenant_isolation.cpython-314.pyc matches
Binary file ./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/snapshots/__pycache__/evidence_output__PETCARE-PH4-CLOSURE__20260217T133616Z__repo_snapshot__TESTS__test_tenant_isolation.cpython-314.pyc matches
Binary file ./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/snapshots/__pycache__/evidence_output__PETCARE-PH5-CLOSURE__20260217T143204Z__repo_snapshot__TESTS__test_tenant_isolation.cpython-314.pyc matches
Binary file ./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/snapshots/__pycache__/evidence_output__PETCARE-PH4-CLOSURE__20260217T134016Z__repo_snapshot__TESTS__test_tenant_isolation.cpython-314.pyc matches
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/snapshots/evidence_output__PETCARE-PH7-CLOSURE__20260217T190409Z__repo_snapshot__TESTS__test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/snapshots/evidence_output__PETCARE-PH4-CLOSURE__20260217T134016Z__repo_snapshot__TESTS__test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/snapshots/evidence_output__PETCARE-PH5-CLOSURE__20260217T143204Z__repo_snapshot__TESTS__test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/snapshots/.venv__lib__python3.9__site-packages__starlette__authentication.py:40:        sig = inspect.signature(func)
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/snapshots/evidence_output__PETCARE-PH6-CLOSURE__20260217T145345Z__repo_snapshot__TESTS__test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:154:./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:22:test_bundle_schema_and_hashes_present (test_tenant_isolation.TestExportBundleHardening) ... ok
./evidence_output/PETCARE-PH13-CLOSURE/20260219T195936Z/snapshots/TESTS/test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
Binary file ./evidence_output/PETCARE-PH13-CLOSURE/20260219T195936Z/snapshots/TESTS/__pycache__/test_tenant_isolation.cpython-314.pyc matches
./evidence_output/PETCARE-PH13-CLOSURE/20260219T193927Z/snapshots/tests/test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
Binary file ./evidence_output/PETCARE-PH13-CLOSURE/20260219T193927Z/snapshots/tests/__pycache__/test_tenant_isolation.cpython-314.pyc matches
./evidence_output/PETCARE-PH13-CLOSURE/20260219T193714Z/snapshots/tests/test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
Binary file ./evidence_output/PETCARE-PH13-CLOSURE/20260219T193714Z/snapshots/tests/__pycache__/test_tenant_isolation.cpython-314.pyc matches
./evidence_output/PETCARE-PH13-CLOSURE/20260219T193643Z/snapshots/tests/test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
Binary file ./evidence_output/PETCARE-PH13-CLOSURE/20260219T193643Z/snapshots/tests/__pycache__/test_tenant_isolation.cpython-314.pyc matches
./evidence_output/PETCARE-PH13-CLOSURE/20260219T194800Z/snapshots/tests/test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
Binary file ./evidence_output/PETCARE-PH13-CLOSURE/20260219T194800Z/snapshots/tests/__pycache__/test_tenant_isolation.cpython-314.pyc matches
./evidence_output/PETCARE-PH13-CLOSURE/20260219T192105Z/snapshots/tests/test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
Binary file ./evidence_output/PETCARE-PH13-CLOSURE/20260219T192105Z/snapshots/tests/__pycache__/test_tenant_isolation.cpython-314.pyc matches
./evidence_output/PETCARE-PH13-CLOSURE/20260219T194431Z/snapshots/tests/test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
Binary file ./evidence_output/PETCARE-PH13-CLOSURE/20260219T194431Z/snapshots/tests/__pycache__/test_tenant_isolation.cpython-314.pyc matches
./evidence_output/PETCARE-PH6-CLOSURE/20260217T145345Z/unittest.log:11:test_bundle_schema_and_hashes_present (test_tenant_isolation.TestExportBundleHardening) ... ok
./evidence_output/PETCARE-PH6-CLOSURE/20260217T145345Z/repo_snapshot/TESTS/test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
Binary file ./evidence_output/PETCARE-PH6-CLOSURE/20260217T145345Z/repo_snapshot/TESTS/__pycache__/test_tenant_isolation.cpython-314.pyc matches
./evidence_output/PETCARE-PH6-CLOSURE/20260217T145345Z/closure.log:25:test_bundle_schema_and_hashes_present (test_tenant_isolation.TestExportBundleHardening) ... ok
./evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/unittest.log:3:test_bundle_schema_and_hashes_present (test_tenant_isolation.TestExportBundleHardening) ... ok
./evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/TESTS/test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
Binary file ./evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/TESTS/__pycache__/test_tenant_isolation.cpython-314.pyc matches
./evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/closure.log:16:test_bundle_schema_and_hashes_present (test_tenant_isolation.TestExportBundleHardening) ... ok
./evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/unittest.log:3:test_bundle_schema_and_hashes_present (test_tenant_isolation.TestExportBundleHardening) ... ok
./evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/TESTS/test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
Binary file ./evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/TESTS/__pycache__/test_tenant_isolation.cpython-314.pyc matches
./evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/closure.log:16:test_bundle_schema_and_hashes_present (test_tenant_isolation.TestExportBundleHardening) ... ok
./evidence_output/PETCARE-PH18-CLOSURE/20260221T185435Z/closure_sha256.txt:2387:6af34b457c72f1353b476d523b70377947b1c1050480a89f030586c6281610d3  .venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH18-CLOSURE/20260221T185435Z/closure_sha256.txt:2415:f049633c97b8a529daa6e8ab1b90e4040803d618201f1100cb314f1fef47d331  .venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH18-CLOSURE/20260221T185435Z/file_listing.txt:2387:.venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH18-CLOSURE/20260221T185435Z/file_listing.txt:2415:.venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH19-CLOSURE/20260221T190305Z/closure_sha256.txt:2387:6af34b457c72f1353b476d523b70377947b1c1050480a89f030586c6281610d3  .venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH19-CLOSURE/20260221T190305Z/closure_sha256.txt:2415:f049633c97b8a529daa6e8ab1b90e4040803d618201f1100cb314f1fef47d331  .venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH19-CLOSURE/20260221T190305Z/file_listing.txt:2387:.venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH19-CLOSURE/20260221T190305Z/file_listing.txt:2415:.venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH27-SCAN/20260223T222814Z/snapshots/20260223T222814Z/LATEST_PH27.txt:1:LATEST_PH27=evidence_output/PETCARE-PH27-SCAN/20260223T222814Z/
./evidence_output/PETCARE-PH27-SCAN/20260223T222814Z/snapshots/20260223T222814Z/PACK.txt:1:PETCARE-PH27-SCAN
./evidence_output/PETCARE-PH27-SCAN/20260223T222814Z/LATEST_PH27.txt:1:LATEST_PH27=evidence_output/PETCARE-PH27-SCAN/20260223T222814Z/
./evidence_output/PETCARE-PH27-SCAN/20260223T222814Z/_tmp_scan.txt:1:=== SCAN: verifier keywords in repo ===
./evidence_output/PETCARE-PH27-SCAN/20260223T222814Z/_tmp_scan.txt:2:./evidence_output/PETCARE-PH29B-CLOSURE/20260223T212656Z/snapshots/TESTS/test_audit_verify_http_endpoint.py:10:    Minimal bundle compatible with existing PH27/PH28 contract patterns.
./evidence_output/PETCARE-PH27-SCAN/20260223T222814Z/_tmp_scan.txt:3:./evidence_output/PETCARE-PH29B-CLOSURE/20260223T212656Z/snapshots/TESTS/test_audit_verify_http_endpoint.py:12:    We avoid signing requirements because the verifier/service supports
./evidence_output/PETCARE-PH27-SCAN/20260223T222814Z/_tmp_scan.txt:4:./evidence_output/PETCARE-PH29B-CLOSURE/20260223T212656Z/snapshots/TESTS/test_audit_verify_http_endpoint.py:13:    signature skips when cryptography isn't available (and signer=None in HTTP wiring).
./evidence_output/PETCARE-PH27-SCAN/20260223T222814Z/_tmp_scan.txt:5:./evidence_output/PETCARE-PH29B-CLOSURE/20260223T212656Z/snapshots/TESTS/test_audit_verify_http_endpoint.py:40:        "bundle_checksum": "00",
./evidence_output/PETCARE-PH27-SCAN/20260223T222814Z/_tmp_scan.txt:6:./evidence_output/PETCARE-PH29B-CLOSURE/20260223T212656Z/snapshots/TESTS/test_audit_verify_http_endpoint.py:41:        "signature": None,
./evidence_output/PETCARE-PH27-SCAN/20260223T222814Z/_tmp_scan.txt:7:./evidence_output/PETCARE-PH29B-CLOSURE/20260223T212656Z/snapshots/TESTS/test_audit_verify_http_endpoint.py:42:        "signature_alg": None,
./evidence_output/PETCARE-PH27-SCAN/20260223T222814Z/_tmp_scan.txt:8:./evidence_output/PETCARE-PH5-INPUT-SNAPSHOT/20260217T135809Z/07_hashes.sha256:712:f049633c97b8a529daa6e8ab1b90e4040803d618201f1100cb314f1fef47d331  ./.venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH27-SCAN/20260223T222814Z/_tmp_scan.txt:9:./evidence_output/PETCARE-PH15-CLOSURE/20260219T220456Z/snapshots/TESTS/test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
./evidence_output/PETCARE-PH27-SCAN/20260223T222814Z/_tmp_scan.txt:11:./evidence_output/PETCARE-PH15-CLOSURE/20260219T220107Z/snapshots/TESTS/test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
./evidence_output/PETCARE-PH27-SCAN/20260223T222814Z/_tmp_scan.txt:13:./evidence_output/PETCARE-PH15-CLOSURE/20260219T221746Z/snapshots/TESTS/test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
./evidence_output/PETCARE-PH27-SCAN/20260223T222814Z/_tmp_scan.txt:15:./evidence_output/PETCARE-PH15-CLOSURE/20260219T220759Z/snapshots/TESTS/test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
./evidence_output/PETCARE-PH27-SCAN/20260223T222814Z/_tmp_scan.txt:17:./evidence_output/PETCARE-PH15-CLOSURE/20260221T135550Z/snapshots/TESTS/test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
./evidence_output/PETCARE-PH27-SCAN/20260223T222814Z/_tmp_scan.txt:19:./evidence_output/PETCARE-PH15-CLOSURE/20260219T221325Z/snapshots/TESTS/test_tenant_isolation.py:103:    def test_bundle_schema_and_hashes_present(self):
./evidence_output/PETCARE-PH27-SCAN/20260223T222814Z/_tmp_scan.txt:21:./evidence_output/PETCARE-PH23-CLOSURE/20260221T214311Z/closure_sha256.txt:2387:6af34b457c72f1353b476d523b70377947b1c1050480a89f030586c6281610d3  .venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH27-SCAN/20260223T222814Z/_tmp_scan.txt:22:./evidence_output/PETCARE-PH23-CLOSURE/20260221T214311Z/closure_sha256.txt:2415:f049633c97b8a529daa6e8ab1b90e4040803d618201f1100cb314f1fef47d331  .venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH27-SCAN/20260223T222814Z/_tmp_scan.txt:23:./evidence_output/PETCARE-PH23-CLOSURE/20260221T214311Z/file_listing.txt:2387:.venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH27-SCAN/20260223T222814Z/_tmp_scan.txt:24:./evidence_output/PETCARE-PH23-CLOSURE/20260221T214311Z/file_listing.txt:2415:.venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH27-SCAN/20260223T222814Z/_tmp_scan.txt:25:./evidence_output/PETCARE-PH22-CLOSURE/20260221T211822Z/closure_sha256.txt:2387:6af34b457c72f1353b476d523b70377947b1c1050480a89f030586c6281610d3  .venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
./evidence_output/PETCARE-PH27-SCAN/20260223T222814Z/_tmp_scan.txt:26:./evidence_output/PETCARE-PH22-CLOSURE/20260221T211822Z/closure_sha256.txt:2415:f049633c97b8a529daa6e8ab1b90e4040803d618201f1100cb314f1fef47d331  .venv/lib/python3.9/site-packages/pydantic/_internal/_signature.py
./evidence_output/PETCARE-PH27-SCAN/20260223T222814Z/_tmp_scan.txt:27:./evidence_output/PETCARE-PH22-CLOSURE/20260221T211822Z/file_listing.txt:2387:.venv/lib/python3.9/site-packages/pydantic/_internal/__pycache__/_signature.cpython-314.pyc
```
