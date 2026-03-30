# PETCARE PH4 DISCOVERY PACK

- timestamp_utc: 20260217T114922Z
- root: /Users/waheebmahmoud/dev/petcare-evidence-repository/petcare_execution

## Git

```

git status -sb
## main...origin/main
?? ./

git log -1 --oneline
7768a6c Sprint 6 Day-3: refresh evidence bundle index after security addendum
```
## Repo shape

```

ls -la
total 16
drwxr-xr-x  17 waheebmahmoud  staff   544 Feb 17 12:02 .
drwxr-xr-x  10 waheebmahmoud  staff   320 Feb 16 22:57 ..
drwxr-xr-x   6 waheebmahmoud  staff   192 Feb 17 12:01 .venv
drwxr-xr-x   2 waheebmahmoud  staff    64 Feb 16 23:38 BACKUP_BASELINE_20260216T203805Z
-rw-r--r--   1 waheebmahmoud  staff  3647 Feb 16 23:38 BACKUP_BASELINE_20260216T203805Z.tgz
drwxr-xr-x   3 waheebmahmoud  staff    96 Feb 16 23:22 BACKUP_FIX_LAND_20260216T202208Z
drwxr-xr-x   2 waheebmahmoud  staff    64 Feb 16 23:06 BACKUP_REGEN_SCRIPTS_20260216T200631Z
drwxr-xr-x   3 waheebmahmoud  staff    96 Feb 16 23:33 EVIDENCE
drwxr-xr-x   4 waheebmahmoud  staff   128 Feb 17 00:00 FND
drwxr-xr-x   6 waheebmahmoud  staff   192 Feb 17 11:48 TESTS
drwxr-xr-x   7 waheebmahmoud  staff   224 Feb 16 23:42 UI2
drwxr-xr-x   7 waheebmahmoud  staff   224 Feb 16 23:46 UI3
drwxr-xr-x   7 waheebmahmoud  staff   224 Feb 16 23:49 UI5
drwxr-xr-x   7 waheebmahmoud  staff   224 Feb 16 22:57 UI6
drwxr-xr-x   9 waheebmahmoud  staff   288 Feb 17 14:46 evidence_output
-rw-r--r--   1 waheebmahmoud  staff   236 Feb 17 12:02 requirements.txt
drwxr-xr-x   6 waheebmahmoud  staff   192 Feb 17 14:46 scripts

find scripts -maxdepth 2 -type f -print | sort
scripts/_manifest_gen.py
scripts/petcare_land_pack.sh
scripts/petcare_ph4_discovery_pack.sh
scripts/run_api.sh

find . -maxdepth 3 -type f \( -name '*.py' -o -name '*.md' -o -name '*.json' \) -print | wc -l | tr -d ' ' | awk '{print "tracked_like_filecount="$1}'
tracked_like_filecount=30
```
## Evidence outputs present

```

ls -la evidence_output || true
total 0
drwxr-xr-x   9 waheebmahmoud  staff  288 Feb 17 14:46 .
drwxr-xr-x  17 waheebmahmoud  staff  544 Feb 17 12:02 ..
drwxr-xr-x   8 waheebmahmoud  staff  256 Feb 17 12:14 PETCARE-EMERGENT-HANDOFF
drwxr-xr-x   5 waheebmahmoud  staff  160 Feb 17 11:55 PETCARE-PH2-CLOSURE
drwxr-xr-x   5 waheebmahmoud  staff  160 Feb 17 11:19 PETCARE-PH2-INPUTS
drwxr-xr-x   5 waheebmahmoud  staff  160 Feb 17 13:48 PETCARE-PH3-P1-CLOSURE
drwxr-xr-x   5 waheebmahmoud  staff  160 Feb 17 14:22 PETCARE-PH3-P2-CLOSURE
drwxr-xr-x   5 waheebmahmoud  staff  160 Feb 17 14:38 PETCARE-PH3-P3-CLOSURE
drwxr-xr-x   4 waheebmahmoud  staff  128 Feb 17 14:49 PETCARE-PH4-DISCOVERY

find evidence_output -maxdepth 3 \( -type f -name '*.zip' -o -type f -name 'MANIFEST.json' -o -type f -name '*.md' \) 2>/dev/null | sort | sed -n '1,260p' || true
evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/MANIFEST.json
evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/MANIFEST.json
evidence_output/PETCARE-EMERGENT-HANDOFF/PETCARE-EMERGENT-HANDOFF_20260217T091134Z.zip
evidence_output/PETCARE-EMERGENT-HANDOFF/PETCARE-EMERGENT-HANDOFF_20260217T091428Z.zip
evidence_output/PETCARE-PH2-CLOSURE/PETCARE-PH2-CLOSURE_20260217T085354Z.zip
evidence_output/PETCARE-PH2-INPUTS/PETCARE-PH2-INPUTS_20260217T081959Z.zip
evidence_output/PETCARE-PH3-P1-CLOSURE/PETCARE-PH3-P1-CLOSURE_20260217T104807Z.zip
evidence_output/PETCARE-PH3-P2-CLOSURE/PETCARE-PH3-P2-CLOSURE_20260217T112255Z.zip
evidence_output/PETCARE-PH3-P3-CLOSURE/PETCARE-PH3-P3-CLOSURE_20260217T113820Z.zip
evidence_output/PETCARE-PH4-DISCOVERY/20260217T114627Z/DISCOVERY_REPORT.md
evidence_output/PETCARE-PH4-DISCOVERY/20260217T114922Z/DISCOVERY_REPORT.md
```
## Phase-2 / Phase-3 / Export keywords scan

