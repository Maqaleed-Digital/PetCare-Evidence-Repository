#!/usr/bin/env python3
import argparse
import hashlib
import json
import sys
import re

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
    edges = []  # PH48 lineage graph: verifier_pack -> verified_pack
    seen_pairs = set()
    for i, e in enumerate(entries):
        if not isinstance(e, dict):
            print(f"ERROR: entry[{i}] not object", file=sys.stderr)
            raise SystemExit(10)

        need_keys = [
            "ts_utc","verified_pack","verified_zip_sha256",
            "verifier_pack","verifier_zip_sha256",
            "verifier_git_head","verifier_git_describe",
            "overall_pass","verifier_class","prev_entry_hash","entry_hash"
        ]
        for k in need_keys:
            if k not in e:
                print(f"ERROR: entry[{i}] missing key {k}", file=sys.stderr)
                raise SystemExit(11)

        # === PH48_VERIFIER_CLASS_HARDENING ===
        def _is_hex64(s: str) -> bool:
            s = (s or "").strip()
            if len(s) != 64:
                return False
            try:
                int(s, 16)
                return True
            except Exception:
                return False

        verified_pack = (e.get("verified_pack") or "").strip()
        verifier_pack = (e.get("verifier_pack") or "").strip()
        if not verified_pack or not verifier_pack:
            print(f"ERROR: entry[{i}] pack ids missing/empty", file=sys.stderr)
            raise SystemExit(111)

        if verifier_pack == verified_pack:
            print(f"ERROR: entry[{i}] self-attestation forbidden (verifier_pack == verified_pack == {verifier_pack})", file=sys.stderr)
            raise SystemExit(112)

        vc = (e.get("verifier_class") or "").strip()
        if vc not in ("independent", "meta"):
            print(f"ERROR: entry[{i}] invalid verifier_class={vc!r}", file=sys.stderr)
            raise SystemExit(113)

        if not _is_hex64(e.get("verified_zip_sha256")):
            print(f"ERROR: entry[{i}] invalid verified_zip_sha256 (must be 64-hex)", file=sys.stderr)
            raise SystemExit(114)

        if not _is_hex64(e.get("verifier_zip_sha256")):
            print(f"ERROR: entry[{i}] invalid verifier_zip_sha256 (must be 64-hex)", file=sys.stderr)
            raise SystemExit(115)
        # === END PH48_VERIFIER_CLASS_HARDENING ===


        # PH48: record lineage edge + ban duplicates
        pair = (verifier_pack, verified_pack)
        if pair in seen_pairs:
            print(f"ERROR: entry[{i}] duplicate lineage edge forbidden: {verifier_pack} -> {verified_pack}", file=sys.stderr)
            raise SystemExit(116)
        seen_pairs.add(pair)
        edges.append(pair)

        if e["prev_entry_hash"] != prev:
            print(f"ERROR: entry[{i}] prev_entry_hash mismatch", file=sys.stderr)
            print(f"want={prev}", file=sys.stderr)
            print(f"got ={e['prev_entry_hash']}", file=sys.stderr)
            raise SystemExit(12)

        entry_core = {k: e[k] for k in [
            "ts_utc","verified_pack","verified_zip_sha256",
            "verifier_pack","verifier_zip_sha256",
            "verifier_git_head","verifier_git_describe",
            "overall_pass","verifier_class","prev_entry_hash"
        ]}
        want_hash = compute_entry_hash(entry_core)
        if e["entry_hash"] != want_hash:
            print(f"ERROR: entry[{i}] entry_hash mismatch", file=sys.stderr)
            print(f"want={want_hash}", file=sys.stderr)
            print(f"got ={e['entry_hash']}", file=sys.stderr)
            raise SystemExit(13)

        prev = e["entry_hash"]


    # PH48: lineage DAG enforcement (no cycles)
    from collections import defaultdict, deque
    g = defaultdict(list)
    indeg = defaultdict(int)
    nodes = set()

    for a, b in edges:
        nodes.add(a); nodes.add(b)
        g[a].append(b)
        indeg[b] += 1
        indeg.setdefault(a, indeg.get(a, 0))

    q = deque([n for n in nodes if indeg.get(n, 0) == 0])
    seen = 0
    while q:
        n = q.popleft()
        seen += 1
        for nxt in g.get(n, []):
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                q.append(nxt)

    if nodes and seen != len(nodes):
        print("ERROR: lineage cycle detected in verifier_pack -> verified_pack graph", file=sys.stderr)
        raise SystemExit(117)

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

    # === PH51 POLICY CHECKS ===
    # Governance rules layered on top of integrity:
    # R1: meta must verify a verifier-pack (structural: verified_pack appears somewhere as verifier_pack)
    # R2: independent-first (first time a pack appears as verified_pack must be independent)
    # R3: no true->false downgrade for same verified_pack
    # R4: verifier_pack naming sanity

    def _ph51_fail(msg: str, code: int = 130):
        print(f"ERROR: {msg}", file=sys.stderr)
        raise SystemExit(code)

    pack_re = re.compile(r"^PETCARE-[A-Z0-9]+-CLOSURE$")

    # R4: verifier_pack naming sanity
    for i, e in enumerate(entries):
        vp = e.get("verifier_pack", "")
        if not isinstance(vp, str) or not pack_re.match(vp):
            _ph51_fail(f"PH51: entry[{i}] verifier_pack invalid: {vp}", 131)

    # Structural set: packs that have acted as verifiers anywhere in index
    acted_as_verifier = set()
    for e in entries:
        acted_as_verifier.add(e.get("verifier_pack"))

    first_class = {}
    ever_true = {}

    for i, e in enumerate(entries):
        p = e.get("verified_pack")
        c = e.get("verifier_class")
        op = e.get("overall_pass")

        # R2: independent-first
        if p not in first_class:
            first_class[p] = c
            if c != "independent":
                _ph51_fail(f"PH51: pack {p} first verification must be independent (got {c})", 132)

        # R3: no true->false downgrade
        if p not in ever_true:
            ever_true[p] = (op == "true")
        else:
            if ever_true[p] and op == "false":
                _ph51_fail(f"PH51: pack {p} cannot downgrade from true to false", 133)
            if op == "true":
                ever_true[p] = True

        # R1: meta must verify a verifier-pack (structural)
        if c == "meta":
            if p not in acted_as_verifier:
                _ph51_fail(f"PH51: meta verifier must verify a verifier-pack; {p} never acts as verifier_pack in index", 134)

    # === END PH51 POLICY CHECKS ===


    
    # === PH52_META_ALLOWLIST_POLICY ===
    # Model A: only allow listed verifier_pack to act as verifier_class=meta.
    POLICY_SCHEMA = "petcare.verification_policy.v1"
    policy_path = "FND/VERIFICATION_POLICY.json"
    policy_sha_path = "FND/VERIFICATION_POLICY.sha256"

    if not isinstance(entries, list):
        print("ERROR: entries must be list (PH52 precondition)", file=sys.stderr)
        raise SystemExit(140)

    # Require policy + sha
    try:
        pol_raw = open(policy_path, "rb").read()
    except Exception:
        print(f"ERROR: PH52: missing required policy file: {policy_path}", file=sys.stderr)
        raise SystemExit(141)

    try:
        pol_sha = open(policy_sha_path, "r", encoding="utf-8").read().strip()
    except Exception:
        print(f"ERROR: PH52: missing required policy sha file: {policy_sha_path}", file=sys.stderr)
        raise SystemExit(142)

    want_pol_sha = sha256_hex(pol_raw)
    if pol_sha != want_pol_sha:
        print("ERROR: PH52: policy sha mismatch", file=sys.stderr)
        print(f"want={want_pol_sha}", file=sys.stderr)
        print(f"got ={pol_sha}", file=sys.stderr)
        raise SystemExit(143)

    try:
        policy = json.loads(pol_raw.decode("utf-8"))
    except Exception as e:
        print(f"ERROR: PH52: policy JSON invalid: {e}", file=sys.stderr)
        raise SystemExit(144)

    if policy.get("schema") != POLICY_SCHEMA:
        print(f"ERROR: PH52: policy schema mismatch: {policy.get('schema')}", file=sys.stderr)
        raise SystemExit(145)

    allow = policy.get("meta_verifiers_allowlist")
    if not isinstance(allow, list):
        print("ERROR: PH52: meta_verifiers_allowlist must be list", file=sys.stderr)
        raise SystemExit(146)

    allow_set = set([x for x in allow if isinstance(x, str) and x])

    # Enforce: meta verifier must be allowlisted
    # (PH51 already enforces other constraints, including independent-first and naming regex.)
    for i, e in enumerate(entries):
        vc = e.get("verifier_class", "")
        vp = e.get("verifier_pack", "")
        if vc == "meta":
            if vp not in allow_set:
                print(f"ERROR: PH52: verifier_pack not allowlisted for meta: {vp} (entry[{i}])", file=sys.stderr)
                raise SystemExit(133)
    # === END PH52_META_ALLOWLIST_POLICY ===

    print("OK verification index integrity PASS")
    print(f"entries_count={len(entries)}")
    print(f"head_entry_hash={prev if entries else ''}")
    print(f"index_digest_sha256={want_digest}")

if __name__ == "__main__":
    main()
