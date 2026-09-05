# Out-of-band proof — the real retired key is still rejected

**Date:** 2026-09-05 · The plaintext appears nowhere in this file, this evidence
run, or any tracked file. Only its fingerprint.

## Why this proof cannot live in the test suite

The repository's tests exercise the *mechanism* with a synthetic value whose
fingerprint is patched in. They cannot exercise the real retired key, because
doing so would require the real key to be present in a tracked file — which is
exactly the condition W0-A2 exists to remove.

So the real-key proof is run out-of-band, once, from history, and the material
is destroyed immediately.

## Method

1. `git show 5202bb5f…:petcare_api/routers/auth.py` — the introducing commit.
2. AST parse; select module-level `SECRET_KEY = os.getenv("SECRET_KEY", <const>)`.
3. Require exactly **one** candidate. (Result: 1.)
4. Write its bytes to a mode-600 file inside a `mktemp -d` directory.
5. Probe the **new** guard in one-shot subprocesses, passing the value through
   the environment only — never on a command line, never in shell history.
6. Wipe the file with random bytes, unlink, remove the directory.

```
PROBE_INPUT_SHA256          = 1cdd7efa59d45698ceba9652ee1c22aa7472503ee381af56833df8f98d65f4ca
MATCHES_PINNED_FINGERPRINT  = YES
SECRET_EXTRACTION_CANDIDATES = 1
```

## Result

| Input | Outcome |
|---|---|
| **the real retired key** | **REJECTED** — *"SECRET_KEY is a retired signing key and is permanently prohibited"* |
| an ordinary governed key | ACCEPTED, returned unchanged |
| whitespace only | REJECTED — *"SECRET_KEY is not set"* |
| unset | REJECTED — *"SECRET_KEY is not set"* |
| `***REMOVED_RETIRED_SECRET***` | ACCEPTED |

The tombstone marker is **accepted, deliberately**. It is a history-redaction
marker, not a key that was ever in use. Pinning its fingerprint would expand the
authored behaviour for no security reason, and would invent a requirement that
no governance document states.

```
PROBE_REAL_LITERAL        = REJECTED
PROBE_ORDINARY            = ACCEPTED
PROBE_EMPTY               = REJECTED
PROBE_UNSET               = REJECTED
PROBE_SECRET_TEMP_REMOVED = YES
```

**Caveat recorded honestly:** the wipe overwrites the file's bytes in place and
unlinks it. On an APFS/SSD copy-on-write filesystem an overwrite is not a
guarantee that no prior copy of those 25 bytes remains on the device. The value
is in any case still present in this repository's published git history until
the Gate-5 purge runs — so this caveat changes nothing about the current
exposure, and it is stated rather than glossed.
