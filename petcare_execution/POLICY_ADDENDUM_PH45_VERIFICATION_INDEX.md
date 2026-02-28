# POLICY ADDENDUM — PH45 Verification Index & Enforcement

This addendum introduces the **Verification Index Registry** and the **Verification Policy Gate**.

## 1) Verification Index Registry (Append-Only, Hash-Linked)

A deterministic JSON ledger at:

- `FND/VERIFICATION_INDEX.json`

The ledger contains append-only `entries[]`, each hash-linked via:

- `prev_entry_hash`
- `entry_hash` = SHA256(canonical JSON of the entry fields excluding entry_hash)

The index also contains:

- `index_digest_sha256` = SHA256(canonical JSON of the index excluding index_digest_sha256)

## 2) Verification Policy Rule (Production Packs)

Any **Production Pack** (PH43-A or later) MUST:

1) Have a downstream **PH44B verification** that reports `overall_pass=true`
2) Appear in `FND/VERIFICATION_INDEX.json` with:
   - `verified_zip_sha256` matching the production pack zip sha256
   - `overall_pass=true`
3) Be enforceable via gate script:

- `scripts/petcare_verification_policy_check.sh <PROD_PACK_ZIP>`

If the gate fails, the pack is **non-compliant**.

## 3) Determinism & Governance

- The index append is performed only by `scripts/petcare_verification_index_append.py`
- The index must not be manually edited (no mutation drift)
- PH45 closure pack snapshots scripts + index + sha list + zip + sidecar
