# W0-A2 — fingerprint guard

## What changed and why

`_require_secret_key()` refused the retired key by comparing against it as a
plaintext literal. That worked, and it made the key impossible to remove: a
content-based history rewrite cannot distinguish the secret **as a leaked
value** from the secret **as the value a guard refuses**.

The Gate-5 offline rehearsal proved the consequence exactly. The rewrite
replaced the comparand, and the resulting tree **accepted the real retired key**
— while the full suite passed, because the same rewrite had edited the test
constants in step with the implementation.

```python
# before — the value is the comparand
if key.strip() == "<retired literal>":

# after — the value is nowhere; its digest is the comparand
RETIRED_KEY_FINGERPRINTS = frozenset({"1cdd7efa…f4ca"})
if hashlib.sha256(key.strip().encode()).hexdigest() in RETIRED_KEY_FINGERPRINTS:
```

Normalisation is unchanged (`key.strip()`), so the guard refuses exactly the
values it refused before — including padded forms, which a test now pins.

## Behaviour is identical

| Input | Before | After |
|---|---|---|
| unset | RuntimeError | RuntimeError |
| whitespace only | RuntimeError | RuntimeError |
| the retired key | RuntimeError | RuntimeError *(proved out-of-band)* |
| padded retired key | RuntimeError | RuntimeError |
| any other value | returned | returned |

## Occurrences removed — 11 across 5 files

Located by hashing byte windows, never by searching for the value.

| File | Was | Now |
|---|---|---|
| `petcare_api/routers/auth.py` | docstring quote + guard comparand | fingerprint set + prose without the value |
| `petcare_api/tests/test_secret_key_required.py` | `RETIRED_LITERAL` + docstring | synthetic value, patched fingerprint, pinned production digest |
| `petcare_api/tests/test_w0_ab_ordering_invariant.py` | `RETIRED_LITERAL` | `RETIRED_KEY_SHA256`, digest-matched AST scan |
| `tests/governance/test_repository_scanners.py` | 5 fixture occurrences | synthetic value — the patterns match the *shape* of the defect, not a particular key |
| `…/NOTION_AUTHORITY_SYNC.md` | prose quote | `<retired-literal; sha256=1cdd7efa…>` |

```
CURRENT_HEAD_TRACKED_PLAINTEXT = 0
ALL_GIT_HISTORY_PLAINTEXT      = still present — that is Gate-5, not this PR
```

## Tests added

- **mechanism**, against a synthetic value with a patched fingerprint set:
  rejected; near-miss accepted; padded form rejected;
- **`RETIRED_KEY_FINGERPRINTS` pinned** to the production digest — without this,
  emptying the set would defeat W0-A2 while every synthetic test still passed;
- **no retired key in `auth.py`** as any string constant, matched by digest;
- **no secret-sized literal comparand** — the structural companion, kept as a
  second signal and never as the sole proof;
- **the fingerprint check is reached** — `_require_secret_key` must actually
  reference the set, or a digest comparison could sit in dead code;
- **repository-wide absence guard** with its own positive control, plus a check
  that the guard file has not itself acquired the value.
