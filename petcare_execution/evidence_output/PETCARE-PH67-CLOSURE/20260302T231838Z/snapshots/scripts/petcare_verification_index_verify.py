#!/usr/bin/env python3
"""
PH62: Verification Index verifier (Trust-grade): integrity + quorum.

Keeps PH61:
- Policy sidecar verified
- meta_verifiers_allowlist + meta_verifiers_quorum enforced
- EXIT_QUORUM_FAIL = 135 when distinct meta verifiers present < quorum

Restores integrity checks:
- Index JSON must be either:
  A) {"entries":[...]} or B) [...]
- Every entry must contain a verifier_pack (extractable via stable key set)
- Index digest (sha256 of file bytes) is always computed and printed
- Optional strict mode validates entries have stable minimal identity:
    - entry_id OR (pack_id + timestamp_utc) must exist (no guessing keys)
  Strict mode is enabled by default; can be disabled via --no_strict.

Exit codes:
- 0 OK
- 2 usage
- 3 missing file
- 33 policy sha mismatch
- 34 index invalid (schema/required fields)
- 135 quorum not met
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_MISSING = 3
EXIT_SHA_MISMATCH = 33
EXIT_INDEX_INVALID = 34
EXIT_QUORUM_FAIL = 135

def verify_index_sidecar(index_path: Path, sidecar_path: Path) -> str:
    must_exist(index_path, "verification index")
    must_exist(sidecar_path, "verification index sha sidecar")
    actual = sha256_file(index_path)
    sidecar = sidecar_path.read_text(encoding="utf-8").strip().split()[0]
    if actual != sidecar:
        print("FATAL: index sha mismatch (sidecar does not match index).", file=sys.stderr)
        print(f"index={index_path}", file=sys.stderr)
        print(f"sidecar={sidecar_path}", file=sys.stderr)
        print(f"actual_sha256={actual}", file=sys.stderr)
        print(f"sidecar_sha256={sidecar}", file=sys.stderr)
        sys.exit(EXIT_SHA_MISMATCH)
    return actual

# -------------------- helpers --------------------

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def must_exist(p: Path, label: str) -> None:
    if not p.exists() or not p.is_file():
        print(f"FATAL: missing {label}: {p}", file=sys.stderr)
        sys.exit(EXIT_MISSING)

def read_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))

def verify_policy_sidecar(policy_path: Path, sidecar_path: Path) -> str:
    must_exist(policy_path, "policy")
    must_exist(sidecar_path, "policy sha sidecar")
    actual = sha256_file(policy_path)
    sidecar = sidecar_path.read_text(encoding="utf-8").strip().split()[0]
    if actual != sidecar:
        print("FATAL: policy sha mismatch (sidecar does not match policy).", file=sys.stderr)
        print(f"actual_sha256={actual}", file=sys.stderr)
        print(f"sidecar_sha256={sidecar}", file=sys.stderr)
        sys.exit(EXIT_SHA_MISMATCH)
    return actual

def autodiscover_index() -> Path:
    base = Path("FND")
    if not base.exists():
        print("FATAL: FND/ directory not found; cannot autodiscover index.", file=sys.stderr)
        sys.exit(EXIT_MISSING)

    matches = sorted(
        p for p in base.rglob("*.json")
        if "VERIFICATION" in p.name.upper() and "INDEX" in p.name.upper()
    )
    if len(matches) == 1:
        return matches[0]
    print("FATAL: could not autodiscover a single verification index JSON.", file=sys.stderr)
    print(f"matches_found={len(matches)}", file=sys.stderr)
    for m in matches[:50]:
        print(f"match={m}", file=sys.stderr)
    print("Provide explicit --index <path>.", file=sys.stderr)
    sys.exit(EXIT_MISSING)

def extract_entries(index_obj: Any) -> List[Dict[str, Any]]:
    if isinstance(index_obj, dict) and "entries" in index_obj:
        entries = index_obj["entries"]
    else:
        entries = index_obj

    if not isinstance(entries, list) or any(not isinstance(e, dict) for e in entries):
        print("FATAL: verification index entries must be list[dict] (or {'entries': list[dict]}).", file=sys.stderr)
        sys.exit(EXIT_INDEX_INVALID)
    return entries  # type: ignore[return-value]

def extract_verifier_pack(entry: Dict[str, Any]) -> str:
    for k in ("verifier_pack", "verifierPack", "verifier", "verifier_id", "verifierId"):
        v = entry.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()

    for k in ("verifier_meta", "verifierMeta", "verifier_info", "verifierInfo"):
        v = entry.get(k)
        if isinstance(v, dict):
            for kk in ("pack", "pack_id", "packId", "verifier_pack"):
                vv = v.get(kk)
                if isinstance(vv, str) and vv.strip():
                    return vv.strip()

    print("FATAL: cannot extract verifier_pack from entry (schema unknown).", file=sys.stderr)
    print(f"entry_keys={sorted(entry.keys())}", file=sys.stderr)
    sys.exit(EXIT_INDEX_INVALID)

def extract_identity(entry: Dict[str, Any]) -> Tuple[str, str]:
    """
    Strict minimal identity:
      - Prefer entry_id (or entryId)
      - Else require (pack_id + timestamp_utc) with common key variants
    Returns (kind, value) for logging/debug.
    """
    for k in ("entry_id", "entryId", "id"):
        v = entry.get(k)
        if isinstance(v, str) and v.strip():
            return ("entry_id", v.strip())

    pack = None
    ts = None
    for k in ("pack_id", "packId", "pack", "verifier_pack", "verified_pack"):
        v = entry.get(k)
        if isinstance(v, str) and v.strip():
            pack = v.strip()
            break

    for k in ("timestamp_utc", "timestampUtc", "ts_utc", "tsUtc"):
        v = entry.get(k)
        if isinstance(v, str) and v.strip():
            ts = v.strip()
            break

    if pack and ts:
        return ("pack_ts", f"{pack}|{ts}")

    print("FATAL: entry missing minimal identity (need entry_id OR pack_id+timestamp_utc).", file=sys.stderr)
    print(f"entry_keys={sorted(entry.keys())}", file=sys.stderr)
    sys.exit(EXIT_INDEX_INVALID)

def require_unique_identities(entries: List[Dict[str, Any]]) -> None:
    seen: Set[str] = set()
    for e in entries:
        _, ident = extract_identity(e)
        if ident in seen:
            print("FATAL: duplicate entry identity detected (integrity fail).", file=sys.stderr)
            print(f"duplicate_identity={ident}", file=sys.stderr)
            sys.exit(EXIT_INDEX_INVALID)
        seen.add(ident)

# -------------------- main --------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="PH62: verify verification index integrity + enforce meta verifier quorum.")
    ap.add_argument("--index", default="", help="Path to verification index JSON; if omitted autodiscovers under FND.")
    ap.add_argument("--policy", default="FND/VERIFICATION_POLICY.json")
    ap.add_argument("--policy-sha", default="FND/VERIFICATION_POLICY.sha256")
    ap.add_argument("--no_strict", action="store_true", help="Disable strict identity checks (PH62 strict is default).")
    args = ap.parse_args()

    policy_path = Path(args.policy)
    policy_sha_path = Path(args.policy_sha)
    policy_sha = verify_policy_sidecar(policy_path, policy_sha_path)
    policy = read_json(policy_path)

    allowlist = policy.get("meta_verifiers_allowlist", [])
    if not isinstance(allowlist, list) or any((not isinstance(x, str) or not x.strip()) for x in allowlist):
        print("FATAL: meta_verifiers_allowlist must be list[str].", file=sys.stderr)
        sys.exit(EXIT_INDEX_INVALID)
    allowset: Set[str] = set(x.strip() for x in allowlist)

    quorum = policy.get("meta_verifiers_quorum", 1)
    if quorum is None:
        quorum = 1
    if not isinstance(quorum, int) or quorum < 1:
        print("FATAL: meta_verifiers_quorum must be int>=1 (or omitted).", file=sys.stderr)
        sys.exit(EXIT_INDEX_INVALID)

    index_path = Path(args.index) if args.index.strip() else autodiscover_index()
    # PH67: require sidecar for real index path under FND/VERIFICATION_INDEX.json
    if str(index_path).replace("\\", "/") == "FND/VERIFICATION_INDEX.json":
        _ = verify_index_sidecar(index_path, Path("FND/VERIFICATION_INDEX.sha256"))
    else:
        must_exist(index_path, "verification index")
    index_bytes = index_path.read_bytes()
    index_digest = hashlib.sha256(index_bytes).hexdigest()

    index_obj = read_json(index_path)
    entries = extract_entries(index_obj)

    # Integrity: schema + required fields
    distinct_meta: Set[str] = set()
    for e in entries:
        vp = extract_verifier_pack(e)
        if vp in allowset:
            distinct_meta.add(vp)

    if not args.no_strict:
        require_unique_identities(entries)

    # Emit stable summary
    print(f"OK verification index loaded — entries_count={len(entries)}")
    print(f"index_digest_sha256={index_digest}")

    # Quorum enforcement
    if len(distinct_meta) < quorum:
        print("FAIL quorum not met for meta verifiers.", file=sys.stderr)
        print(f"policy_sha256={policy_sha}", file=sys.stderr)
        print(f"allowlist_count={len(allowset)}", file=sys.stderr)
        print(f"quorum_required={quorum}", file=sys.stderr)
        print(f"distinct_meta_present_count={len(distinct_meta)}", file=sys.stderr)
        print(f"distinct_meta_present={sorted(distinct_meta)}", file=sys.stderr)
        sys.exit(EXIT_QUORUM_FAIL)

    print("OK verification index integrity PASS")
    print(f"policy_sha256={policy_sha}")
    print(f"allowlist_count={len(allowset)}")
    print(f"quorum_required={quorum}")
    print(f"distinct_meta_present_count={len(distinct_meta)}")
    print(f"distinct_meta_present={sorted(distinct_meta)}")
    sys.exit(EXIT_OK)

if __name__ == "__main__":
    main()
