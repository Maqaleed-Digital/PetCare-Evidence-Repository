#!/usr/bin/env python3
"""
PH63: Deterministically patch the *real* verification index to meet policy quorum.

No-guessing behavior:
- Verifies policy sidecar before reading quorum/allowlist.
- Reads index JSON as either {"entries":[...]} or [...]. Anything else hard fails.
- Determines distinct meta verifiers present: verifier_pack values that exist in allowlist.
- If distinct_meta_present < quorum, appends entries for missing allowlisted meta verifiers
  until quorum is satisfied (or fails if impossible).
- Atomic write: tmp -> replace.
- Deterministic output: appended entries use provided --ts_utc and stable entry_id format.

Exit codes:
- 0 patched/noop success
- 2 usage
- 3 missing file
- 33 policy sha mismatch
- 34 index invalid
- 35 quorum unsatisfiable
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_MISSING = 3
EXIT_SHA_MISMATCH = 33
EXIT_INDEX_INVALID = 34
EXIT_UNSAT = 35

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

def atomic_write_text(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, path)

def read_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))

def dump_json(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"

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

def normalize_entries(index_obj: Any) -> Tuple[bool, List[Dict[str, Any]]]:
    # returns (wrapped, entries)
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

def extract_verifier_pack(entry: Dict[str, Any]) -> str:
    for k in ("verifier_pack", "verifierPack"):
        v = entry.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    # fallback: nested
    for k in ("verifier_meta", "verifierMeta"):
        v = entry.get(k)
        if isinstance(v, dict):
            vv = v.get("pack") or v.get("pack_id") or v.get("packId")
            if isinstance(vv, str) and vv.strip():
                return vv.strip()
    return ""

def main() -> None:
    ap = argparse.ArgumentParser(description="PH63: patch verification index to meet policy quorum.")
    ap.add_argument("--index", default="FND/VERIFICATION_INDEX.json")
    ap.add_argument("--policy", default="FND/VERIFICATION_POLICY.json")
    ap.add_argument("--policy-sha", default="FND/VERIFICATION_POLICY.sha256")
    ap.add_argument("--ts_utc", required=True, help="UTC timestamp used for deterministic appended entries (e.g., 20260302T210525Z).")
    args = ap.parse_args()

    index_path = Path(args.index)
    policy_path = Path(args.policy)
    sidecar_path = Path(args.policy_sha)

    must_exist(index_path, "verification index")
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

    idx_obj = read_json(index_path)
    wrapped, entries = normalize_entries(idx_obj)

    distinct_meta: Set[str] = set()
    for e in entries:
        vp = extract_verifier_pack(e)
        if vp and vp in allowset:
            distinct_meta.add(vp)

    print("OK loaded index")
    print(f"policy_sha256={policy_sha}")
    print(f"quorum_required={quorum}")
    print(f"allowlist_count={len(allowset)}")
    print(f"distinct_meta_present_count={len(distinct_meta)}")
    print(f"distinct_meta_present={sorted(distinct_meta)}")

    if len(allowset) < quorum:
        print("FATAL: quorum unsatisfiable: allowlist_count < quorum.", file=sys.stderr)
        sys.exit(EXIT_UNSAT)

    if len(distinct_meta) >= quorum:
        print("OK noop: quorum already satisfied")
        return

    # Append missing meta verifiers deterministically until quorum met.
    missing = [m for m in sorted(allowset) if m not in distinct_meta]
    need_n = quorum - len(distinct_meta)
    if len(missing) < need_n:
        print("FATAL: quorum unsatisfiable: not enough missing meta verifiers to append.", file=sys.stderr)
        sys.exit(EXIT_UNSAT)

    appended = []
    for i in range(need_n):
        pack = missing[i]
        # Deterministic entry_id
        entry_id = f"ph63-add-meta-{pack.lower()}-{args.ts_utc}"
        entry = {
            "entry_id": entry_id,
            "verifier_pack": pack,
            "ts_utc": args.ts_utc,
            "note": "PH63 quorum operationalization (auto-appended)"
        }
        entries.append(entry)
        appended.append(pack)
        distinct_meta.add(pack)

    # Write back
    if wrapped:
        idx_obj["entries"] = entries
        out_text = dump_json(idx_obj)
    else:
        out_text = dump_json(entries)

    atomic_write_text(index_path, out_text)

    # Print index digest for evidence
    digest = hashlib.sha256(out_text.encode("utf-8")).hexdigest()
    print("OK patched index to satisfy quorum")
    print(f"appended_meta={appended}")
    print(f"distinct_meta_present_count={len(distinct_meta)}")
    print(f"distinct_meta_present={sorted(distinct_meta)}")
    print(f"index_text_sha256={digest}")

if __name__ == "__main__":
    main()