```

grep -R --line-number --fixed-string 'PHASE-2' . 2>/dev/null | sed -n '1,240p' || true
./evidence_output/PETCARE-PH4-DISCOVERY/20260217T114627Z/DISCOVERY_REPORT.md:82:grep -R --line-number --fixed-string 'PHASE-2' . 2>/dev/null | sed -n '1,200p' || true
./evidence_output/PETCARE-PH4-DISCOVERY/20260217T114627Z/DISCOVERY_REPORT.md:83:./evidence_output/PETCARE-PH4-DISCOVERY/20260217T114627Z/LOGS.txt:2:grep -R --line-number --fixed-string 'PHASE-2' . 2>/dev/null | sed -n '1,200p' || true
./evidence_output/PETCARE-PH4-DISCOVERY/20260217T114627Z/DISCOVERY_REPORT.md:84:./scripts/petcare_ph4_discovery_pack.sh:63:run "grep -R --line-number --fixed-string 'PHASE-2' . 2>/dev/null | sed -n '1,200p' || true"
./evidence_output/PETCARE-PH4-DISCOVERY/20260217T114922Z/LOGS.txt:2:grep -R --line-number --fixed-string 'PHASE-2' . 2>/dev/null | sed -n '1,240p' || true
./scripts/petcare_ph4_discovery_pack.sh:64:run "grep -R --line-number --fixed-string 'PHASE-2' . 2>/dev/null | sed -n '1,240p' || true"

grep -R --line-number --fixed-string 'PHASE-3' . 2>/dev/null | sed -n '1,240p' || true
./evidence_output/PETCARE-PH4-DISCOVERY/20260217T114627Z/DISCOVERY_REPORT.md:86:grep -R --line-number --fixed-string 'PHASE-3' . 2>/dev/null | sed -n '1,200p' || true
./evidence_output/PETCARE-PH4-DISCOVERY/20260217T114627Z/DISCOVERY_REPORT.md:87:./evidence_output/PETCARE-PH4-DISCOVERY/20260217T114627Z/LOGS.txt:6:grep -R --line-number --fixed-string 'PHASE-3' . 2>/dev/null | sed -n '1,200p' || true
./evidence_output/PETCARE-PH4-DISCOVERY/20260217T114627Z/DISCOVERY_REPORT.md:88:./scripts/petcare_ph4_discovery_pack.sh:64:run "grep -R --line-number --fixed-string 'PHASE-3' . 2>/dev/null | sed -n '1,200p' || true"
./evidence_output/PETCARE-PH4-DISCOVERY/20260217T114922Z/LOGS.txt:9:grep -R --line-number --fixed-string 'PHASE-3' . 2>/dev/null | sed -n '1,240p' || true
./scripts/petcare_ph4_discovery_pack.sh:65:run "grep -R --line-number --fixed-string 'PHASE-3' . 2>/dev/null | sed -n '1,240p' || true"

grep -R --line-number --ignore-case -E 'evidence export|export bundle|deterministic export|exporter|MANIFEST.json|tenant isolation|tenant_id|x-tenant|uuid' . 2>/dev/null | sed -n '1,320p' || true
./EVIDENCE/MANIFEST.json:21:      "path": "EVIDENCE/MANIFEST.json",
./EVIDENCE/MANIFEST.json:191:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/MANIFEST.json",
./EVIDENCE/MANIFEST.json:246:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/MANIFEST.json",
./EVIDENCE/MANIFEST.json:331:      "path": "evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/EVIDENCE/MANIFEST.json",
./EVIDENCE/MANIFEST.json:426:      "path": "evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/EVIDENCE/MANIFEST.json",
./EVIDENCE/MANIFEST.json:506:      "path": "evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/EVIDENCE/MANIFEST.json",
./EVIDENCE/MANIFEST.json:571:      "path": "evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/EVIDENCE/MANIFEST.json",
Binary file ./evidence_output/PETCARE-PH3-P2-CLOSURE/PETCARE-PH3-P2-CLOSURE_20260217T112255Z.zip matches
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/closure_files.txt:6:EVIDENCE/MANIFEST.json
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/EVIDENCE/MANIFEST.json:21:      "path": "EVIDENCE/MANIFEST.json",
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/EVIDENCE/MANIFEST.json:191:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/MANIFEST.json",
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/EVIDENCE/MANIFEST.json:246:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/MANIFEST.json",
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/EVIDENCE/MANIFEST.json:331:      "path": "evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/EVIDENCE/MANIFEST.json",
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/EVIDENCE/MANIFEST.json:426:      "path": "evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/EVIDENCE/MANIFEST.json",
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/TESTS/test_tenant_isolation.py:5:    normalize_tenant_id,
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/TESTS/test_tenant_isolation.py:21:        self.assertEqual(TENANT_HEADER, "x-tenant-id")
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/TESTS/test_tenant_isolation.py:25:            normalize_tenant_id(None)
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/TESTS/test_tenant_isolation.py:29:            normalize_tenant_id("  ")
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/TESTS/test_tenant_isolation.py:31:    def test_invalid_uuid(self):
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/TESTS/test_tenant_isolation.py:33:            normalize_tenant_id("not-a-uuid")
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/TESTS/test_tenant_isolation.py:36:        self.assertEqual(normalize_tenant_id(T1.upper()), T1)
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/TESTS/test_tenant_isolation.py:41:        self.assertEqual(ctx.tenant_id, T1)
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/TESTS/test_tenant_isolation.py:83:        self.assertEqual(b["tenant_id"], T1)
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/scripts/run_api.sh:29:  echo "${r1}" | grep -q 'x-tenant-id is required' || { echo "FAIL: missing tenant not rejected"; exit 3; }
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/scripts/run_api.sh:32:  r2="$(curl -sS -X POST "${API}/api/platform-admin/storage/put" -H "Content-Type: application/json" -H "x-tenant-id: ${TENANT}" -d '{"key":"k1","value":"v1","actor_id":"a"}' || true)"
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/scripts/run_api.sh:37:  r3="$(curl -sS -X POST "${API}/api/platform-admin/storage/get" -H "Content-Type: application/json" -H "x-tenant-id: ${TENANT}" -d '{"key":"k1"}' || true)"
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:8:TENANT_HEADER = "x-tenant-id"
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:9:UUID_RE = re.compile(r"^[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}$")
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:24:def normalize_tenant_id(raw: Optional[str]) -> str:
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:30:    if not UUID_RE.match(v):
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:31:        raise InvalidTenantHeader(f"{TENANT_HEADER} must be a UUID")
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:37:    tenant_id: str
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:41:        return TenantContext(tenant_id=normalize_tenant_id(raw))
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/FND/CODE_SCAFFOLD/app.py:12:def _tenant_ctx_dependency(x_tenant_id: Optional[str] = Header(default=None, alias=TENANT_HEADER)) -> TenantContext:
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/FND/CODE_SCAFFOLD/app.py:13:    return require_tenant_context(x_tenant_id)
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/FND/CODE_SCAFFOLD/app.py:34:        store.put(tenant_id=ctx.tenant_id, key=str(key), value=value, actor_id=str(actor_id))
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/FND/CODE_SCAFFOLD/app.py:40:        v = store.get(tenant_id=ctx.tenant_id, key=str(key))
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/FND/CODE_SCAFFOLD/app.py:47:        existed = store.delete(tenant_id=ctx.tenant_id, key=str(key), actor_id=str(actor_id))
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/FND/CODE_SCAFFOLD/app.py:53:        keys = store.list_keys(tenant_id=ctx.tenant_id, prefix=prefix)
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/smoke.log:5:{"error":"x-tenant-id is required"}
./evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/closure_sha256.txt:5:2a24bc14a03cd0095aedff04f7828529fe36bdef639bcd157e7d7806f13d9c9f  evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/EVIDENCE/MANIFEST.json
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/closure_files.txt:6:EVIDENCE/MANIFEST.json
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/EVIDENCE/MANIFEST.json:21:      "path": "EVIDENCE/MANIFEST.json",
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/EVIDENCE/MANIFEST.json:191:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/MANIFEST.json",
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/EVIDENCE/MANIFEST.json:246:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/MANIFEST.json",
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/EVIDENCE/MANIFEST.json:331:      "path": "evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/EVIDENCE/MANIFEST.json",
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/EVIDENCE/MANIFEST.json:426:      "path": "evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/EVIDENCE/MANIFEST.json",
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/EVIDENCE/MANIFEST.json:506:      "path": "evidence_output/PETCARE-PH3-P2-CLOSURE/20260217T112255Z/snapshots/EVIDENCE/MANIFEST.json",
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/TESTS/test_tenant_isolation.py:5:    normalize_tenant_id,
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/TESTS/test_tenant_isolation.py:21:        self.assertEqual(TENANT_HEADER, "x-tenant-id")
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/TESTS/test_tenant_isolation.py:25:            normalize_tenant_id(None)
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/TESTS/test_tenant_isolation.py:29:            normalize_tenant_id("  ")
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/TESTS/test_tenant_isolation.py:31:    def test_invalid_uuid(self):
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/TESTS/test_tenant_isolation.py:33:            normalize_tenant_id("not-a-uuid")
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/TESTS/test_tenant_isolation.py:36:        self.assertEqual(normalize_tenant_id(T1.upper()), T1)
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/TESTS/test_tenant_isolation.py:41:        self.assertEqual(ctx.tenant_id, T1)
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/TESTS/test_tenant_isolation.py:56:    def test_put_requires_uuid_tenant(self):
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/TESTS/test_tenant_isolation.py:58:            self.s.put("not-a-uuid", "k", "v", "a")
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/TESTS/test_tenant_isolation.py:91:        self.assertEqual(b["tenant_id"], T1)
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/scripts/run_api.sh:29:  echo "${r1}" | grep -q 'x-tenant-id is required' || { echo "FAIL: missing tenant not rejected"; exit 3; }
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/scripts/run_api.sh:32:  r2="$(curl -sS -X POST "${API}/api/platform-admin/storage/put" -H "Content-Type: application/json" -H "x-tenant-id: ${TENANT}" -d '{"key":"k1","value":"v1","actor_id":"a"}' || true)"
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/scripts/run_api.sh:37:  r3="$(curl -sS -X POST "${API}/api/platform-admin/storage/get" -H "Content-Type: application/json" -H "x-tenant-id: ${TENANT}" -d '{"key":"k1"}' || true)"
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:7:from FND.CODE_SCAFFOLD.tenant_isolation_guard import normalize_tenant_id
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:19:    def _require_tenant(self, tenant_id: str) -> str:
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:20:        return normalize_tenant_id(tenant_id)
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:28:    def put(self, tenant_id: str, key: str, value: Any, actor_id: str) -> None:
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:29:        t = self._require_tenant(tenant_id)
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:36:    def get(self, tenant_id: str, key: str) -> Optional[Any]:
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:37:        t = self._require_tenant(tenant_id)
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:41:    def delete(self, tenant_id: str, key: str, actor_id: str) -> bool:
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:42:        t = self._require_tenant(tenant_id)
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:52:    def list_keys(self, tenant_id: str, prefix: str = "") -> List[str]:
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:53:        t = self._require_tenant(tenant_id)
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:61:    def audit_log(self, tenant_id: str) -> List[Dict[str, Any]]:
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:62:        t = self._require_tenant(tenant_id)
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:8:TENANT_HEADER = "x-tenant-id"
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:9:UUID_RE = re.compile(r"^[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}$")
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:24:def normalize_tenant_id(raw: Optional[str]) -> str:
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:30:    if not UUID_RE.match(v):
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:31:        raise InvalidTenantHeader(f"{TENANT_HEADER} must be a UUID")
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:37:    tenant_id: str
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:41:        return TenantContext(tenant_id=normalize_tenant_id(raw))
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/app.py:12:def _tenant_ctx_dependency(x_tenant_id: Optional[str] = Header(default=None, alias=TENANT_HEADER)) -> TenantContext:
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/app.py:13:    return require_tenant_context(x_tenant_id)
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/app.py:34:        store.put(tenant_id=ctx.tenant_id, key=str(key), value=value, actor_id=str(actor_id))
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/app.py:40:        v = store.get(tenant_id=ctx.tenant_id, key=str(key))
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/app.py:47:        existed = store.delete(tenant_id=ctx.tenant_id, key=str(key), actor_id=str(actor_id))
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/FND/CODE_SCAFFOLD/app.py:53:        keys = store.list_keys(tenant_id=ctx.tenant_id, prefix=prefix)
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/smoke.log:5:{"error":"x-tenant-id is required"}
./evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/closure_sha256.txt:5:f5746104575c7e69f70e13f17f0ea85950f9d6e618681548c7cef7fc546804d5  evidence_output/PETCARE-PH3-P3-CLOSURE/20260217T113820Z/snapshots/EVIDENCE/MANIFEST.json
Binary file ./evidence_output/PETCARE-PH3-P3-CLOSURE/PETCARE-PH3-P3-CLOSURE_20260217T113820Z.zip matches
Binary file ./evidence_output/PETCARE-EMERGENT-HANDOFF/PETCARE-EMERGENT-HANDOFF_20260217T091134Z.zip matches
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/TESTS/test_tenant_isolation.py:3:from FND.CODE_SCAFFOLD.tenant_isolation_guard import normalize_tenant_id, MissingTenantHeader, InvalidTenantHeader
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/TESTS/test_tenant_isolation.py:15:            normalize_tenant_id(None)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/TESTS/test_tenant_isolation.py:19:            normalize_tenant_id("  ")
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/TESTS/test_tenant_isolation.py:21:    def test_invalid_uuid(self):
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/TESTS/test_tenant_isolation.py:23:            normalize_tenant_id("not-a-uuid")
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/TESTS/test_tenant_isolation.py:26:        self.assertEqual(normalize_tenant_id(T1.upper()), T1)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/TESTS/test_tenant_isolation.py:64:        self.assertEqual(b["tenant_id"], T1)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/storage/export_bundle.py:7:from FND.CODE_SCAFFOLD.tenant_isolation_guard import normalize_tenant_id
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/storage/export_bundle.py:16:    tenant_id: str
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/storage/export_bundle.py:27:def build_export_bundle(tenant_id: str, keys: List[str], records: int) -> Dict[str, Any]:
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/storage/export_bundle.py:28:    t = normalize_tenant_id(tenant_id)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/storage/export_bundle.py:34:    b = ExportBundle(tenant_id=t, ts=_utc_ts_compact(), keys=k, records=r)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:18:    def _require_tenant(self, tenant_id: str) -> str:
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:19:        t = (tenant_id or "").strip()
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:21:            raise ValueError("tenant_id is required")
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:24:    def put(self, tenant_id: str, key: str, value: Any, actor_id: str) -> None:
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:25:        t = self._require_tenant(tenant_id)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:34:    def get(self, tenant_id: str, key: str) -> Optional[Any]:
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:35:        t = self._require_tenant(tenant_id)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:41:    def delete(self, tenant_id: str, key: str, actor_id: str) -> bool:
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:42:        t = self._require_tenant(tenant_id)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:54:    def list_keys(self, tenant_id: str, prefix: str = "") -> List[str]:
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:55:        t = self._require_tenant(tenant_id)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:63:    def audit_log(self, tenant_id: str) -> List[Dict[str, Any]]:
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:64:        t = self._require_tenant(tenant_id)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:8:TENANT_HEADER = "x-tenant-id"
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:9:UUID_RE = re.compile(r"^[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}$")
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:24:def normalize_tenant_id(raw: Optional[str]) -> str:
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:26:        raise MissingTenantHeader("x-tenant-id is required")
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:29:        raise MissingTenantHeader("x-tenant-id is required")
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:30:    if not UUID_RE.match(v):
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:31:        raise InvalidTenantHeader("x-tenant-id must be a UUID")
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:37:    tenant_id: str
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:41:        return TenantContext(tenant_id=normalize_tenant_id(raw))
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/app.py:8:from FND.CODE_SCAFFOLD.tenant_isolation_guard import TenantIsolationError, normalize_tenant_id
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/app.py:26:    async def storage_put(payload: Dict[str, Any], x_tenant_id: Optional[str] = Header(default=None)):
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/app.py:27:        tenant_id = normalize_tenant_id(x_tenant_id)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/app.py:31:        store.put(tenant_id=tenant_id, key=str(key), value=value, actor_id=str(actor_id))
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/app.py:35:    async def storage_get(payload: Dict[str, Any], x_tenant_id: Optional[str] = Header(default=None)):
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/app.py:36:        tenant_id = normalize_tenant_id(x_tenant_id)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/app.py:38:        v = store.get(tenant_id=tenant_id, key=str(key))
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/app.py:42:    async def storage_delete(payload: Dict[str, Any], x_tenant_id: Optional[str] = Header(default=None)):
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/app.py:43:        tenant_id = normalize_tenant_id(x_tenant_id)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/app.py:46:        existed = store.delete(tenant_id=tenant_id, key=str(key), actor_id=str(actor_id))
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/app.py:50:    async def storage_list(payload: Dict[str, Any], x_tenant_id: Optional[str] = Header(default=None)):
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/app.py:51:        tenant_id = normalize_tenant_id(x_tenant_id)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/app.py:53:        keys = store.list_keys(tenant_id=tenant_id, prefix=prefix)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/interfaces/storage_interface.py:7:    def put(self, tenant_id: str, key: str, value: Any, actor_id: str) -> None:
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/interfaces/storage_interface.py:10:    def get(self, tenant_id: str, key: str) -> Optional[Any]:
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/interfaces/storage_interface.py:13:    def delete(self, tenant_id: str, key: str, actor_id: str) -> bool:
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/interfaces/storage_interface.py:16:    def list_keys(self, tenant_id: str, prefix: str = "") -> List[str]:
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/snapshots/FND/CODE_SCAFFOLD/interfaces/storage_interface.py:19:    def audit_log(self, tenant_id: str) -> List[Dict[str, Any]]:
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/repo_files_sha256.txt:1047:05072cafcaf1e16d1e7c60e400117ccdc9b1bfa3b39b07ec5f0b278f8fd502da  ./EVIDENCE/MANIFEST.json
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/MANIFEST.json:21:      "path": "EVIDENCE/MANIFEST.json",
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/MANIFEST.json:201:      "path": "evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/EVIDENCE/MANIFEST.json",
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/TESTS/test_tenant_isolation.py:3:from FND.CODE_SCAFFOLD.tenant_isolation_guard import normalize_tenant_id, MissingTenantHeader, InvalidTenantHeader
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/TESTS/test_tenant_isolation.py:15:            normalize_tenant_id(None)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/TESTS/test_tenant_isolation.py:19:            normalize_tenant_id("  ")
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/TESTS/test_tenant_isolation.py:21:    def test_invalid_uuid(self):
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/TESTS/test_tenant_isolation.py:23:            normalize_tenant_id("not-a-uuid")
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/TESTS/test_tenant_isolation.py:26:        self.assertEqual(normalize_tenant_id(T1.upper()), T1)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/TESTS/test_tenant_isolation.py:64:        self.assertEqual(b["tenant_id"], T1)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/storage/export_bundle.py:7:from FND.CODE_SCAFFOLD.tenant_isolation_guard import normalize_tenant_id
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/storage/export_bundle.py:16:    tenant_id: str
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/storage/export_bundle.py:27:def build_export_bundle(tenant_id: str, keys: List[str], records: int) -> Dict[str, Any]:
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/storage/export_bundle.py:28:    t = normalize_tenant_id(tenant_id)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/storage/export_bundle.py:34:    b = ExportBundle(tenant_id=t, ts=_utc_ts_compact(), keys=k, records=r)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:18:    def _require_tenant(self, tenant_id: str) -> str:
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:19:        t = (tenant_id or "").strip()
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:21:            raise ValueError("tenant_id is required")
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:24:    def put(self, tenant_id: str, key: str, value: Any, actor_id: str) -> None:
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:25:        t = self._require_tenant(tenant_id)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:34:    def get(self, tenant_id: str, key: str) -> Optional[Any]:
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:35:        t = self._require_tenant(tenant_id)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:41:    def delete(self, tenant_id: str, key: str, actor_id: str) -> bool:
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:42:        t = self._require_tenant(tenant_id)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:54:    def list_keys(self, tenant_id: str, prefix: str = "") -> List[str]:
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:55:        t = self._require_tenant(tenant_id)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:63:    def audit_log(self, tenant_id: str) -> List[Dict[str, Any]]:
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:64:        t = self._require_tenant(tenant_id)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:8:TENANT_HEADER = "x-tenant-id"
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:9:UUID_RE = re.compile(r"^[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}$")
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:24:def normalize_tenant_id(raw: Optional[str]) -> str:
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:26:        raise MissingTenantHeader("x-tenant-id is required")
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:29:        raise MissingTenantHeader("x-tenant-id is required")
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:30:    if not UUID_RE.match(v):
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:31:        raise InvalidTenantHeader("x-tenant-id must be a UUID")
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:37:    tenant_id: str
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:41:        return TenantContext(tenant_id=normalize_tenant_id(raw))
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/app.py:8:from FND.CODE_SCAFFOLD.tenant_isolation_guard import TenantIsolationError, normalize_tenant_id
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/app.py:26:    async def storage_put(payload: Dict[str, Any], x_tenant_id: Optional[str] = Header(default=None)):
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/app.py:27:        tenant_id = normalize_tenant_id(x_tenant_id)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/app.py:31:        store.put(tenant_id=tenant_id, key=str(key), value=value, actor_id=str(actor_id))
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/app.py:35:    async def storage_get(payload: Dict[str, Any], x_tenant_id: Optional[str] = Header(default=None)):
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/app.py:36:        tenant_id = normalize_tenant_id(x_tenant_id)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/app.py:38:        v = store.get(tenant_id=tenant_id, key=str(key))
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/app.py:42:    async def storage_delete(payload: Dict[str, Any], x_tenant_id: Optional[str] = Header(default=None)):
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/app.py:43:        tenant_id = normalize_tenant_id(x_tenant_id)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/app.py:46:        existed = store.delete(tenant_id=tenant_id, key=str(key), actor_id=str(actor_id))
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/app.py:50:    async def storage_list(payload: Dict[str, Any], x_tenant_id: Optional[str] = Header(default=None)):
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/app.py:51:        tenant_id = normalize_tenant_id(x_tenant_id)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/app.py:53:        keys = store.list_keys(tenant_id=tenant_id, prefix=prefix)
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/interfaces/storage_interface.py:7:    def put(self, tenant_id: str, key: str, value: Any, actor_id: str) -> None:
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/interfaces/storage_interface.py:10:    def get(self, tenant_id: str, key: str) -> Optional[Any]:
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/interfaces/storage_interface.py:13:    def delete(self, tenant_id: str, key: str, actor_id: str) -> bool:
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/interfaces/storage_interface.py:16:    def list_keys(self, tenant_id: str, prefix: str = "") -> List[str]:
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/snapshots/FND/CODE_SCAFFOLD/interfaces/storage_interface.py:19:    def audit_log(self, tenant_id: str) -> List[Dict[str, Any]]:
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/repo_files_sha256.txt:1047:05072cafcaf1e16d1e7c60e400117ccdc9b1bfa3b39b07ec5f0b278f8fd502da  ./EVIDENCE/MANIFEST.json
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/MANIFEST.json:21:      "path": "EVIDENCE/MANIFEST.json",
./evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/MANIFEST.json:201:      "path": "evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/EVIDENCE/MANIFEST.json",
Binary file ./evidence_output/PETCARE-EMERGENT-HANDOFF/PETCARE-EMERGENT-HANDOFF_20260217T091428Z.zip matches
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/closure_files.txt:9:EVIDENCE/MANIFEST.json
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/EVIDENCE/MANIFEST.json:21:      "path": "EVIDENCE/MANIFEST.json",
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/EVIDENCE/MANIFEST.json:191:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091134Z/MANIFEST.json",
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/EVIDENCE/MANIFEST.json:246:      "path": "evidence_output/PETCARE-EMERGENT-HANDOFF/20260217T091428Z/MANIFEST.json",
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/EVIDENCE/MANIFEST.json:331:      "path": "evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/EVIDENCE/MANIFEST.json",
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/TESTS/test_tenant_isolation.py:3:from FND.CODE_SCAFFOLD.tenant_isolation_guard import normalize_tenant_id, MissingTenantHeader, InvalidTenantHeader
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/TESTS/test_tenant_isolation.py:15:            normalize_tenant_id(None)
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/TESTS/test_tenant_isolation.py:19:            normalize_tenant_id("  ")
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/TESTS/test_tenant_isolation.py:21:    def test_invalid_uuid(self):
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/TESTS/test_tenant_isolation.py:23:            normalize_tenant_id("not-a-uuid")
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/TESTS/test_tenant_isolation.py:26:        self.assertEqual(normalize_tenant_id(T1.upper()), T1)
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/TESTS/test_tenant_isolation.py:64:        self.assertEqual(b["tenant_id"], T1)
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/scripts/run_api.sh:29:  echo "${r1}" | grep -q 'x-tenant-id is required' || { echo "FAIL: missing tenant not rejected"; exit 3; }
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/scripts/run_api.sh:32:  r2="$(curl -sS -X POST "${API}/api/platform-admin/storage/put" -H "Content-Type: application/json" -H "x-tenant-id: ${TENANT}" -d '{"key":"k1","value":"v1","actor_id":"a"}' || true)"
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/scripts/run_api.sh:37:  r3="$(curl -sS -X POST "${API}/api/platform-admin/storage/get" -H "Content-Type: application/json" -H "x-tenant-id: ${TENANT}" -d '{"key":"k1"}' || true)"
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/storage/export_bundle.py:7:from FND.CODE_SCAFFOLD.tenant_isolation_guard import normalize_tenant_id
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/storage/export_bundle.py:16:    tenant_id: str
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/storage/export_bundle.py:27:def build_export_bundle(tenant_id: str, keys: List[str], records: int) -> Dict[str, Any]:
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/storage/export_bundle.py:28:    t = normalize_tenant_id(tenant_id)
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/storage/export_bundle.py:34:    b = ExportBundle(tenant_id=t, ts=_utc_ts_compact(), keys=k, records=r)
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:18:    def _require_tenant(self, tenant_id: str) -> str:
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:19:        t = (tenant_id or "").strip()
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:21:            raise ValueError("tenant_id is required")
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:24:    def put(self, tenant_id: str, key: str, value: Any, actor_id: str) -> None:
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:25:        t = self._require_tenant(tenant_id)
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:34:    def get(self, tenant_id: str, key: str) -> Optional[Any]:
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:35:        t = self._require_tenant(tenant_id)
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:41:    def delete(self, tenant_id: str, key: str, actor_id: str) -> bool:
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:42:        t = self._require_tenant(tenant_id)
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:54:    def list_keys(self, tenant_id: str, prefix: str = "") -> List[str]:
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:55:        t = self._require_tenant(tenant_id)
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:63:    def audit_log(self, tenant_id: str) -> List[Dict[str, Any]]:
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:64:        t = self._require_tenant(tenant_id)
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:8:TENANT_HEADER = "x-tenant-id"
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:9:UUID_RE = re.compile(r"^[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}$")
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:24:def normalize_tenant_id(raw: Optional[str]) -> str:
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:26:        raise MissingTenantHeader("x-tenant-id is required")
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:29:        raise MissingTenantHeader("x-tenant-id is required")
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:30:    if not UUID_RE.match(v):
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:31:        raise InvalidTenantHeader("x-tenant-id must be a UUID")
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:37:    tenant_id: str
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:41:        return TenantContext(tenant_id=normalize_tenant_id(raw))
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/app.py:8:from FND.CODE_SCAFFOLD.tenant_isolation_guard import TenantIsolationError, normalize_tenant_id
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/app.py:26:    async def storage_put(payload: Dict[str, Any], x_tenant_id: Optional[str] = Header(default=None)):
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/app.py:27:        tenant_id = normalize_tenant_id(x_tenant_id)
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/app.py:31:        store.put(tenant_id=tenant_id, key=str(key), value=value, actor_id=str(actor_id))
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/app.py:35:    async def storage_get(payload: Dict[str, Any], x_tenant_id: Optional[str] = Header(default=None)):
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/app.py:36:        tenant_id = normalize_tenant_id(x_tenant_id)
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/app.py:38:        v = store.get(tenant_id=tenant_id, key=str(key))
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/app.py:42:    async def storage_delete(payload: Dict[str, Any], x_tenant_id: Optional[str] = Header(default=None)):
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/app.py:43:        tenant_id = normalize_tenant_id(x_tenant_id)
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/app.py:46:        existed = store.delete(tenant_id=tenant_id, key=str(key), actor_id=str(actor_id))
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/app.py:50:    async def storage_list(payload: Dict[str, Any], x_tenant_id: Optional[str] = Header(default=None)):
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/app.py:51:        tenant_id = normalize_tenant_id(x_tenant_id)
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/app.py:53:        keys = store.list_keys(tenant_id=tenant_id, prefix=prefix)
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/interfaces/storage_interface.py:7:    def put(self, tenant_id: str, key: str, value: Any, actor_id: str) -> None:
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/interfaces/storage_interface.py:10:    def get(self, tenant_id: str, key: str) -> Optional[Any]:
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/interfaces/storage_interface.py:13:    def delete(self, tenant_id: str, key: str, actor_id: str) -> bool:
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/interfaces/storage_interface.py:16:    def list_keys(self, tenant_id: str, prefix: str = "") -> List[str]:
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/FND/CODE_SCAFFOLD/interfaces/storage_interface.py:19:    def audit_log(self, tenant_id: str) -> List[Dict[str, Any]]:
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/smoke.log:5:{"error":"x-tenant-id is required"}
./evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/closure_sha256.txt:5:c7109c7a9bd51655bfb49078f6d5370cf0a43b4db63a0cdd743462279d40cc04  evidence_output/PETCARE-PH3-P1-CLOSURE/20260217T104807Z/snapshots/EVIDENCE/MANIFEST.json
Binary file ./evidence_output/PETCARE-PH3-P1-CLOSURE/PETCARE-PH3-P1-CLOSURE_20260217T104807Z.zip matches
Binary file ./evidence_output/PETCARE-PH2-CLOSURE/PETCARE-PH2-CLOSURE_20260217T085354Z.zip matches
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/EVIDENCE/MANIFEST.json:21:      "path": "EVIDENCE/MANIFEST.json",
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/TESTS/test_tenant_isolation.py:3:from FND.CODE_SCAFFOLD.tenant_isolation_guard import normalize_tenant_id, MissingTenantHeader, InvalidTenantHeader
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/TESTS/test_tenant_isolation.py:15:            normalize_tenant_id(None)
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/TESTS/test_tenant_isolation.py:19:            normalize_tenant_id("  ")
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/TESTS/test_tenant_isolation.py:21:    def test_invalid_uuid(self):
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/TESTS/test_tenant_isolation.py:23:            normalize_tenant_id("not-a-uuid")
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/TESTS/test_tenant_isolation.py:26:        self.assertEqual(normalize_tenant_id(T1.upper()), T1)
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/TESTS/test_tenant_isolation.py:64:        self.assertEqual(b["tenant_id"], T1)
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/storage/export_bundle.py:7:from FND.CODE_SCAFFOLD.tenant_isolation_guard import normalize_tenant_id
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/storage/export_bundle.py:16:    tenant_id: str
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/storage/export_bundle.py:27:def build_export_bundle(tenant_id: str, keys: List[str], records: int) -> Dict[str, Any]:
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/storage/export_bundle.py:28:    t = normalize_tenant_id(tenant_id)
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/storage/export_bundle.py:34:    b = ExportBundle(tenant_id=t, ts=_utc_ts_compact(), keys=k, records=r)
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:18:    def _require_tenant(self, tenant_id: str) -> str:
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:19:        t = (tenant_id or "").strip()
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:21:            raise ValueError("tenant_id is required")
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:24:    def put(self, tenant_id: str, key: str, value: Any, actor_id: str) -> None:
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:25:        t = self._require_tenant(tenant_id)
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:34:    def get(self, tenant_id: str, key: str) -> Optional[Any]:
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:35:        t = self._require_tenant(tenant_id)
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:41:    def delete(self, tenant_id: str, key: str, actor_id: str) -> bool:
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:42:        t = self._require_tenant(tenant_id)
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:54:    def list_keys(self, tenant_id: str, prefix: str = "") -> List[str]:
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:55:        t = self._require_tenant(tenant_id)
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:63:    def audit_log(self, tenant_id: str) -> List[Dict[str, Any]]:
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/storage/memory_store.py:64:        t = self._require_tenant(tenant_id)
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:8:TENANT_HEADER = "x-tenant-id"
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:9:UUID_RE = re.compile(r"^[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}$")
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:24:def normalize_tenant_id(raw: Optional[str]) -> str:
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:26:        raise MissingTenantHeader("x-tenant-id is required")
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:29:        raise MissingTenantHeader("x-tenant-id is required")
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:30:    if not UUID_RE.match(v):
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:31:        raise InvalidTenantHeader("x-tenant-id must be a UUID")
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:37:    tenant_id: str
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/tenant_isolation_guard.py:41:        return TenantContext(tenant_id=normalize_tenant_id(raw))
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/app.py:11:from FND.CODE_SCAFFOLD.tenant_isolation_guard import TenantIsolationError, normalize_tenant_id
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/app.py:32:    async def storage_put(payload: Dict[str, Any], x_tenant_id: Optional[str] = Header(default=None)):
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/app.py:33:        tenant_id = normalize_tenant_id(x_tenant_id)
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/app.py:37:        store.put(tenant_id=tenant_id, key=str(key), value=value, actor_id=str(actor_id))
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/app.py:41:    async def storage_get(payload: Dict[str, Any], x_tenant_id: Optional[str] = Header(default=None)):
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/app.py:42:        tenant_id = normalize_tenant_id(x_tenant_id)
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/app.py:44:        v = store.get(tenant_id=tenant_id, key=str(key))
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/app.py:48:    async def storage_delete(payload: Dict[str, Any], x_tenant_id: Optional[str] = Header(default=None)):
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/app.py:49:        tenant_id = normalize_tenant_id(x_tenant_id)
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/app.py:52:        existed = store.delete(tenant_id=tenant_id, key=str(key), actor_id=str(actor_id))
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/app.py:56:    async def storage_list(payload: Dict[str, Any], x_tenant_id: Optional[str] = Header(default=None)):
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/app.py:57:        tenant_id = normalize_tenant_id(x_tenant_id)
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/app.py:59:        keys = store.list_keys(tenant_id=tenant_id, prefix=prefix)
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/interfaces/storage_interface.py:7:    def put(self, tenant_id: str, key: str, value: Any, actor_id: str) -> None:
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/interfaces/storage_interface.py:10:    def get(self, tenant_id: str, key: str) -> Optional[Any]:
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/interfaces/storage_interface.py:13:    def delete(self, tenant_id: str, key: str, actor_id: str) -> bool:
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/interfaces/storage_interface.py:16:    def list_keys(self, tenant_id: str, prefix: str = "") -> List[str]:
./evidence_output/PETCARE-PH2-CLOSURE/20260217T085354Z/snapshots/FND/CODE_SCAFFOLD/interfaces/storage_interface.py:19:    def audit_log(self, tenant_id: str) -> List[Dict[str, Any]]:
```
## Tests + smoke + land pack detection

