# Protection evidence — normalization recipe and provenance

## Recipe

```
PROTECTION_NORMALIZATION_RECIPE = jq -S -c . before.json | shasum -a 256
```

## Digests

| file | raw sha256 | `jq -S -c` sha256 |
|---|---|---|
| `PROTECTION_BEFORE.json` | `4c3a4da99341408a62ffe84bdc0b091b14ac81585adbb082114fbb635767d446` | `c57329523ab4fbd6638e66d06f58fcfdc60c7caf4d7b8a5eafed22b5c14f4049` |
| `PROTECTION_AFTER.json` | `4c3a4da99341408a62ffe84bdc0b091b14ac81585adbb082114fbb635767d446` | `c57329523ab4fbd6638e66d06f58fcfdc60c7caf4d7b8a5eafed22b5c14f4049` |
| `PROTECTION_RESTORE.json` | `c8e2c945fdd232cc39bdd66a1da230763bc9eca2256146c1f99577445dc2a810` | `021cd2a1c0e015ce8e610c00a214ad34027fad21f218c255e2be82057bce123d` |
| `PROTECTION_WINDOW.json` | `2ecee55d525a2bc48c1f271f8c48408e848ea513e3cb0bcb581904c409162d55` | `4c9aaa34587aad17831b8b7915ee04f4b724d8183b67b83be29f5634572c475b` |

```
PROTECTION_BEFORE_RAW_SHA256 = c57329523ab4fbd6638e66d06f58fcfdc60c7caf4d7b8a5eafed22b5c14f4049
```

All four files parse as valid JSON.

## `before` and `after` are the same bytes

`PROTECTION_BEFORE.json` and `PROTECTION_AFTER.json` have **identical digests**.
The protection state after the window is not merely equivalent to the state
before it — it is the same response, byte for byte.

```
PROTECTION_RESTORED_IDENTICAL = YES
```

## What this digest must not be compared against

This is the digest of the **raw API response**, normalised only by key ordering.
Earlier packs recorded digests over a **writable-fields-only** projection.
Those are different measurements over different byte sequences and will not
match. Do not treat a mismatch against an older writable-fields hash as a
finding.

Acceptance for protection is **semantic, field-for-field** — see
`PROTECTION_FIELD_COMPARISON.md`.
