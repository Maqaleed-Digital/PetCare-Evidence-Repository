import ast, hashlib, subprocess, sys
BASE, HEAD = sys.argv[1], sys.argv[2]
FILES = ["petcare_api/tests/test_epc_d2h_x30_establishment_licence.py", "petcare_api/tests/test_epc_d2h_establishment_licence_postgres.py"]
def asserts(rev, f):
    src = subprocess.run(["git", "show", f"{rev}:{f}"], capture_output=True, text=True, check=True).stdout
    lines = src.splitlines()
    out = []
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.Assert) or (isinstance(n, ast.With) and any("raises" in ast.unparse(i.context_expr) for i in n.items)):
            seg = "\n".join(lines[n.lineno - 1:n.end_lineno]) if isinstance(n, ast.Assert) else lines[n.lineno - 1]
            out.append(seg)
    return out
ok = True
for f in FILES:
    a, b = asserts(BASE, f), asserts(HEAD, f)
    ha, hb = (hashlib.sha256("\n\x00".join(x).encode()).hexdigest() for x in (a, b))
    same = a == b
    ok &= same
    print(f"{f}: asserts base={len(a)} head={len(b)} sha256 base={ha} head={hb} BYTE_IDENTICAL={'YES' if same else 'NO'}")
print("D2H_ASSERTIONS_BYTE_IDENTICAL=" + ("YES" if ok else "NO"))
