# A11 — KSA portability

```
KSA_PORTABILITY_PROOF=PASS
D21_CURRENT_STATE=TEMPORARY_OUT_OF_KINGDOM_ALLOWED
D21_TARGET_STATE=KSA_MIGRATION_MANDATORY_WHEN_APPROVED_KSA_SITE_READY
KSA_TARGET_INVENTED=NO
```

## What was already guarded, and what was not

`tests/governance/test_w0f_architecture_contracts.py` forbids a region, a
provider endpoint, a residency branch or an assigned KSA placeholder from
appearing in application code. It was passing. It was also **not scanning the
code W0-F added to `scripts/`**.

That gap was real rather than theoretical. When the guard's scan list was
written, `scripts/` held only verification scanners, which connect nowhere. It
now holds two operational tools: `apply_migrations.py` applies schema to a
database, and `identity_migration_dryrun.py` can write identities to one. A
region literal in either would pin the mandatory migration exactly as effectively
as one in the application — and would have been outside every guard that exists
to prevent it.

`scripts` is now in `APPLICATION_TREES`. It scans clean.

## Controls

| ID | Control | Result |
|---|---|---|
| KSA-01 | every W0-F module is inside the portability guard's scan set — asserted by name, because an absence assertion is only as wide as its scan | PASS |
| KSA-02 | no W0-F module names a region, endpoint or residency branch | PASS |
| KSA-03 | the three KSA target identifiers remain unassigned | PASS |
| KSA-04 | repointing the store at a different target needs no application change — proven by relocating and hashing the sources before and after | PASS |
| KSA-05 | the connection URL is assembled only from the governed secret's own fields; no literal host on that path | PASS |
| KSA-06 | the migration runner takes its target and never defaults one | PASS |

```
TESTS=tests/governance/test_ksa_portability.py                 6 passed
      tests/governance/test_w0f_architecture_contracts.py     11 passed
```

## The relocation proof

`KSA-04` performs a synthetic move: the same `build_persistence` is asked for a
store at a temporary location and then at a placeholder KSA target, and the
sources of all nine W0-F modules are SHA-256'd before and after. Both targets are
refused identically — neither exists — and that is the point: the code path is
the same, it names no location, and not one application byte changed.

The two addresses are RFC 5737 documentation addresses, routable nowhere. **No
KSA site or region is invented**, which is what lets this control run before the
destination is approved.

## Secret re-binding, recorded not executed

`MVC-W0F-KSA-MIGRATION-READINESS-001` §4: secrets are re-created in the target,
never copied, because copying material produces two live credentials with no
single revocation point. The provider supports this without code change — the
runtime is bound by secret IDENTIFIER, and re-binding is configuration.

```
SECRETS_COPIED=NO
SECRETS_CREATED=NO
```

## Residual, recorded

`ConsentRepository` and `UPHRService` are **file-backed**, not relational. A file
on a host does not travel with a logical database dump, so the KSA move has a
second data path that the migration readiness specification's §1–§2 do not cover.
Recorded rather than solved: it is outside W0-F's identity/tenancy/session
boundary.

```
FILE_BACKED_STATE_OUTSIDE_THE_LOGICAL_DUMP=CONSENT_STORE,UPHR_STORE
```
