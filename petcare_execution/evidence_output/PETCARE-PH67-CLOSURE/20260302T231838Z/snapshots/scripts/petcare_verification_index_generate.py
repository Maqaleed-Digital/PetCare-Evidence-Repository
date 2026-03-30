#!/usr/bin/env python3
"""
PH65: Deterministic generator for FND/VERIFICATION_INDEX.json.

Design goals:
- Idempotent: running repeatedly yields identical file content.
- No-guessing: policy sidecar must match before using allowlist/quorum.
- Stable identity: entries must have minimal identity in strict mode:
    entry_id OR (verifier_pack/verified_pack + ts_utc/timestamp_utc)
- Ensures quorum satisfiable in output by including at least quorum distinct meta verifiers
  from policy allowlist (if allowlist_count >= quorum).
- Deterministic ordering: stable sort by (ts_utc, verifier_pack, entry_id) where present.
- Supports index format: {"entries":[...]} OR [...]. Preserves wrapper style.

Modes:
- --write : write generated result to index path (atomic).
- --check : do not write; exit non-zero if generation would change file.

Exit codes:
- 0 success / no drift
- 33 policy sha mismatch
- 34 index invalid
- 35 quorum unsatisfiable (allowlist_count < quorum)
- 65 drift detected in --check mode
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional, Set

EXIT_OK = 0
EXIT_SHA_MISMATCH = 33
EXIT_INDEX_INVALID = 34
EXIT_UNSAT = 35
EXIT_DRIFT = 65

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def must_exist(p: Path, label: str) -> None:
    if not p.exists() or not p.is_file():
        raise SystemExit(f"FATAL: missing {label}: {p}")

def read_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))

def dump_json(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"

def atomic_write_text(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, path)

def verify_policy_sidecar(policy_path: Path, sidecar_path: Path) -> str:
    must_exist(policy_path, "policy")
    must_exist(sidecar_path, "policy sha sidecar")
    actual = sha256_file(policy_path)
    sidecar = sidecar_path.read_text(encoding="utf-8").strip().split()[0]
    if actual != sidecar:
        print("FATAL: policy sha mismatch (sidecar != policy).", file=sys.stderr)
        print(f"actual_sha256={actual}", file=sys.stderr)
        print(f"sidecar_sha256={sidecar}", file=sys.stderr)
        sys.exit(EXIT_SHA_MISMATCH)
    return actual

def normalize_index(index_obj: Any) -> Tuple[bool, List[Dict[str, Any]]]:
    if isinstance(index_obj, dict) and "entries" in index_obj:
        entries = index_obj["entries"]
        wrapped = True
    else:
        entries = index_obj
        wrapped = False
    if not isinstance(entries, list) or any(not isinstance(e, dict) for e in entries):
        print("FATAL: index must be list[dict] or {'entries': list[dict]}.", file=sys.stderr)
        sys.exit(EXIT_INDEX_INVALID)
    return wrapped, entries  # type: ignore[return-value]

def get_str(d: Dict[str, Any], keys: Tuple[str, ...]) -> Optional[str]:
    for k in keys:
        v = d.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None

def extract_verifier_pack(entry: Dict[str, Any]) -> Optional[str]:
    return get_str(entry, ("verifier_pack", "verifierPack", "verified_pack", "verifiedPack"))

def extract_ts(entry: Dict[str, Any]) -> Optional[str]:
    return get_str(entry, ("ts_utc", "tsUtc", "timestamp_utc", "timestampUtc"))

def extract_entry_id(entry: Dict[str, Any]) -> Optional[str]:
    return get_str(entry, ("entry_id", "entryId", "id"))

def identity_strict(entry: Dict[str, Any]) -> str:
    eid = extract_entry_id(entry)
    if eid:
        return f"entry_id:{eid}"
    vp = extract_verifier_pack(entry)
    ts = extract_ts(entry)
    if vp and ts:
        return f"pack_ts:{vp}|{ts}"
    print("FATAL: entry missing minimal identity (entry_id OR verifier_pack+ts_utc).", file=sys.stderr)
    print(f"entry_keys={sorted(entry.keys())}", file=sys.stderr)
    sys.exit(EXIT_INDEX_INVALID)

def sort_key(entry: Dict[str, Any]) -> Tuple[str, str, str]:
    ts = extract_ts(entry) or ""
    vp = extract_verifier_pack(entry) or ""
    eid = extract_entry_id(entry) or ""
    return (ts, vp, eid)

def build_missing_meta_entries(missing_packs: List[str], ts_utc: str) -> List[Dict[str, Any]]:
    out = []
    for pack in missing_packs:
        out.append({
            "entry_id": f"ph65-gen-meta-{pack.lower()}-{ts_utc}",
            "verifier_pack": pack,
            "ts_utc": ts_utc,
            "note": "PH65 deterministic generation (auto-included)"
        })
    return out

def main() -> None:
    ap = argparse.ArgumentParser(description="PH65 deterministic generator for VERIFICATION_INDEX.json")
    ap.add_argument("--index", default="FND/VERIFICATION_INDEX.json")
    ap.add_argument("--policy", default="FND/VERIFICATION_POLICY.json")
    ap.add_argument("--policy-sha", default="FND/VERIFICATION_POLICY.sha256")
    ap.add_argument("--ts_utc", required=True, help="UTC timestamp used only if entries must be added (deterministic within run).")
    ap.add_argument("--check", action="store_true", help="Check mode: fail if generated output differs.")
    ap.add_argument("--write", action="store_true", help="Write mode: update index atomically if needed.")
    args = ap.parse_args()

    if args.check and args.write:
        print("FATAL: choose exactly one of --check or --write.", file=sys.stderr)
        sys.exit(EXIT_INDEX_INVALID)
    if not args.check and not args.write:
        print("FATAL: must pass --check or --write.", file=sys.stderr)
        sys.exit(EXIT_INDEX_INVALID)

    index_path = Path(args.index)
    policy_path = Path(args.policy)
    sidecar_path = Path(args.policy_sha)

    must_exist(index_path, "index")
    policy_sha = verify_policy_sidecar(policy_path, sidecar_path)
    policy = read_json(policy_path)

    allow = policy.get("meta_verifiers_allowlist", [])
    quorum = policy.get("meta_verifiers_quorum", 1)
    if quorum is None:
        quorum = 1

    if not isinstance(allow, list) or any((not isinstance(x, str) or not x.strip()) for x in allow):
        print("FATAL: meta_verifiers_allowlist invalid.", file=sys.stderr)
        sys.exit(EXIT_INDEX_INVALID)
    if not isinstance(quorum, int) or quorum < 1:
        print("FATAL: meta_verifiers_quorum invalid.", file=sys.stderr)
        sys.exit(EXIT_INDEX_INVALID)

    allowset: Set[str] = set(x.strip() for x in allow)
    if len(allowset) < quorum:
        print("FATAL: quorum unsatisfiable: allowlist_count < quorum.", file=sys.stderr)
        print(f"allowlist_count={len(allowset)} quorum={quorum}", file=sys.stderr)
        sys.exit(EXIT_UNSAT)

    raw = index_path.read_text(encoding="utf-8")
    idx_obj = json.loads(raw)
    wrapped, entries = normalize_index(idx_obj)

    # strict identity validation + de-dupe by identity (keep first occurrence deterministically after sort)
    validated: List[Dict[str, Any]] = []
    for e in entries:
        _ = identity_strict(e)
        validated.append(e)

    # Determine distinct meta present
    distinct_meta: Set[str] = set()
    for e in validated:
        vp = extract_verifier_pack(e)
        if vp and vp in allowset:
            distinct_meta.add(vp)

    # Ensure quorum satisfied by including missing meta verifiers
    need_n = max(0, quorum - len(distinct_meta))
    added: List[str] = []
    if need_n > 0:
        missing = [m for m in sorted(allowset) if m not in distinct_meta]
        missing = missing[:need_n]
        added = missing[:]
        validated.extend(build_missing_meta_entries(missing, args.ts_utc))
        distinct_meta.update(missing)

    # Deterministic ordering
    validated_sorted = sorted(validated, key=sort_key)

    # Deterministic de-dup by strict identity after sort
    seen: Set[str] = set()
    deduped: List[Dict[str, Any]] = []
    for e in validated_sorted:
        ident = identity_strict(e)
        if ident in seen:
            continue
        seen.add(ident)
        deduped.append(e)

    out_obj: Any
    if wrapped:
        out_obj = dict(idx_obj)
        out_obj["schema"] = "petcare.verification_index.v1"
        out_obj["schema_version"] = 1
        out_obj["entries"] = deduped
    else:
        out_obj = deduped

    out_text = dump_json(out_obj)

    old_sha = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    new_sha = hashlib.sha256(out_text.encode("utf-8")).hexdigest()

    print("OK generation computed")
    print(f"policy_sha256={policy_sha}")
    print(f"old_index_text_sha256={old_sha}")
    print(f"new_index_text_sha256={new_sha}")
    print(f"quorum_required={quorum}")
    print(f"distinct_meta_present_count={len(distinct_meta)}")
    print(f"distinct_meta_present={sorted(distinct_meta)}")
    print(f"added_meta={added}")
    print(f"entries_out_count={len(deduped)}")

    if raw == out_text:
        print("OK no change")
        return

    if args.check:
        print("FAIL drift detected: generated index differs from repo index.", file=sys.stderr)
        sys.exit(EXIT_DRIFT)

    # write mode
    atomic_write_text(index_path, out_text)
    print("OK wrote index (atomic)")

if __name__ == "__main__":
    main()
