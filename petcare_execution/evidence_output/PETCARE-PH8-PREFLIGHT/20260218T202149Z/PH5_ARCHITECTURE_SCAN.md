# PH5 Architecture Scan (Preflight for PH8)

Generated (UTC): 20260218T202149Z

## Repo Context
```
=== BASIC REPO CONTEXT ===
/Users/waheebmahmoud/dev/petcare-evidence-repository/petcare_execution

## main...origin/main

145869c petcare: ignore venv + evidence outputs
```

## Discovered Docs (PH5/UI5/Architecture/Pack Summaries)
```
=== LOCATE PH5 / UI5 / ARCHITECTURE DOCS ===
TESTS/UI5_TEST_CHECKLIST.md
TESTS/__pycache__/ui5_deterministic_proof.cpython-314.pyc
TESTS/ui5_deterministic_proof.py
UI2/UI2_PACK_SUMMARY.md
UI3/UI3_PACK_SUMMARY.md
UI5/UI5_PACK_SUMMARY.md
UI6/UI6_PACK_SUMMARY.md
evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/TESTS/UI5_TEST_CHECKLIST.md
evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/TESTS/ui5_deterministic_proof.py
evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/UI2/UI2_PACK_SUMMARY.md
evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/UI3/UI3_PACK_SUMMARY.md
evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/UI5/UI5_PACK_SUMMARY.md
evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/UI6/UI6_PACK_SUMMARY.md
evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/TESTS/UI5_TEST_CHECKLIST.md
evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/TESTS/ui5_deterministic_proof.py
evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/UI2/UI2_PACK_SUMMARY.md
evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/UI3/UI3_PACK_SUMMARY.md
evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/UI5/UI5_PACK_SUMMARY.md
evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/UI6/UI6_PACK_SUMMARY.md
evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/repo_snapshot/TESTS/UI5_TEST_CHECKLIST.md
evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/repo_snapshot/TESTS/ui5_deterministic_proof.py
evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/repo_snapshot/UI2/UI2_PACK_SUMMARY.md
evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/repo_snapshot/UI3/UI3_PACK_SUMMARY.md
evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/repo_snapshot/UI5/UI5_PACK_SUMMARY.md
evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/repo_snapshot/UI6/UI6_PACK_SUMMARY.md
evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/repo_snapshot/scripts/petcare_ph5_closure_pack.sh
evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/repo_snapshot/scripts/petcare_ph5_unittest.sh
evidence_output/PETCARE-PH5-CLOSURE/PETCARE-PH5-CLOSURE_20260217T143204Z.zip
evidence_output/PETCARE-PH5-CLOSURE/PETCARE-PH5-CLOSURE_20260217T143204Z.zip.sha256
evidence_output/PETCARE-PH6-CLOSURE/20260217T145345Z/repo_snapshot/TESTS/UI5_TEST_CHECKLIST.md
evidence_output/PETCARE-PH6-CLOSURE/20260217T145345Z/repo_snapshot/TESTS/ui5_deterministic_proof.py
evidence_output/PETCARE-PH6-CLOSURE/20260217T145345Z/repo_snapshot/UI2/UI2_PACK_SUMMARY.md
evidence_output/PETCARE-PH6-CLOSURE/20260217T145345Z/repo_snapshot/UI3/UI3_PACK_SUMMARY.md
evidence_output/PETCARE-PH6-CLOSURE/20260217T145345Z/repo_snapshot/UI5/UI5_PACK_SUMMARY.md
evidence_output/PETCARE-PH6-CLOSURE/20260217T145345Z/repo_snapshot/UI6/UI6_PACK_SUMMARY.md
evidence_output/PETCARE-PH6-CLOSURE/20260217T145345Z/repo_snapshot/scripts/petcare_ph5_closure_pack.sh
evidence_output/PETCARE-PH6-CLOSURE/20260217T145345Z/repo_snapshot/scripts/petcare_ph5_unittest.sh
evidence_output/PETCARE-PH6-INPUT-SNAPSHOT/20260217T144121Z/scripts__petcare_ph5_closure_pack.sh
evidence_output/PETCARE-PH7-CLOSURE/20260217T190409Z/repo_snapshot/TESTS/UI5_TEST_CHECKLIST.md
evidence_output/PETCARE-PH7-CLOSURE/20260217T190409Z/repo_snapshot/TESTS/ui5_deterministic_proof.py
evidence_output/PETCARE-PH7-CLOSURE/20260217T190409Z/repo_snapshot/UI2/UI2_PACK_SUMMARY.md
evidence_output/PETCARE-PH7-CLOSURE/20260217T190409Z/repo_snapshot/UI3/UI3_PACK_SUMMARY.md
evidence_output/PETCARE-PH7-CLOSURE/20260217T190409Z/repo_snapshot/UI5/UI5_PACK_SUMMARY.md
evidence_output/PETCARE-PH7-CLOSURE/20260217T190409Z/repo_snapshot/UI6/UI6_PACK_SUMMARY.md
evidence_output/PETCARE-PH7-CLOSURE/20260217T190409Z/repo_snapshot/scripts/petcare_ph5_closure_pack.sh
evidence_output/PETCARE-PH7-CLOSURE/20260217T190409Z/repo_snapshot/scripts/petcare_ph5_unittest.sh
evidence_output/PETCARE-PH7-INPUT-SNAPSHOT/20260217T174838Z/scripts__petcare_ph5_closure_pack.sh
evidence_output/_local_debug_ph5_closure_20260217T142018Z.log
scripts/petcare_ph5_closure_pack.sh
scripts/petcare_ph5_unittest.sh
```

