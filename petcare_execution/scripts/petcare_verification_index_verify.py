#!/usr/bin/env python3
import argparse
import hashlib
import json
import sys

SCHEMA = "petcare.verification_index.v1"

def sha256_hex(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()

def canon_json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def compute_entry_hash(entry_core: dict) -> str:
    return sha256_hex(canon_json(entry_core).encode("utf-8"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", default="FND/VERIFICATION_INDEX.json")
    args = ap.parse_args()

    idx_path = args.index
    idx = json.load(open(idx_path, "r", encoding="utf-8"))

    if idx.get("schema") != SCHEMA:
        print(f"ERROR: schema mismatch: {idx.get('schema')}", file=sys.stderr)
        raise SystemExit(2)

    created = idx.get("created_utc")
    if not isinstance(created, str) or not created:
        print("ERROR: created_utc missing/invalid", file=sys.stderr)
        raise SystemExit(3)

    entries = idx.get("entries")
    if not isinstance(entries, list):
        print("ERROR: entries must be list", file=sys.stderr)
        raise SystemExit(4)

    # Validate chain + hashes
    prev = ""
    for i, e in enumerate(entries):
        if not isinstance(e, dict):
            print(f"ERROR: entry[{i}] not object", file=sys.stderr)
            raise SystemExit(10)

        need_keys = [
            "ts_utc","verified_pack","verified_zip_sha256",
            "verifier_pack","verifier_zip_sha256",
            "verifier_git_head","verifier_git_describe",
            "overall_pass","prev_entry_hash","entry_hash"
        ]
        for k in need_keys:
            if k not in e:
                print(f"ERROR: entry[{i}] missing key {k}", file=sys.stderr)
                raise SystemExit(11)

        if e["prev_entry_hash"] != prev:
            print(f"ERROR: entry[{i}] prev_entry_hash mismatch", file=sys.stderr)
            print(f"want={prev}", file=sys.stderr)
            print(f"got ={e['prev_entry_hash']}", file=sys.stderr)
            raise SystemExit(12)

        entry_core = {k: e[k] for k in [
            "ts_utc","verified_pack","verified_zip_sha256",
            "verifier_pack","verifier_zip_sha256",
            "verifier_git_head","verifier_git_describe",
            "overall_pass","prev_entry_hash"
        ]}
        want_hash = compute_entry_hash(entry_core)
        if e["entry_hash"] != want_hash:
            print(f"ERROR: entry[{i}] entry_hash mismatch", file=sys.stderr)
            print(f"want={want_hash}", file=sys.stderr)
            print(f"got ={e['entry_hash']}", file=sys.stderr)
            raise SystemExit(13)

        prev = e["entry_hash"]

    # Validate index_digest_sha256
    idx_digest = idx.get("index_digest_sha256")
    if not isinstance(idx_digest, str) or not idx_digest:
        print("ERROR: index_digest_sha256 missing/invalid", file=sys.stderr)
        raise SystemExit(20)

    idx_core = {"schema": idx["schema"], "created_utc": idx["created_utc"], "entries": idx["entries"]}
    want_digest = sha256_hex(canon_json(idx_core).encode("utf-8"))
    if idx_digest != want_digest:
        print("ERROR: index_digest_sha256 mismatch", file=sys.stderr)
        print(f"want={want_digest}", file=sys.stderr)
        print(f"got ={idx_digest}", file=sys.stderr)
        raise SystemExit(21)

    print("OK verification index integrity PASS")
    print(f"entries_count={len(entries)}")
    print(f"head_entry_hash={prev if entries else ''}")
    print(f"index_digest_sha256={want_digest}")

if __name__ == "__main__":
    main()
