#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import sys
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


def write_json_atomic(path: str, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)


def compute_entry_hash(entry_core: dict) -> str:
    return sha256_hex(canon_json(entry_core).encode("utf-8"))


def fail(msg: str, code: int = 42):
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def is_hex64(s: str) -> bool:
    if not isinstance(s, str) or len(s) != 64:
        return False
    try:
        int(s, 16)
        return True
    except Exception:
        return False


def parse_args_or_env():
    """
    Governed behavior:
    - Primary: argparse (used by closure packs + CI)
    - Fallback: env vars only if invoked with NO CLI args (local smoke test)
    """
    if len(sys.argv) == 1:
        # Env fallback contract (explicit)
        class A:
            pass

        a = A()
        a.index = os.environ.get("PC_INDEX", "FND/VERIFICATION_INDEX.json")
        a.verified_pack = os.environ.get("PC_VERIFIED_PACK", "")
        a.verified_zip_sha256 = os.environ.get("PC_VERIFIED_ZIP_SHA256", "")
        a.verifier_pack = os.environ.get("PC_VERIFIER_PACK", "")
        a.verifier_class = os.environ.get("PC_VERIFIER_CLASS", "independent")
        a.verifier_zip_sha256 = os.environ.get("PC_VERIFIER_ZIP_SHA256", "")
        a.verifier_git_head = os.environ.get("PC_VERIFIER_GIT_HEAD", "")
        a.verifier_git_describe = os.environ.get("PC_VERIFIER_GIT_DESCRIBE", "")
        a.overall_pass = os.environ.get("PC_OVERALL_PASS", "")
        a.ts_utc = os.environ.get("PC_TS_UTC", "")
        return a

    ap = argparse.ArgumentParser()
    ap.add_argument("--index", required=True, help="Path to FND/VERIFICATION_INDEX.json")
    ap.add_argument("--verified_pack", required=True, help="Pack id of the verified pack (e.g., PETCARE-PH43B-CLOSURE)")
    ap.add_argument("--verified_zip_sha256", required=True, help="SHA256 of the verified pack zip (64-hex)")
    ap.add_argument("--verifier_pack", required=True, help="Verifier pack id (e.g., PETCARE-PH44B-CLOSURE)")
    ap.add_argument("--verifier_class", required=True, help="Verifier class: independent|meta")
    ap.add_argument("--verifier_zip_sha256", required=True, help="SHA256 of the verifier pack zip (64-hex)")
    ap.add_argument("--verifier_git_head", required=True)
    ap.add_argument("--verifier_git_describe", required=True)
    ap.add_argument("--overall_pass", required=True, help="true|false (string contract)")
    ap.add_argument("--ts_utc", default="", help="UTC timestamp; if empty, generated")
    return ap.parse_args()


def enforce_ph49_guards(args):
    if getattr(args, "verifier_class", "") not in ("independent", "meta"):
        fail(f"verifier_class invalid: {getattr(args,'verifier_class',None)}")

    vp = getattr(args, "verifier_pack", "") or ""
    vdp = getattr(args, "verified_pack", "") or ""
    if vp and vdp and vp == vdp:
        fail(f"self-attestation forbidden (verifier_pack == verified_pack == {vp})")

    vz = getattr(args, "verified_zip_sha256", "") or ""
    vzr = getattr(args, "verifier_zip_sha256", "") or ""
    if not is_hex64(vz):
        fail("verified_zip_sha256 must be 64-hex")
    if not is_hex64(vzr):
        fail("verifier_zip_sha256 must be 64-hex")

    op = getattr(args, "overall_pass", "") or ""
    if op not in ("true", "false"):
        fail("overall_pass must be 'true' or 'false'")


def main():
    args = parse_args_or_env()
    enforce_ph49_guards(args)

    idx = load_json(args.index)

    if idx.get("schema") != SCHEMA:
        raise SystemExit(f"ERROR: unexpected index schema: {idx.get('schema')}")

    entries = idx.get("entries")
    if not isinstance(entries, list):
        raise SystemExit("ERROR: index.entries must be a list")

    ts = (getattr(args, "ts_utc", "") or "").strip() or now_utc()

    prev_hash = ""
    if entries:
        last = entries[-1]
        prev_hash = (last.get("entry_hash", "") or "")

    # idempotency: block duplicate verifier zip sha
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
        "verifier_class": args.verifier_class,
        "prev_entry_hash": prev_hash,
    }
    entry_hash = compute_entry_hash({k: entry_core[k] for k in [
        "ts_utc","verified_pack","verified_zip_sha256",
        "verifier_pack","verifier_zip_sha256",
        "verifier_git_head","verifier_git_describe",
        "overall_pass","verifier_class","prev_entry_hash"
    ]})

    entry = dict(entry_core)
    entry["entry_hash"] = entry_hash

    if idx.get("created_utc") == "INIT":
        idx["created_utc"] = ts

    entries.append(entry)
    idx["entries"] = entries

    # index_digest is deterministic sha over canonical JSON excluding itself
    idx_core = {"schema": idx["schema"], "created_utc": idx["created_utc"], "entries": idx["entries"]}
    idx["index_digest_sha256"] = sha256_hex(canon_json(idx_core).encode("utf-8"))

    write_json_atomic(args.index, idx)

    print("OK appended")
    print("entry_hash=" + entry_hash)
    print("index_digest_sha256=" + idx["index_digest_sha256"])


if __name__ == "__main__":
    main()