## Discovered Code (API/Auth/Audit/SQLite/Export/Tests)
```
=== LOCATE API/AUTH/AUDIT/SQLITE/EXPORT/TEST FILES ===
.venv/lib/python3.9/site-packages/annotated_types/test_cases.py
.venv/lib/python3.9/site-packages/anyio/_core/_testing.py
.venv/lib/python3.9/site-packages/anyio/abc/_testing.py
.venv/lib/python3.9/site-packages/anyio/pytest_plugin.py
.venv/lib/python3.9/site-packages/click/testing.py
.venv/lib/python3.9/site-packages/fastapi/security/api_key.py
.venv/lib/python3.9/site-packages/fastapi/security/oauth2.py
.venv/lib/python3.9/site-packages/fastapi/testclient.py
.venv/lib/python3.9/site-packages/setuptools/command/test.py
.venv/lib/python3.9/site-packages/starlette/authentication.py
.venv/lib/python3.9/site-packages/starlette/middleware/authentication.py
.venv/lib/python3.9/site-packages/starlette/testclient.py
FND/CODE_SCAFFOLD/api/routes_platform_admin.py
FND/CODE_SCAFFOLD/app.py
FND/CODE_SCAFFOLD/storage/export_bundle.py
FND/CODE_SCAFFOLD/storage/sqlite_lifecycle.py
FND/CODE_SCAFFOLD/storage/sqlite_store.py
TESTS/test_sqlite_governance.py
TESTS/test_sqlite_store.py
TESTS/test_tenant_isolation.py
evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/app.py
evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/TESTS/test_tenant_isolation.py
evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/app.py
evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/TESTS/test_tenant_isolation.py
evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/app.py
evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/TESTS/test_tenant_isolation.py
evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/app.py
evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/TESTS/test_tenant_isolation.py
evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/FND/CODE_SCAFFOLD/app.py
evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/TESTS/test_tenant_isolation.py
evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/app.py
evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/TESTS/test_tenant_isolation.py
evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/FND/CODE_SCAFFOLD/app.py
evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/TESTS/test_tenant_isolation.py
evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/FND/CODE_SCAFFOLD/app.py
evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/TESTS/test_tenant_isolation.py
evidence_output/PETCARE-PH4-INPUTS/20260217T115438Z/snapshots/FND/CODE_SCAFFOLD/app.py
evidence_output/PETCARE-PH4-INPUTS/20260217T115438Z/snapshots/TESTS/test_tenant_isolation.py
evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/repo_snapshot/FND/CODE_SCAFFOLD/app.py
evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/repo_snapshot/TESTS/test_sqlite_store.py
evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/repo_snapshot/TESTS/test_tenant_isolation.py
evidence_output/PETCARE-PH6-CLOSURE/20260217T145345Z/repo_snapshot/FND/CODE_SCAFFOLD/app.py
evidence_output/PETCARE-PH6-CLOSURE/20260217T145345Z/repo_snapshot/TESTS/test_sqlite_governance.py
evidence_output/PETCARE-PH6-CLOSURE/20260217T145345Z/repo_snapshot/TESTS/test_sqlite_store.py
evidence_output/PETCARE-PH6-CLOSURE/20260217T145345Z/repo_snapshot/TESTS/test_tenant_isolation.py
evidence_output/PETCARE-PH6-INPUT-SNAPSHOT/20260217T144121Z/FND__CODE_SCAFFOLD__storage__export_bundle.py
evidence_output/PETCARE-PH6-INPUT-SNAPSHOT/20260217T144121Z/FND__CODE_SCAFFOLD__storage__sqlite_store.py
evidence_output/PETCARE-PH7-CLOSURE/20260217T190409Z/repo_snapshot/FND/CODE_SCAFFOLD/app.py
evidence_output/PETCARE-PH7-CLOSURE/20260217T190409Z/repo_snapshot/TESTS/test_sqlite_governance.py
evidence_output/PETCARE-PH7-CLOSURE/20260217T190409Z/repo_snapshot/TESTS/test_sqlite_store.py
evidence_output/PETCARE-PH7-CLOSURE/20260217T190409Z/repo_snapshot/TESTS/test_tenant_isolation.py
evidence_output/PETCARE-PH7-INPUT-SNAPSHOT/20260217T174838Z/FND__CODE_SCAFFOLD__storage__export_bundle.py
evidence_output/PETCARE-PH7-INPUT-SNAPSHOT/20260217T174838Z/FND__CODE_SCAFFOLD__storage__sqlite_store.py
```

