# W0-I — security review findings, and what they changed

An automated security review of the W0-I commit flagged defects in
`professional_authority/authority.py`. They were real, they were mine, and CI was
green over them. Both are recorded here because the second one is a lesson about
the tests, not only about the code.

## Finding 1 · permissive tenant default (authorization bypass)

```python
def held_at(self, actor_id, when, tenant_id: Optional[str] = None) -> bool:
    ...
    if tenant_id is not None and g.tenant_id != tenant_id:
        continue
```

`tenant_id` was optional and defaulted to `None`, which the filter reads as
*"match a grant in any tenant"*. A caller who simply omitted the argument got a
cross-tenant authority check that looked correct at the call site.

W0-C's principle is that tenant scope is established server-side and is never
permissive. A default in an authorization path is a bypass waiting for someone to
forget an argument.

**Fixed:** `tenant_id` is now required on `held_at`, `professional_class_at` and
`attest_clinical_record`. There is no default, so the question cannot be asked
without naming its tenant.

## Finding 2 · cross-tenant class inference

`held_at` filtered by tenant; `professional_class_at` did not:

```python
def professional_class_at(self, actor_id, when):
    for g in self._grants:
        if g.actor_id == actor_id and g.held_at(when):   # no tenant filter
            return g.professional_class
```

So an actor could be correctly **denied** authority in a tenant while an
attestation still recorded a professional class derived from a **different**
tenant's grant. Two questions about the same grant were answered by two
independent lookups, and they disagreed.

**Fixed:** both now resolve through one `_grant_in_force(actor, when, tenant)`.
The attestation also records `grant_id` and `tenant_id`, so it can be re-checked
against the grant it actually relied on.

## The more important finding — about the tests

Perturbation P5 restored the permissive default. **Every test still passed.**

That is not a fix working; it is a guard that does not bind to the property it
claims to protect. Every call site in the suite passes `tenant_id` explicitly, so
restoring the vulnerable default breaks none of them. The tests were asserting
behaviour at call sites the tests themselves controlled — while the defect lived
in what happens when a caller *omits* the argument.

`test_tenant_id_carries_no_permissive_default` now asserts the **signature**: no
default on `tenant_id`, and omitting it raises. With that guard, P5 fails as it
must.

| Perturbation | Before the signature guard | After |
|---|---|---|
| P5 restore permissive default | **12 passed** — undetected | **FAILS** |
| P6 class resolution ignores tenant | FAILS (`T-PROF-05b`) | FAILS |

Written down because the failure mode generalises: a negative control that only
exercises correct call sites cannot detect a permissive default, and it looks
exactly like a passing test while doing so.

## Result

```
CROSS_TENANT_AUTHORITY=DENIED
CROSS_TENANT_CLASS_INFERENCE=DENIED
PERMISSIVE_TENANT_DEFAULT=REMOVED (guarded by signature assertion)
petcare_runtime tests: 234 -> 247
```
