#!/usr/bin/env python3
"""Gate-5 armed retired-secret fingerprint scanner.

Detection semantics are identical to the W0-A2 recipe: a blob matches when it
contains a 25-byte window whose SHA-256 equals the pinned fingerprint.

The comparand is derived in-memory from the introducing commit by AST, its
digest is checked against the pinned fingerprint, and it is never printed,
never written to disk and never passed on a command line.
"""
import argparse
import ast
import hashlib
import subprocess
import sys
import threading

FINGERPRINT = "1cdd7efa59d45698ceba9652ee1c22aa7472503ee381af56833df8f98d65f4ca"
INTRODUCING = "5202bb5ffbd6b3085cdeedc68c5e9ea876a0dc96"
GUARD_FILE = "petcare_api/routers/auth.py"


def git(repo, *args, binary=False):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {r.stderr.decode()[:400]}")
    return r.stdout if binary else r.stdout.decode()


def derive_comparand(repo):
    """AST-extract the single module-level SECRET_KEY default from the
    introducing commit. Returns bytes. Never logs the value."""
    src = git(repo, "show", f"{INTRODUCING}:{GUARD_FILE}", binary=True)
    tree = ast.parse(src.decode("utf-8"))
    candidates = []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(t, ast.Name) and t.id == "SECRET_KEY" for t in node.targets):
            continue
        call = node.value
        if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                and call.func.attr == "getenv"):
            continue
        for arg in call.args[1:]:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                candidates.append(arg.value.encode("utf-8"))
    if len(candidates) != 1:
        raise SystemExit(f"SECRET_EXTRACTION_CANDIDATES={len(candidates)} (expected 1)")
    value = candidates[0]
    if hashlib.sha256(value).hexdigest() != FINGERPRINT:
        raise SystemExit("COMPARAND_FINGERPRINT_MISMATCH")
    return value


def confirm_by_fingerprint(content, comparand):
    """Return sorted offsets where a window hashes to the pinned fingerprint."""
    n = len(comparand)
    hits, start = [], 0
    while True:
        i = content.find(comparand, start)
        if i < 0:
            return hits
        if hashlib.sha256(content[i:i + n]).hexdigest() == FINGERPRINT:
            hits.append(i)
        start = i + 1


def enumerate_blobs(repo, revargs):
    """Yield (blob_sha, path) reachable from revargs."""
    p = subprocess.run(["git", "-C", repo, "rev-list", "--objects", *revargs],
                       capture_output=True)
    if p.returncode != 0:
        raise SystemExit(f"rev-list failed: {p.stderr.decode()[:400]}")
    seen = {}
    for line in p.stdout.decode("utf-8", "replace").splitlines():
        sha, _, blob_path = line.partition(" ")
        if blob_path:
            seen.setdefault(sha, blob_path)
    return seen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--comparand-repo", required=True,
                    help="repo that still holds the introducing commit")
    ap.add_argument("--label", required=True)
    ap.add_argument("--max-blob-bytes", type=int, default=200 * 1024 * 1024)
    ap.add_argument("revs", nargs="+")
    a = ap.parse_args()

    comparand = derive_comparand(a.comparand_repo)
    objs = enumerate_blobs(a.repo, a.revs)

    # classify object types
    check = subprocess.run(
        ["git", "-C", a.repo, "cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)"],
        input="\n".join(objs).encode(), capture_output=True)
    blobs = []
    for line in check.stdout.decode().splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[1] == "blob":
            blobs.append((parts[0], int(parts[2])))

    scanned = skipped = 0
    matching_blobs = []
    total_occurrences = 0

    to_read = [(s, sz) for s, sz in blobs if sz <= a.max_blob_bytes]
    skipped = len(blobs) - len(to_read)

    proc = subprocess.Popen(["git", "-C", a.repo, "cat-file", "--batch"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def _feed():
        try:
            for sha, _ in to_read:
                proc.stdin.write(sha.encode() + b"\n")
            proc.stdin.flush()
        finally:
            proc.stdin.close()

    feeder = threading.Thread(target=_feed, daemon=True)
    feeder.start()
    out = proc.stdout
    for _ in to_read:
        header = out.readline()
        if not header:
            break
        parts = header.split()
        sha, size = parts[0].decode(), int(parts[2])
        content = out.read(size)
        out.read(1)
        scanned += 1
        hits = confirm_by_fingerprint(content, comparand)
        if hits:
            matching_blobs.append((sha, objs.get(sha, "<no-path>"), len(hits)))
            total_occurrences += len(hits)
    feeder.join()
    proc.wait()

    paths = sorted({p for _, p, _ in matching_blobs})
    print(f"LABEL                      = {a.label}")
    print(f"REPO                       = {a.repo}")
    print(f"REVS                       = {' '.join(a.revs)}")
    print(f"FINGERPRINT                = {FINGERPRINT}")
    print(f"COMPARAND_LENGTH_BYTES     = {len(comparand)}")
    print(f"OBJECTS_ENUMERATED         = {len(objs)}")
    print(f"BLOBS_TOTAL                = {len(blobs)}")
    print(f"BLOBS_SCANNED              = {scanned}")
    print(f"BLOBS_SKIPPED_OVERSIZE     = {skipped}")
    print(f"MATCHING_BLOBS             = {len(matching_blobs)}")
    print(f"MATCHING_PATHS             = {len(paths)}")
    print(f"TOTAL_OCCURRENCES          = {total_occurrences}")
    print("PATHS:")
    for p in paths:
        print(f"  {p}")
    print("BLOBS:")
    for sha, p, n in sorted(matching_blobs, key=lambda x: (x[1], x[0])):
        print(f"  {sha}  occurrences={n}  {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