## Grep Highlights (Routes/Auth/Audit/SQLite/Backup/Evidence)
```
./UI5/GOVERNANCE_EVIDENCE_POLICY.md:10:  - SCOPE.json tenant-scoped
./TESTS/UI5_TEST_CHECKLIST.md:13:- Verify UI6/ files in manifest
./TESTS/UI5_TEST_CHECKLIST.md:16:- Call /api/platform-admin/export/bundle
./scripts/petcare_land_pack.sh:32:echo "manifest: regenerate"
./scripts/petcare_land_pack.sh:33:PETCARE_ROOT="${ROOT}" "$PYBIN" "${ROOT}/scripts/_manifest_gen.py" >/dev/null
./scripts/petcare_land_pack.sh:34:echo "PASS manifest"
./scripts/petcare_land_pack.sh:75:echo "manifest_record True"
./UI5/TENANT_ISOLATION_POLICY.md:4:- Every API call must include x-tenant-id
./UI5/TENANT_ISOLATION_POLICY.md:5:- Storage keys are tenant-scoped logically (single-tenant store per request)
./UI5/TENANT_ISOLATION_POLICY.md:8:- Cross-tenant reads
./UI5/TENANT_ISOLATION_POLICY.md:9:- Cross-tenant listings without tenant scope
./UI5/TENANT_ISOLATION_POLICY.md:10:- Any implicit tenant context
./UI5/TENANT_ISOLATION_POLICY.md:14:- Export bundle must include deterministic manifest + hashes
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:5:repo_root=/Users/waheebmahmoud/dev/petcare-evidence-repository/petcare_execution
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:6:out=/Users/waheebmahmoud/dev/petcare-evidence-repository/petcare_execution/evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:7:zip=/Users/waheebmahmoud/dev/petcare-evidence-repository/petcare_execution/evidence_output/PETCARE-PH5-CLOSURE/PETCARE-PH5-CLOSURE_20260217T143204Z.zip
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:10:store_backend=sqlite
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:15:test_delete_audit_existed_flag (test_sqlite_store.TestSqliteStore) ... ok
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:16:test_export_items_stable (test_sqlite_store.TestSqliteStore) ... ok
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:17:test_list_keys_sorted_and_prefix (test_sqlite_store.TestSqliteStore) ... ok
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:18:test_put_get_persists_across_instances (test_sqlite_store.TestSqliteStore) ... ok
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:19:test_tenant_isolation_by_file (test_sqlite_store.TestSqliteStore) ... ok
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:20:test_bundle_deterministic_when_generated_at_fixed (test_tenant_isolation.TestExportBundleHardening) ... ok
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:21:test_bundle_requires_valid_tenant (test_tenant_isolation.TestExportBundleHardening) ... ok
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:22:test_bundle_schema_and_hashes_present (test_tenant_isolation.TestExportBundleHardening) ... ok
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:23:test_bundle_sorts_items_by_key (test_tenant_isolation.TestExportBundleHardening) ... ok
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:24:test_cross_tenant_read_blocked_by_scope (test_tenant_isolation.TestStorageIsolation) ... ok
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:25:test_delete_scoped (test_tenant_isolation.TestStorageIsolation) ... ok
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:26:test_export_items_scoped_and_sorted (test_tenant_isolation.TestStorageIsolation) ... ok
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:27:test_export_prefix_filter (test_tenant_isolation.TestStorageIsolation) ... ok
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:28:test_list_scoped (test_tenant_isolation.TestStorageIsolation) ... ok
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:29:test_put_get_same_tenant (test_tenant_isolation.TestStorageIsolation) ... ok
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:30:test_put_normalizes_tenant_lower (test_tenant_isolation.TestStorageIsolation) ... ok
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:31:test_put_requires_tenant (test_tenant_isolation.TestStorageIsolation) ... ok
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:32:test_put_requires_uuid_tenant (test_tenant_isolation.TestStorageIsolation) ... ok
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:33:test_empty (test_tenant_isolation.TestTenantHeaderValidation) ... ok
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:34:test_header_constant (test_tenant_isolation.TestTenantHeaderValidation) ... ok
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:35:test_invalid_uuid (test_tenant_isolation.TestTenantHeaderValidation) ... ok
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:36:test_missing (test_tenant_isolation.TestTenantHeaderValidation) ... ok
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:37:test_normalizes_lower (test_tenant_isolation.TestTenantHeaderValidation) ... ok
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:38:test_require_context_missing (test_tenant_isolation.TestTenantHeaderValidation) ... ok
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:39:test_require_context_ok (test_tenant_isolation.TestTenantHeaderValidation) ... ok
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:47:STEP 2: START API SERVER (uvicorn) [sqlite backend]
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:52:STEP 3: SMOKE [sqlite backend]
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:55:=== PUT missing tenant (expect error) ===
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:56:{"error":"x-tenant-id is required"}
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:57:=== PUT with tenant (expect ok) ===
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:59:=== GET with tenant (expect value v1) ===
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:61:=== EXPORT with tenant (expect bundle_sha256 present) ===
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:62:{"schema_version":"PH4_EXPORT_BUNDLE_V1","tenant_id":"11111111-1111-1111-1111-111111111111","generated_at":"20260217T143207Z","items":[{"key":"k1","value":"v1"}],"audit":[{"ts":"2026-02-17T14:31:19+00:00","action":"put","key":"k1","actor_id":"a"},{"ts":"2026-02-17T14:32:07+00:00","action":"put","key":"k1","actor_id":"a"}],"counts":{"items":1,"audit":2},"hashes":{"items_sha256":"43eb6d529f8c716e16b6312197dd5645cd17594a7d4af92ff3b11c289ec5e8be","audit_sha256":"bc6015e8dbd98d47d7316f387f7d23bcb39213e728d6a9909ed671ca381ace6c","bundle_sha256":"ec29fbb9f1ea3d8b297c4939f494c5043583a0a50e7c92ac38d7404854c4f057"}}
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:67:scripts/petcare_ph5_closure_pack.sh: line 107: 40161 Terminated: 15          PETCARE_STORE_BACKEND="sqlite" PORT="${SMOKE_PORT}" HOST="${HOST}" bash "scripts/run_api.sh" serve > "${SERVER_LOG}" 2>&1
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:72:root=/Users/waheebmahmoud/dev/petcare-evidence-repository/petcare_execution
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:75:manifest: regenerate
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:76:PASS manifest
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:80:manifest_record True
./evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/closure.log:91:ZIP=/Users/waheebmahmoud/dev/petcare-evidence-repository/petcare_execution/evidence_output/PETCARE-PH5-CLOSURE/PETCARE-PH5-CLOSURE_20260217T143204Z.zip
./UI5/SCOPE.md:4:Rebuild tenant isolation + governance controls and define deterministic verification checks.
./UI5/SCOPE.md:7:- Tenant boundary rules (must enforce x-tenant-id)
./UI5/SCOPE.md:8:- Cross-tenant read/write rejection rules
./UI5/SCOPE.md:10:- Evidence manifest expectations
./UI5/SCOPE.md:13:- External auth providers
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:8:/Users/waheebmahmoud/dev/petcare-evidence-repository/petcare_execution
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:12:145869c petcare: ignore venv + evidence outputs
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:25:evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/TESTS/UI5_TEST_CHECKLIST.md
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:26:evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/TESTS/ui5_deterministic_proof.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:27:evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/UI2/UI2_PACK_SUMMARY.md
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:28:evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/UI3/UI3_PACK_SUMMARY.md
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:29:evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/UI5/UI5_PACK_SUMMARY.md
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:30:evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/UI6/UI6_PACK_SUMMARY.md
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:31:evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/TESTS/UI5_TEST_CHECKLIST.md
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:32:evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/TESTS/ui5_deterministic_proof.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:33:evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/UI2/UI2_PACK_SUMMARY.md
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:34:evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/UI3/UI3_PACK_SUMMARY.md
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:35:evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/UI5/UI5_PACK_SUMMARY.md
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:36:evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/UI6/UI6_PACK_SUMMARY.md
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:37:evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/repo_snapshot/TESTS/UI5_TEST_CHECKLIST.md
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:38:evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/repo_snapshot/TESTS/ui5_deterministic_proof.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:39:evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/repo_snapshot/UI2/UI2_PACK_SUMMARY.md
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:40:evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/repo_snapshot/UI3/UI3_PACK_SUMMARY.md
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:41:evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/repo_snapshot/UI5/UI5_PACK_SUMMARY.md
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:42:evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/repo_snapshot/UI6/UI6_PACK_SUMMARY.md
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:43:evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/repo_snapshot/scripts/petcare_ph5_closure_pack.sh
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:44:evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/repo_snapshot/scripts/petcare_ph5_unittest.sh
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:45:evidence_output/PETCARE-PH5-CLOSURE/PETCARE-PH5-CLOSURE_20260217T143204Z.zip
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:46:evidence_output/PETCARE-PH5-CLOSURE/PETCARE-PH5-CLOSURE_20260217T143204Z.zip.sha256
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:47:evidence_output/PETCARE-PH6-CLOSURE/20260217T145345Z/repo_snapshot/TESTS/UI5_TEST_CHECKLIST.md
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:48:evidence_output/PETCARE-PH6-CLOSURE/20260217T145345Z/repo_snapshot/TESTS/ui5_deterministic_proof.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:49:evidence_output/PETCARE-PH6-CLOSURE/20260217T145345Z/repo_snapshot/UI2/UI2_PACK_SUMMARY.md
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:50:evidence_output/PETCARE-PH6-CLOSURE/20260217T145345Z/repo_snapshot/UI3/UI3_PACK_SUMMARY.md
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:51:evidence_output/PETCARE-PH6-CLOSURE/20260217T145345Z/repo_snapshot/UI5/UI5_PACK_SUMMARY.md
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:52:evidence_output/PETCARE-PH6-CLOSURE/20260217T145345Z/repo_snapshot/UI6/UI6_PACK_SUMMARY.md
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:53:evidence_output/PETCARE-PH6-CLOSURE/20260217T145345Z/repo_snapshot/scripts/petcare_ph5_closure_pack.sh
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:54:evidence_output/PETCARE-PH6-CLOSURE/20260217T145345Z/repo_snapshot/scripts/petcare_ph5_unittest.sh
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:55:evidence_output/PETCARE-PH6-INPUT-SNAPSHOT/20260217T144121Z/scripts__petcare_ph5_closure_pack.sh
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:56:evidence_output/PETCARE-PH7-CLOSURE/20260217T190409Z/repo_snapshot/TESTS/UI5_TEST_CHECKLIST.md
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:57:evidence_output/PETCARE-PH7-CLOSURE/20260217T190409Z/repo_snapshot/TESTS/ui5_deterministic_proof.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:58:evidence_output/PETCARE-PH7-CLOSURE/20260217T190409Z/repo_snapshot/UI2/UI2_PACK_SUMMARY.md
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:59:evidence_output/PETCARE-PH7-CLOSURE/20260217T190409Z/repo_snapshot/UI3/UI3_PACK_SUMMARY.md
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:60:evidence_output/PETCARE-PH7-CLOSURE/20260217T190409Z/repo_snapshot/UI5/UI5_PACK_SUMMARY.md
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:61:evidence_output/PETCARE-PH7-CLOSURE/20260217T190409Z/repo_snapshot/UI6/UI6_PACK_SUMMARY.md
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:62:evidence_output/PETCARE-PH7-CLOSURE/20260217T190409Z/repo_snapshot/scripts/petcare_ph5_closure_pack.sh
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:63:evidence_output/PETCARE-PH7-CLOSURE/20260217T190409Z/repo_snapshot/scripts/petcare_ph5_unittest.sh
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:64:evidence_output/PETCARE-PH7-INPUT-SNAPSHOT/20260217T174838Z/scripts__petcare_ph5_closure_pack.sh
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:65:evidence_output/_local_debug_ph5_closure_20260217T142018Z.log
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:79:.venv/lib/python3.9/site-packages/fastapi/security/oauth2.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:82:.venv/lib/python3.9/site-packages/starlette/authentication.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:83:.venv/lib/python3.9/site-packages/starlette/middleware/authentication.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:85:FND/CODE_SCAFFOLD/api/routes_platform_admin.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:87:FND/CODE_SCAFFOLD/storage/export_bundle.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:88:FND/CODE_SCAFFOLD/storage/sqlite_lifecycle.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:89:FND/CODE_SCAFFOLD/storage/sqlite_store.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:90:TESTS/test_sqlite_governance.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:91:TESTS/test_sqlite_store.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:92:TESTS/test_tenant_isolation.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:93:evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/app.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:94:evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/TESTS/test_tenant_isolation.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:95:evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/app.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:96:evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/TESTS/test_tenant_isolation.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:97:evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/app.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:98:evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/TESTS/test_tenant_isolation.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:99:evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/app.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:100:evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/TESTS/test_tenant_isolation.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:101:evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/FND/CODE_SCAFFOLD/app.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:102:evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/TESTS/test_tenant_isolation.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:103:evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/app.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:104:evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/TESTS/test_tenant_isolation.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:105:evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/FND/CODE_SCAFFOLD/app.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:106:evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/TESTS/test_tenant_isolation.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:107:evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/FND/CODE_SCAFFOLD/app.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:108:evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/TESTS/test_tenant_isolation.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:109:evidence_output/PETCARE-PH4-INPUTS/20260217T115438Z/snapshots/FND/CODE_SCAFFOLD/app.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:110:evidence_output/PETCARE-PH4-INPUTS/20260217T115438Z/snapshots/TESTS/test_tenant_isolation.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:111:evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/repo_snapshot/FND/CODE_SCAFFOLD/app.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:112:evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/repo_snapshot/TESTS/test_sqlite_store.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:113:evidence_output/PETCARE-PH5-CLOSURE/20260217T143204Z/repo_snapshot/TESTS/test_tenant_isolation.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:114:evidence_output/PETCARE-PH6-CLOSURE/20260217T145345Z/repo_snapshot/FND/CODE_SCAFFOLD/app.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:115:evidence_output/PETCARE-PH6-CLOSURE/20260217T145345Z/repo_snapshot/TESTS/test_sqlite_governance.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:116:evidence_output/PETCARE-PH6-CLOSURE/20260217T145345Z/repo_snapshot/TESTS/test_sqlite_store.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:117:evidence_output/PETCARE-PH6-CLOSURE/20260217T145345Z/repo_snapshot/TESTS/test_tenant_isolation.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:118:evidence_output/PETCARE-PH6-INPUT-SNAPSHOT/20260217T144121Z/FND__CODE_SCAFFOLD__storage__export_bundle.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:119:evidence_output/PETCARE-PH6-INPUT-SNAPSHOT/20260217T144121Z/FND__CODE_SCAFFOLD__storage__sqlite_store.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:120:evidence_output/PETCARE-PH7-CLOSURE/20260217T190409Z/repo_snapshot/FND/CODE_SCAFFOLD/app.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:121:evidence_output/PETCARE-PH7-CLOSURE/20260217T190409Z/repo_snapshot/TESTS/test_sqlite_governance.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:122:evidence_output/PETCARE-PH7-CLOSURE/20260217T190409Z/repo_snapshot/TESTS/test_sqlite_store.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:123:evidence_output/PETCARE-PH7-CLOSURE/20260217T190409Z/repo_snapshot/TESTS/test_tenant_isolation.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:124:evidence_output/PETCARE-PH7-INPUT-SNAPSHOT/20260217T174838Z/FND__CODE_SCAFFOLD__storage__export_bundle.py
./evidence_output/PETCARE-PH8-PREFLIGHT/20260218T202149Z/PH5_ARCHITECTURE_SCAN.md:125:evidence_output/PETCARE-PH7-INPUT-SNAPSHOT/20260217T174838Z/FND__CODE_SCAFFOLD__storage__sqlite_store.py
./UI5/NEGATIVE_CASES.md:3:## NC-1 Missing tenant header
./UI5/NEGATIVE_CASES.md:6:## NC-2 Attempt export without tenant header
./UI5/NEGATIVE_CASES.md:16:- Re-run export with same dataset -> stable ordering rules must hold
./TESTS/test_sqlite_store.py:6:from FND.CODE_SCAFFOLD.storage.sqlite_store import SqliteStore
./TESTS/test_sqlite_store.py:17:            s1.put(tenant_id=TENANT_A, key="k1", value={"a": 1}, actor_id="u1")
./TESTS/test_sqlite_store.py:20:            v = s2.get(tenant_id=TENANT_A, key="k1")
./TESTS/test_sqlite_store.py:23:    def test_tenant_isolation_by_file(self):
./TESTS/test_sqlite_store.py:26:            s.put(tenant_id=TENANT_A, key="shared", value="A", actor_id="u1")
./TESTS/test_sqlite_store.py:27:            s.put(tenant_id=TENANT_B, key="shared", value="B", actor_id="u1")
./TESTS/test_sqlite_store.py:29:            self.assertEqual(s.get(tenant_id=TENANT_A, key="shared"), "A")
./TESTS/test_sqlite_store.py:30:            self.assertEqual(s.get(tenant_id=TENANT_B, key="shared"), "B")
./TESTS/test_sqlite_store.py:35:            s.put(tenant_id=TENANT_A, key="b/2", value=2, actor_id="u1")
./TESTS/test_sqlite_store.py:36:            s.put(tenant_id=TENANT_A, key="a/1", value=1, actor_id="u1")
./TESTS/test_sqlite_store.py:37:            s.put(tenant_id=TENANT_A, key="a/2", value=2, actor_id="u1")
./TESTS/test_sqlite_store.py:39:            self.assertEqual(s.list_keys(tenant_id=TENANT_A), ["a/1", "a/2", "b/2"])
./TESTS/test_sqlite_store.py:40:            self.assertEqual(s.list_keys(tenant_id=TENANT_A, prefix="a/"), ["a/1", "a/2"])
./TESTS/test_sqlite_store.py:42:    def test_delete_audit_existed_flag(self):
./TESTS/test_sqlite_store.py:45:            s.put(tenant_id=TENANT_A, key="k", value=1, actor_id="u1")
./TESTS/test_sqlite_store.py:47:            existed_true = s.delete(tenant_id=TENANT_A, key="k", actor_id="u2")
./TESTS/test_sqlite_store.py:48:            existed_false = s.delete(tenant_id=TENANT_A, key="k", actor_id="u3")
./TESTS/test_sqlite_store.py:53:            audit = s.audit_log(tenant_id=TENANT_A)
./TESTS/test_sqlite_store.py:54:            deletes = [e for e in audit if e.get("action") == "delete"]
./TESTS/test_sqlite_store.py:59:    def test_export_items_stable(self):
./TESTS/test_sqlite_store.py:62:            s.put(tenant_id=TENANT_A, key="b", value=2, actor_id="u1")
./TESTS/test_sqlite_store.py:63:            s.put(tenant_id=TENANT_A, key="a", value=1, actor_id="u1")
./TESTS/test_sqlite_store.py:64:            items = s.export_items(tenant_id=TENANT_A)
./UI3/JOURNEYS.md:3:All journeys are tenant-scoped.
./UI3/JOURNEYS.md:26:1) Call export bundle endpoint
./UI3/JOURNEYS.md:27:2) Bundle created under EVIDENCE/exports/{tenant_id}_{timestamp}
./EVIDENCE/MANIFEST.json:16:      "path": "BACKUP_FIX_LAND_20260216T202208Z/scripts/_manifest_gen.py",
./EVIDENCE/MANIFEST.json:31:      "path": "FND/CODE_SCAFFOLD/api/routes_platform_admin.py",
./EVIDENCE/MANIFEST.json:56:      "path": "FND/CODE_SCAFFOLD/storage/export_bundle.py",
./EVIDENCE/MANIFEST.json:71:      "path": "FND/CODE_SCAFFOLD/storage/sqlite_lifecycle.py",
./EVIDENCE/MANIFEST.json:76:      "path": "FND/CODE_SCAFFOLD/storage/sqlite_store.py",
./EVIDENCE/MANIFEST.json:81:      "path": "FND/CODE_SCAFFOLD/tenant_isolation_guard.py",
./EVIDENCE/MANIFEST.json:106:      "path": "TESTS/test_sqlite_governance.py",
./EVIDENCE/MANIFEST.json:111:      "path": "TESTS/test_sqlite_store.py",
./EVIDENCE/MANIFEST.json:116:      "path": "TESTS/test_tenant_isolation.py",
./EVIDENCE/MANIFEST.json:226:      "path": "data/tenants/11111111-1111-1111-1111-111111111111.sqlite",
./EVIDENCE/MANIFEST.json:231:      "path": "data/tenants/11111111-1111-1111-1111-111111111111.sqlite-shm",
./EVIDENCE/MANIFEST.json:236:      "path": "data/tenants/11111111-1111-1111-1111-111111111111.sqlite-wal",
./EVIDENCE/MANIFEST.json:241:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/MANIFEST.json",
./EVIDENCE/MANIFEST.json:246:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/allowed_touch_files.txt",
./EVIDENCE/MANIFEST.json:251:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/repo_files_sha256.txt",
./EVIDENCE/MANIFEST.json:256:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/app.py",
./EVIDENCE/MANIFEST.json:261:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/interfaces/storage_interface.py",
./EVIDENCE/MANIFEST.json:266:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/storage/export_bundle.py",
./EVIDENCE/MANIFEST.json:271:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py",
./EVIDENCE/MANIFEST.json:276:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py",
./EVIDENCE/MANIFEST.json:281:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/TESTS/test_tenant_isolation.py",
./EVIDENCE/MANIFEST.json:286:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/requirements.txt",
./EVIDENCE/MANIFEST.json:291:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/scripts/run_api.sh",
./EVIDENCE/MANIFEST.json:296:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/MANIFEST.json",
./EVIDENCE/MANIFEST.json:301:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/allowed_touch_files.txt",
./EVIDENCE/MANIFEST.json:306:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/repo_files_sha256.txt",
./EVIDENCE/MANIFEST.json:311:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/app.py",
./EVIDENCE/MANIFEST.json:316:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/interfaces/storage_interface.py",
./EVIDENCE/MANIFEST.json:321:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/storage/export_bundle.py",
./EVIDENCE/MANIFEST.json:326:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py",
./EVIDENCE/MANIFEST.json:331:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py",
./EVIDENCE/MANIFEST.json:336:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/TESTS/test_tenant_isolation.py",
./EVIDENCE/MANIFEST.json:341:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/requirements.txt",
./EVIDENCE/MANIFEST.json:346:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/scripts/run_api.sh",
./EVIDENCE/MANIFEST.json:351:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/PETCARE-EMERGENT-HANDOFF_20260217T091134Z.zip",
./EVIDENCE/MANIFEST.json:356:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/PETCARE-EMERGENT-HANDOFF_20260217T091134Z.zip.sha256",
./EVIDENCE/MANIFEST.json:361:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/PETCARE-EMERGENT-HANDOFF_20260217T091428Z.zip",
./EVIDENCE/MANIFEST.json:366:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/PETCARE-EMERGENT-HANDOFF_20260217T091428Z.zip.sha256",
./EVIDENCE/MANIFEST.json:371:      "path": "evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/closure_sha256.txt",
./EVIDENCE/MANIFEST.json:376:      "path": "evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/petcare_land_pack_phase2.log",
./EVIDENCE/MANIFEST.json:381:      "path": "evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/EVIDENCE/MANIFEST.json",
./EVIDENCE/MANIFEST.json:386:      "path": "evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/app.py",
./EVIDENCE/MANIFEST.json:391:      "path": "evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/interfaces/storage_interface.py",
./EVIDENCE/MANIFEST.json:396:      "path": "evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/storage/export_bundle.py",
./EVIDENCE/MANIFEST.json:401:      "path": "evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py",
./EVIDENCE/MANIFEST.json:406:      "path": "evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py",
./EVIDENCE/MANIFEST.json:411:      "path": "evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/TESTS/test_tenant_isolation.py",
./EVIDENCE/MANIFEST.json:416:      "path": "evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/unittest_phase2.log",
./EVIDENCE/MANIFEST.json:421:      "path": "evidence_output/PETCARE-PH2-CLOSURE/PETCARE-PH2-CLOSURE_20260217T085354Z.zip",
./EVIDENCE/MANIFEST.json:426:      "path": "evidence_output/PETCARE-PH2-CLOSURE/PETCARE-PH2-CLOSURE_20260217T085354Z.zip.sha256",
./EVIDENCE/MANIFEST.json:431:      "path": "evidence_output/PETCARE-PH2-INPUTS/20260217T081959Z/repo_file_count.txt",
./EVIDENCE/MANIFEST.json:436:      "path": "evidence_output/PETCARE-PH2-INPUTS/20260217T081959Z/repo_files_sha256.txt",
./EVIDENCE/MANIFEST.json:441:      "path": "evidence_output/PETCARE-PH2-INPUTS/20260217T081959Z/tenant_storage_grep.txt",
./EVIDENCE/MANIFEST.json:446:      "path": "evidence_output/PETCARE-PH2-INPUTS/PETCARE-PH2-INPUTS_20260217T081959Z.zip",
./EVIDENCE/MANIFEST.json:451:      "path": "evidence_output/PETCARE-PH2-INPUTS/PETCARE-PH2-INPUTS_20260217T081959Z.zip.sha256",
./EVIDENCE/MANIFEST.json:456:      "path": "evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/closure_files.txt",
./EVIDENCE/MANIFEST.json:461:      "path": "evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/closure_sha256.txt",
./EVIDENCE/MANIFEST.json:466:      "path": "evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/land_pack.log",
./EVIDENCE/MANIFEST.json:471:      "path": "evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/smoke.log",
./EVIDENCE/MANIFEST.json:476:      "path": "evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/EVIDENCE/MANIFEST.json",
./EVIDENCE/MANIFEST.json:481:      "path": "evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/app.py",
./EVIDENCE/MANIFEST.json:486:      "path": "evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/interfaces/storage_interface.py",
./EVIDENCE/MANIFEST.json:491:      "path": "evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/storage/export_bundle.py",
./EVIDENCE/MANIFEST.json:496:      "path": "evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py",
./EVIDENCE/MANIFEST.json:501:      "path": "evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py",
./EVIDENCE/MANIFEST.json:506:      "path": "evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/TESTS/test_tenant_isolation.py",
./EVIDENCE/MANIFEST.json:511:      "path": "evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/requirements.txt",
./EVIDENCE/MANIFEST.json:516:      "path": "evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/scripts/run_api.sh",
./EVIDENCE/MANIFEST.json:521:      "path": "evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/unittest.log",
./EVIDENCE/MANIFEST.json:526:      "path": "evidence_output/PETCARE-PH3-P1-CLOSURE/PETCARE-PH3-P1-CLOSURE_20260217T104807Z.zip",
./EVIDENCE/MANIFEST.json:531:      "path": "evidence_output/PETCARE-PH3-P1-CLOSURE/PETCARE-PH3-P1-CLOSURE_20260217T104807Z.zip.sha256",
./EVIDENCE/MANIFEST.json:536:      "path": "evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/closure_files.txt",
./EVIDENCE/MANIFEST.json:541:      "path": "evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/closure_sha256.txt",
./EVIDENCE/MANIFEST.json:546:      "path": "evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/land_pack.log",
./EVIDENCE/MANIFEST.json:551:      "path": "evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/smoke.log",
./EVIDENCE/MANIFEST.json:556:      "path": "evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/EVIDENCE/MANIFEST.json",
./EVIDENCE/MANIFEST.json:561:      "path": "evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/FND/CODE_SCAFFOLD/app.py",
./EVIDENCE/MANIFEST.json:566:      "path": "evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py",
./EVIDENCE/MANIFEST.json:571:      "path": "evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/TESTS/test_tenant_isolation.py",
./EVIDENCE/MANIFEST.json:576:      "path": "evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/requirements.txt",
./EVIDENCE/MANIFEST.json:581:      "path": "evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/scripts/run_api.sh",
./EVIDENCE/MANIFEST.json:586:      "path": "evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/unittest.log",
./EVIDENCE/MANIFEST.json:591:      "path": "evidence_output/PETCARE-PH3-P2-CLOSURE/PETCARE-PH3-P2-CLOSURE_20260217T112255Z.zip",
./EVIDENCE/MANIFEST.json:596:      "path": "evidence_output/PETCARE-PH3-P2-CLOSURE/PETCARE-PH3-P2-CLOSURE_20260217T112255Z.zip.sha256",
./EVIDENCE/MANIFEST.json:601:      "path": "evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/closure_files.txt",
./EVIDENCE/MANIFEST.json:606:      "path": "evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/closure_sha256.txt",
./EVIDENCE/MANIFEST.json:611:      "path": "evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/land_pack.log",
./EVIDENCE/MANIFEST.json:616:      "path": "evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/smoke.log",
./EVIDENCE/MANIFEST.json:621:      "path": "evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/EVIDENCE/MANIFEST.json",
./EVIDENCE/MANIFEST.json:626:      "path": "evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/app.py",
./EVIDENCE/MANIFEST.json:631:      "path": "evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py",
./EVIDENCE/MANIFEST.json:636:      "path": "evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py",
./EVIDENCE/MANIFEST.json:641:      "path": "evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/TESTS/test_tenant_isolation.py",
./EVIDENCE/MANIFEST.json:646:      "path": "evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/scripts/run_api.sh",
./EVIDENCE/MANIFEST.json:651:      "path": "evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/unittest.log",
./EVIDENCE/MANIFEST.json:656:      "path": "evidence_output/PETCARE-PH3-P3-CLOSURE/PETCARE-PH3-P3-CLOSURE_20260217T113820Z.zip",
./EVIDENCE/MANIFEST.json:661:      "path": "evidence_output/PETCARE-PH3-P3-CLOSURE/PETCARE-PH3-P3-CLOSURE_20260217T113820Z.zip.sha256",
./EVIDENCE/MANIFEST.json:666:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/closure.log",
./EVIDENCE/MANIFEST.json:671:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/health_poll.log",
./EVIDENCE/MANIFEST.json:676:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/land_pack.log",
./EVIDENCE/MANIFEST.json:681:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/.gitignore",
./EVIDENCE/MANIFEST.json:686:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/BACKUP_BASELINE_20260216T203805Z.tgz",
./EVIDENCE/MANIFEST.json:691:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/BACKUP_FIX_LAND_20260216T202208Z/scripts/_manifest_gen.py",
./EVIDENCE/MANIFEST.json:696:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/BACKUP_FIX_LAND_20260216T202208Z/scripts/petcare_land_pack.sh",
./EVIDENCE/MANIFEST.json:701:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/EVIDENCE/MANIFEST.json",
./EVIDENCE/MANIFEST.json:706:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/FND/CODE_SCAFFOLD/api/routes_platform_admin.py",
./EVIDENCE/MANIFEST.json:711:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/FND/CODE_SCAFFOLD/app.py",
./EVIDENCE/MANIFEST.json:716:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/FND/CODE_SCAFFOLD/interfaces/init.py",
./EVIDENCE/MANIFEST.json:721:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/FND/CODE_SCAFFOLD/interfaces/storage_interface.py",
./EVIDENCE/MANIFEST.json:726:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/FND/CODE_SCAFFOLD/storage/export_bundle.py",
./EVIDENCE/MANIFEST.json:731:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/FND/CODE_SCAFFOLD/storage/init.py",
./EVIDENCE/MANIFEST.json:736:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/FND/CODE_SCAFFOLD/storage/memory_store.py",
./EVIDENCE/MANIFEST.json:741:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/FND/CODE_SCAFFOLD/tenant_isolation_guard.py",
./EVIDENCE/MANIFEST.json:746:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/FND/__init__.py",
./EVIDENCE/MANIFEST.json:751:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/TESTS/TEST_PLAN.md",
./EVIDENCE/MANIFEST.json:756:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/TESTS/UI5_TEST_CHECKLIST.md",
./EVIDENCE/MANIFEST.json:761:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/TESTS/__init__.py",
./EVIDENCE/MANIFEST.json:766:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/TESTS/test_tenant_isolation.py",
./EVIDENCE/MANIFEST.json:771:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/TESTS/ui5_deterministic_proof.py",
./EVIDENCE/MANIFEST.json:776:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/UI2/ACCEPTANCE_CHECKS.md",
./EVIDENCE/MANIFEST.json:781:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/UI2/API_SURFACE.md",
./EVIDENCE/MANIFEST.json:786:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/UI2/DOMAIN_MODEL.md",
./EVIDENCE/MANIFEST.json:791:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/UI2/SCOPE.md",
./EVIDENCE/MANIFEST.json:796:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/UI2/UI2_PACK_SUMMARY.md",
./EVIDENCE/MANIFEST.json:801:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/UI3/ERROR_STATES.md",
./EVIDENCE/MANIFEST.json:806:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/UI3/FLOWS.md",
./EVIDENCE/MANIFEST.json:811:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/UI3/JOURNEYS.md",
./EVIDENCE/MANIFEST.json:816:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/UI3/SCOPE.md",
./EVIDENCE/MANIFEST.json:821:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/UI3/UI3_PACK_SUMMARY.md",
./EVIDENCE/MANIFEST.json:826:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/UI5/GOVERNANCE_EVIDENCE_POLICY.md",
./EVIDENCE/MANIFEST.json:831:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/UI5/NEGATIVE_CASES.md",
./EVIDENCE/MANIFEST.json:836:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/UI5/SCOPE.md",
./EVIDENCE/MANIFEST.json:841:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/UI5/TENANT_ISOLATION_POLICY.md",
./EVIDENCE/MANIFEST.json:846:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/UI5/UI5_PACK_SUMMARY.md",
./EVIDENCE/MANIFEST.json:851:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/UI6/DAL_CONTRACT.md",
./EVIDENCE/MANIFEST.json:856:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/UI6/EVIDENCE_EXPORT_BUNDLE_SPEC.md",
./EVIDENCE/MANIFEST.json:861:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/UI6/NEGATIVE_CASES_UI6.md",
./EVIDENCE/MANIFEST.json:866:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/UI6/TENANT_BOUND_STORAGE_MODEL.md",
./EVIDENCE/MANIFEST.json:871:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/UI6/UI6_PACK_SUMMARY.md",
./EVIDENCE/MANIFEST.json:876:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/requirements.txt",
./EVIDENCE/MANIFEST.json:881:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/scripts/_manifest_gen.py",
./EVIDENCE/MANIFEST.json:886:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/scripts/petcare_land_pack.sh",
./EVIDENCE/MANIFEST.json:891:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/scripts/petcare_ph4_closure_pack.sh",
./EVIDENCE/MANIFEST.json:896:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/scripts/petcare_ph4_discovery_pack.sh",
./EVIDENCE/MANIFEST.json:901:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/scripts/petcare_ph4_git_hardening.sh",
./EVIDENCE/MANIFEST.json:906:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/scripts/petcare_ph4_inputs_pack.sh",
./EVIDENCE/MANIFEST.json:911:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/scripts/petcare_ph4_unittest.sh",
./EVIDENCE/MANIFEST.json:916:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/repo_snapshot/scripts/run_api.sh",
./EVIDENCE/MANIFEST.json:921:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/smoke.log",
./EVIDENCE/MANIFEST.json:926:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/unittest.log",
./EVIDENCE/MANIFEST.json:931:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/uvicorn.log",
./EVIDENCE/MANIFEST.json:936:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T133616Z/uvicorn.pid",
./EVIDENCE/MANIFEST.json:941:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/MANIFEST.json",
./EVIDENCE/MANIFEST.json:946:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/closure.log",
./EVIDENCE/MANIFEST.json:951:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/health_poll.log",
./EVIDENCE/MANIFEST.json:956:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/land_pack.log",
./EVIDENCE/MANIFEST.json:961:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/.gitignore",
./EVIDENCE/MANIFEST.json:966:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/BACKUP_BASELINE_20260216T203805Z.tgz",
./EVIDENCE/MANIFEST.json:971:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/BACKUP_FIX_LAND_20260216T202208Z/scripts/_manifest_gen.py",
./EVIDENCE/MANIFEST.json:976:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/BACKUP_FIX_LAND_20260216T202208Z/scripts/petcare_land_pack.sh",
./EVIDENCE/MANIFEST.json:981:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/EVIDENCE/MANIFEST.json",
./EVIDENCE/MANIFEST.json:986:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/FND/CODE_SCAFFOLD/api/routes_platform_admin.py",
./EVIDENCE/MANIFEST.json:991:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/FND/CODE_SCAFFOLD/app.py",
./EVIDENCE/MANIFEST.json:996:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/FND/CODE_SCAFFOLD/interfaces/init.py",
./EVIDENCE/MANIFEST.json:1001:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/FND/CODE_SCAFFOLD/interfaces/storage_interface.py",
./EVIDENCE/MANIFEST.json:1006:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/FND/CODE_SCAFFOLD/storage/export_bundle.py",
./EVIDENCE/MANIFEST.json:1011:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/FND/CODE_SCAFFOLD/storage/init.py",
./EVIDENCE/MANIFEST.json:1016:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/FND/CODE_SCAFFOLD/storage/memory_store.py",
./EVIDENCE/MANIFEST.json:1021:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/FND/CODE_SCAFFOLD/tenant_isolation_guard.py",
./EVIDENCE/MANIFEST.json:1026:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/FND/__init__.py",
./EVIDENCE/MANIFEST.json:1031:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/TESTS/TEST_PLAN.md",
./EVIDENCE/MANIFEST.json:1036:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/TESTS/UI5_TEST_CHECKLIST.md",
./EVIDENCE/MANIFEST.json:1041:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/TESTS/__init__.py",
./EVIDENCE/MANIFEST.json:1046:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/TESTS/test_tenant_isolation.py",
./EVIDENCE/MANIFEST.json:1051:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/TESTS/ui5_deterministic_proof.py",
./EVIDENCE/MANIFEST.json:1056:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/UI2/ACCEPTANCE_CHECKS.md",
./EVIDENCE/MANIFEST.json:1061:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/UI2/API_SURFACE.md",
./EVIDENCE/MANIFEST.json:1066:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/UI2/DOMAIN_MODEL.md",
./EVIDENCE/MANIFEST.json:1071:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/UI2/SCOPE.md",
./EVIDENCE/MANIFEST.json:1076:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/UI2/UI2_PACK_SUMMARY.md",
./EVIDENCE/MANIFEST.json:1081:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/UI3/ERROR_STATES.md",
./EVIDENCE/MANIFEST.json:1086:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/UI3/FLOWS.md",
./EVIDENCE/MANIFEST.json:1091:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/UI3/JOURNEYS.md",
./EVIDENCE/MANIFEST.json:1096:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/UI3/SCOPE.md",
./EVIDENCE/MANIFEST.json:1101:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/UI3/UI3_PACK_SUMMARY.md",
./EVIDENCE/MANIFEST.json:1106:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/UI5/GOVERNANCE_EVIDENCE_POLICY.md",
./EVIDENCE/MANIFEST.json:1111:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/UI5/NEGATIVE_CASES.md",
./EVIDENCE/MANIFEST.json:1116:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/UI5/SCOPE.md",
./EVIDENCE/MANIFEST.json:1121:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/UI5/TENANT_ISOLATION_POLICY.md",
./EVIDENCE/MANIFEST.json:1126:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/UI5/UI5_PACK_SUMMARY.md",
./EVIDENCE/MANIFEST.json:1131:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/UI6/DAL_CONTRACT.md",
./EVIDENCE/MANIFEST.json:1136:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/UI6/EVIDENCE_EXPORT_BUNDLE_SPEC.md",
./EVIDENCE/MANIFEST.json:1141:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/UI6/NEGATIVE_CASES_UI6.md",
./EVIDENCE/MANIFEST.json:1146:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/UI6/TENANT_BOUND_STORAGE_MODEL.md",
./EVIDENCE/MANIFEST.json:1151:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/UI6/UI6_PACK_SUMMARY.md",
./EVIDENCE/MANIFEST.json:1156:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/requirements.txt",
./EVIDENCE/MANIFEST.json:1161:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/scripts/_manifest_gen.py",
./EVIDENCE/MANIFEST.json:1166:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/scripts/petcare_land_pack.sh",
./EVIDENCE/MANIFEST.json:1171:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/scripts/petcare_ph4_closure_pack.sh",
./EVIDENCE/MANIFEST.json:1176:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/scripts/petcare_ph4_discovery_pack.sh",
./EVIDENCE/MANIFEST.json:1181:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/scripts/petcare_ph4_git_hardening.sh",
./EVIDENCE/MANIFEST.json:1186:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/scripts/petcare_ph4_inputs_pack.sh",
./EVIDENCE/MANIFEST.json:1191:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/scripts/petcare_ph4_unittest.sh",
./EVIDENCE/MANIFEST.json:1196:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/repo_snapshot/scripts/run_api.sh",
./EVIDENCE/MANIFEST.json:1201:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/smoke.log",
./EVIDENCE/MANIFEST.json:1206:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/unittest.log",
./EVIDENCE/MANIFEST.json:1211:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/uvicorn.log",
./EVIDENCE/MANIFEST.json:1216:      "path": "evidence_output/PETCARE-PH4-CLOSURE/20260217T134016Z/uvicorn.pid",
./EVIDENCE/MANIFEST.json:1221:      "path": "evidence_output/PETCARE-PH4-CLOSURE/PETCARE-PH4-CLOSURE_20260217T134016Z.zip",
./EVIDENCE/MANIFEST.json:1226:      "path": "evidence_output/PETCARE-PH4-CLOSURE/PETCARE-PH4-CLOSURE_20260217T134016Z.zip.sha256",
./EVIDENCE/MANIFEST.json:1231:      "path": "evidence_output/PETCARE-PH4-DISCOVERY/20260217T114627Z/DISCOVERY_REPORT.md",
./EVIDENCE/MANIFEST.json:1236:      "path": "evidence_output/PETCARE-PH4-DISCOVERY/20260217T114627Z/LOGS.txt",
./EVIDENCE/MANIFEST.json:1241:      "path": "evidence_output/PETCARE-PH4-DISCOVERY/20260217T114922Z/DISCOVERY_REPORT.md",
./EVIDENCE/MANIFEST.json:1246:      "path": "evidence_output/PETCARE-PH4-DISCOVERY/20260217T114922Z/LOGS.txt",
./EVIDENCE/MANIFEST.json:1251:      "path": "evidence_output/PETCARE-PH4-DISCOVERY/20260217T114922Z/MANIFEST.json",
./EVIDENCE/MANIFEST.json:1256:      "path": "evidence_output/PETCARE-PH4-DISCOVERY/PETCARE-PH4-DISCOVERY_20260217T114922Z.zip",
./EVIDENCE/MANIFEST.json:1261:      "path": "evidence_output/PETCARE-PH4-DISCOVERY/PETCARE-PH4-DISCOVERY_20260217T114922Z.zip.sha256",
./EVIDENCE/MANIFEST.json:1266:      "path": "evidence_output/PETCARE-PH4-INPUTS/20260217T115438Z/PH4_INPUTS_REPORT.md",
./EVIDENCE/MANIFEST.json:1271:      "path": "evidence_output/PETCARE-PH4-INPUTS/20260217T115438Z/SNAPSHOT_BODIES.txt",
./EVIDENCE/MANIFEST.json:1276:      "path": "evidence_output/PETCARE-PH4-INPUTS/20260217T115438Z/snapshots/FND/CODE_SCAFFOLD/app.py",
./EVIDENCE/MANIFEST.json:1281:      "path": "evidence_output/PETCARE-PH4-INPUTS/20260217T115438Z/snapshots/FND/CODE_SCAFFOLD/interfaces/storage_interface.py",
./EVIDENCE/MANIFEST.json:1286:      "path": "evidence_output/PETCARE-PH4-INPUTS/20260217T115438Z/snapshots/FND/CODE_SCAFFOLD/storage/export_bundle.py",
./EVIDENCE/MANIFEST.json:1291:      "path": "evidence_output/PETCARE-PH4-INPUTS/20260217T115438Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py",
./EVIDENCE/MANIFEST.json:1296:      "path": "evidence_output/PETCARE-PH4-INPUTS/20260217T115438Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py",
```

