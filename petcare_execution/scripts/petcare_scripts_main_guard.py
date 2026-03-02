#!/usr/bin/env python3
"""
PetCare PH50
Script main-boundary guard (Python-only).

Goal:
- Prevent "import-time execution" regressions in critical scripts.
- Enforce that scripts are structured as:
  - imports / constants / defs
  - optional: module docstring
  - optional: if __name__ == "__main__": main()

This guard is intentionally strict and should be applied to a small allowlist
of critical scripts (verification tooling) to avoid false positives.

Exit codes:
- 0: PASS
- 2: FAIL (policy violation)
- 3: FAIL (parse error)
"""
from __future__ import annotations

import argparse
import ast
import pathlib
import sys
from typing import Iterable


ALLOWED_TOPLEVEL_NODES = (
    ast.Import,
    ast.ImportFrom,
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.ClassDef,
    ast.Assign,          # allow constants at module scope
    ast.AnnAssign,       # allow typed constants
    ast.Expr,            # allow module docstring ONLY
    ast.If,              # allow __main__ guard ONLY
)


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(2)


def is_module_docstring(expr: ast.Expr) -> bool:
    # module docstring is ast.Expr(value=ast.Constant(str))
    v = getattr(expr, "value", None)
    return isinstance(v, ast.Constant) and isinstance(v.value, str)


def is_main_guard(ifnode: ast.If) -> bool:
    # Accept:
    # if __name__ == "__main__":
    #     main()
    t = ifnode.test
    if not isinstance(t, ast.Compare):
        return False
    if not (isinstance(t.left, ast.Name) and t.left.id == "__name__"):
        return False
    if len(t.ops) != 1 or not isinstance(t.ops[0], ast.Eq):
        return False
    if len(t.comparators) != 1:
        return False
    c = t.comparators[0]
    if not (isinstance(c, ast.Constant) and c.value == "__main__"):
        return False
    return True


def contains_top_level_runtime_statements(mod: ast.Module) -> Iterable[str]:
    """
    Return human-readable policy violations.
    """
    violations: list[str] = []

    for i, node in enumerate(mod.body):
        if not isinstance(node, ALLOWED_TOPLEVEL_NODES):
            violations.append(f"disallowed top-level node: {type(node).__name__} at body[{i}]")
            continue

        # ast.Expr is only allowed if it's the module docstring
        if isinstance(node, ast.Expr) and not is_module_docstring(node):
            violations.append(f"non-docstring expression at top-level at body[{i}]")
            continue

        # ast.If is only allowed if it's __main__ guard
        if isinstance(node, ast.If) and not is_main_guard(node):
            violations.append(f"top-level if is not __main__ guard at body[{i}]")
            continue

        # For Assign / AnnAssign: block obvious runtime calls (best-effort)
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = node.value if isinstance(node, ast.AnnAssign) else node.value
            if isinstance(value, ast.Call):
                violations.append(f"top-level assignment executes a call at body[{i}] (import-time execution)")
                continue

    # Additionally require a main() function AND __main__ guard
    has_main_def = any(isinstance(n, ast.FunctionDef) and n.name == "main" for n in mod.body)
    has_main_guard = any(isinstance(n, ast.If) and is_main_guard(n) for n in mod.body)

    if not has_main_def:
        violations.append("missing def main() at top-level")
    if not has_main_guard:
        violations.append('missing if __name__ == "__main__": guard at top-level')

    return violations


def check_file(path: pathlib.Path) -> None:
    src = path.read_text(encoding="utf-8")
    try:
        mod = ast.parse(src, filename=str(path))
    except SyntaxError as e:
        print(f"ERROR: syntax error parsing {path}: {e}", file=sys.stderr)
        raise SystemExit(3)

    violations = list(contains_top_level_runtime_statements(mod))
    if violations:
        print(f"ERROR: main-boundary violations in {path}:", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        raise SystemExit(2)

    print(f"OK main-boundary PASS: {path}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", nargs="+", required=True, help="Python script paths to validate")
    args = ap.parse_args()

    for f in args.files:
        p = pathlib.Path(f)
        if not p.exists():
            fail(f"missing file: {f}")
        check_file(p)


if __name__ == "__main__":
    main()