```

find . -maxdepth 3 -type f \( -name '*smoke*.sh' -o -name '*land_pack*.sh' -o -name '*unittest*.sh' -o -name 'petcare_*pack*.sh' \) 2>/dev/null | sort || true
./BACKUP_FIX_LAND_20260216T202208Z/scripts/petcare_land_pack.sh
./scripts/petcare_land_pack.sh
./scripts/petcare_ph4_discovery_pack.sh
```
## Run validations (best-effort, no guessing)

```

python3 -m unittest -q || true
----------------------------------------------------------------------
Ran 0 tests in 0.000s

OK

echo 'SMOKE_SCRIPT_NOT_FOUND'
SMOKE_SCRIPT_NOT_FOUND

bash scripts/petcare_land_pack.sh
PetCare LAND PACK
root=/Users/waheebmahmoud/dev/petcare-evidence-repository/petcare_execution
compile: app.py
compile: scaffold python files
manifest: regenerate
PASS manifest
file_count 131
dirs 208
ui2 5 ui3 5 ui5 5 ui6 5 tests 4 fnd 9 evid 1 scripts 4 other 93
manifest_record True
DONE
```
## Manifest generation (python3/python preferred, shasum fallback)

## ZIP + SHA256

- ZIP: evidence_output/PETCARE-PH4-DISCOVERY/PETCARE-PH4-DISCOVERY_20260217T114922Z.zip
- SHA256_FILE: evidence_output/PETCARE-PH4-DISCOVERY/PETCARE-PH4-DISCOVERY_20260217T114922Z.zip.sha256
- REPORT: evidence_output/PETCARE-PH4-DISCOVERY/20260217T114922Z/DISCOVERY_REPORT.md
- MANIFEST: evidence_output/PETCARE-PH4-DISCOVERY/20260217T114922Z/MANIFEST.json
