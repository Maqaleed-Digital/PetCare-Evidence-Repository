#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
from datetime import datetime, timezone

SCHEMA = "petcare.verification_index.v1"

def sha256_hex(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()

def canon_json(obj) -> str:
    # Deterministic JSON string (stable key ordering, stable separators)
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json(path: str, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)

def compute_entry_hash(entry_without_hash: dict) -> str:
    return sha256_hex(canon_json(entry_without_hash).encode("utf-8"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", required=True, help="Path to FND/VERIFICATION_INDEX.json")
    ap.add_argument("--verified_pack", required=True, help="Pack id of the verified pack (e.g., PETCARE-PH43B-CLOSURE)")
    ap.add_argument("--verified_zip_sha256", required=True, help="SHA256 of the verified pack zip (from PH44B manifest input_zip.sha256)")
    ap.add_argument("--verifier_pack", required=True, help="Verifier pack id (e.g., PETCARE-PH44B-CLOSURE)")
    ap.add_argument("--verifier_zip_sha256", required=True, help="SHA256 of the verifier pack zip (zip sidecar value)")
    ap.add_argument("--verifier_git_head", required=True)
    ap.add_argument("--verifier_git_describe", required=True)
    ap.add_argument("--overall_pass", required=True, choices=["true","false"])
    ap.add_argument("--ts_utc", default="", help="UTC timestamp; if empty, generated")
    args = ap.parse_args()

    idx = load_json(args.index)

    if idx.get("schema") != SCHEMA:
        raise SystemExit(f"ERROR: unexpected index schema: {idx.get('schema')}")

    entries = idx.get("entries")
    if not isinstance(entries, list):
        raise SystemExit("ERROR: index.entries must be a list")

    ts = args.ts_utc.strip() or now_utc()

    prev_hash = ""
    if entries:
        last = entries[-1]
        prev_hash = last.get("entry_hash", "") or ""

    # Prevent duplicate verifier zip sha append (idempotency)
    for e in entries:
        if e.get("verifier_zip_sha256") == args.verifier_zip_sha256:
            raise SystemExit("ERROR: verifier_zip_sha256 already indexed (duplicate append blocked)")

    entry_core = {
        "ts_utc": ts,
        "verified_pack": args.verified_pack,
        "verified_zip_sha256": args.verified_zip_sha256,
        "verifier_pack": args.verifier_pack,
        "verifier_zip_sha256": args.verifier_zip_sha256,
        "verifier_git_head": args.verifier_git_head,
        "verifier_git_describe": args.verifier_git_describe,
        "overall_pass": args.overall_pass,
        "prev_entry_hash": prev_hash
    }
    entry_hash = compute_entry_hash(entry_core)

    entry = dict(entry_core)
    entry["entry_hash"] = entry_hash

    if idx.get("created_utc") == "INIT":
        idx["created_utc"] = ts

    entries.append(entry)
    idx["entries"] = entries

    # index_digest is deterministic sha over canonical JSON excluding itself
    idx_core = {"schema": idx["schema"], "created_utc": idx["created_utc"], "entries": idx["entries"]}
    idx["index_digest_sha256"] = sha256_hex(canon_json(idx_core).encode("utf-8"))

    write_json(args.index, idx)
    print("OK appended")
    print("entry_hash=" + entry_hash)
    print("index_digest_sha256=" + idx["index_digest_sha256"])

if __name__ == "__main__":
    main()
