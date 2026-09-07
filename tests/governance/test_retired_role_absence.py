"""F2/F3 — tree-wide absence of the retired `pharmacy_operator` role.

W0-F acceptance criterion 3 says the retired role must appear nowhere in the
tree. The guard that previously enforced it scanned three directories of one
application (`petcare_web/{app,components,lib}`), so the claim was far wider than
its enforcement.

Taken literally, AC3 is also unachievable and undesirable: a guard that forbids
the role must name it, and the governance decision that retires it must quote it.
The enforceable form is two-sided, and both sides are asserted here:

    live source        ZERO occurrences, no exceptions
    everywhere else    every occurrence explicitly REGISTERED, with a reason

Exclusions are path-specific and justified in the register. There is no wildcard
that could hide a live source tree.

Authority: MVC-GOV-CANON-001 · register MVC-RETIRED-ROLE-CUSTODY-001 · W0-D.
"""
import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTER_PATH = (
    ROOT
    / "petcare_execution/GOVERNANCE/CANONICAL_REPOSITORY_AUTHORITY"
    / "RETIRED_ROLE_CUSTODY_REGISTER.json"
)
REGISTER = json.loads(REGISTER_PATH.read_text(encoding="utf-8"))

NEEDLE = REGISTER["retired_role"]
LIVE_TREES = REGISTER["live_source_trees"]
EXCLUDED = [e["path"] for e in REGISTER["excluded_paths"]]
REGISTERED = {a["path"] for a in REGISTER["registered_stale_artefacts"]}

SOURCE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".sql", ".json", ".md", ".yaml", ".yml"}

#: The guards themselves must name the needle to forbid it.
GUARD_FILES = {
    "tests/governance/test_retired_role_absence.py",
    "tests/governance/test_canonical_register_integrity.py",
    "petcare_web/__tests__/absence-guards.test.ts",
    "petcare_api/tests/test_dispensing_fail_closed.py",
    # Asserts a session claiming the retired role is refused; it must name it.
    "petcare_api/tests/test_session_bound_authorization.py",
}


def _excluded(rel: str) -> bool:
    return any(rel == e or rel.startswith(e + "/") for e in EXCLUDED)


def _scan(base: Path) -> list[str]:
    """Every source-like file under `base`, minus excluded paths."""
    out = []
    for p in base.rglob("*"):
        if not p.is_file() or p.suffix not in SOURCE_SUFFIXES:
            continue
        rel = str(p.relative_to(ROOT))
        if _excluded(rel):
            continue
        out.append(rel)
    return out


#: Case-insensitive needle. The role string is `pharmacy_operator`, but a live
#: grant could be reintroduced as `Pharmacy_Operator` or `PHARMACY_OPERATOR`, and a
#: case-sensitive scan would report the tree clean. A guard that can miss a
#: differently-cased live authorization string is not a guard.
#:
#: The underscore stays REQUIRED. Making the separator optional as well was tried
#: and matched the ordinary English phrase "pharmacy operator" throughout the
#: governance prose — 18 false positives, which would have trained the next
#: reader to widen the exclusion list until the guard meant nothing. A wire role
#: keeps its underscore; only its case can drift.
_NEEDLE_RE = re.compile(re.escape(NEEDLE), re.IGNORECASE)

#: Display-only constants that match the needle case-insensitively but confer no
#: authorization. Each is registered with the reason it cannot grant anything.
#: `ROLE_PHARMACY_OPERATOR = "Pharmacy Operator"` is a legacy DISPLAY name, and
#: `test_dispensing_fail_closed.py` asserts it is absent from `VALID_ROLES` — so
#: the constant exists precisely so a test can prove the role is rejected.
DISPLAY_ONLY_CONSTANTS = {
    "petcare_runtime/src/petcare/auth/access_control.py":
        'ROLE_PHARMACY_OPERATOR = "Pharmacy Operator" — legacy display label, not a '
        "wire role. It is excluded from VALID_ROLES, and "
        "petcare_api/tests/test_dispensing_fail_closed.py::"
        "test_t_disp_05_retired_pharmacy_operator_cannot_authenticate asserts that "
        "exclusion, so the symbol exists in order to be proven powerless.",
    "petcare_api/main.py":
        "Imports ROLE_PHARMACY_OPERATOR solely so VALID_ROLES can be asserted not "
        "to contain it. The import is the subject of the guard, not a grant.",
}


#: The exact display-only symbol permitted inside the files registered above.
#: Only THIS token is subtracted; everything else in those files is still
#: scanned.
_DISPLAY_ONLY_TOKEN = re.compile(r"ROLE_PHARMACY_OPERATOR", re.IGNORECASE)


def _strip_prose(rel: str, text: str) -> str:
    """Remove comments and docstrings, keeping every other string literal.

    A retired role named in a comment or docstring cannot grant anything — W0-D's
    own explanation in `main.py` says "PHARMACY_OPERATOR is deliberately ABSENT",
    and a guard that flagged that would be flagging the record of the retirement.
    A role named in a STRING LITERAL in code is exactly what a grant looks like,
    so literals are kept and still scanned.

    This is why the file-wide exemption was wrong: it removed both. Stripping
    prose removes only the half that cannot confer authority.
    """
    if rel.endswith(".py"):
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return text
        # Docstrings are string expressions in a body position.
        doc_spans = []
        for node in ast.walk(tree):
            if not isinstance(
                node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
            ):
                continue
            body = getattr(node, "body", [])
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                doc_spans.append((body[0].lineno, body[0].end_lineno))
        lines = text.splitlines()
        for start, end in doc_spans:
            for i in range(start - 1, min(end, len(lines))):
                lines[i] = ""
        # `#` comments. A `#` inside a string literal is rare in this estate and
        # erring toward stripping only risks a false NEGATIVE on a commented
        # grant, which the code-literal scan above would still catch.
        lines = [re.sub(r"#.*$", "", ln) for ln in lines]
        return "\n".join(lines)

    if rel.endswith((".ts", ".tsx", ".js", ".jsx")):
        text = re.sub(r"/\*[\s\S]*?\*/", "", text)
        text = re.sub(r"//.*$", "", text, flags=re.M)
    return text


def _hits(files: list[str]) -> list[str]:
    """Files matching the needle, case-insensitively.

    Display-only constants are subtracted TOKEN-WISE, never file-wise. Excluding
    a whole file was tried and is wrong: it blinds the guard everywhere inside
    that file, so a planted `PHARMACY_OPERATOR` grant in `main.py` went
    undetected. The registered symbol is removed from the text and the remainder
    is still scanned, so the exemption covers exactly the constant it names and
    nothing else in the same file.
    """
    hits = []
    for rel in files:
        try:
            text = (ROOT / rel).read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        text = _strip_prose(rel, text)
        if rel in DISPLAY_ONLY_CONSTANTS:
            text = _DISPLAY_ONLY_TOKEN.sub("", text)
        if _NEEDLE_RE.search(text):
            hits.append(rel)
    return hits


def test_live_source_trees_are_scannable_and_not_empty():
    """Without this, every absence assertion below could pass vacuously."""
    for tree in LIVE_TREES:
        assert (ROOT / tree).exists(), f"declared live source tree missing: {tree}"
    total = sum(len(_scan(ROOT / t)) for t in LIVE_TREES)
    assert total > 100, f"live source scan collapsed to {total} files"


def test_retired_role_absent_from_every_live_source_tree():
    """The load-bearing guard, and the one AC3 actually means. Zero tolerance:
    no register entry exempts a live source file."""
    offenders = []
    for tree in LIVE_TREES:
        for rel in _hits(_scan(ROOT / tree)):
            if rel not in GUARD_FILES:
                offenders.append(rel)
    assert offenders == [], f"retired role present in live source: {offenders}"


def test_every_remaining_occurrence_is_registered():
    """Outside live source, retention is permitted but never silent. An
    unregistered occurrence is drift; a registered one is a recorded decision."""
    unregistered = [
        rel
        for rel in _hits(_scan(ROOT / "petcare_execution"))
        if rel not in REGISTERED and rel not in GUARD_FILES
    ]
    assert unregistered == [], f"unregistered retired-role occurrences: {unregistered}"


def test_registered_artefacts_still_exist():
    """The inverse guard: a register row for a file that is gone is a custody
    claim that quietly stopped being true."""
    missing = [p for p in sorted(REGISTERED) if not (ROOT / p).exists()]
    assert missing == [], f"registered artefacts absent from the tree: {missing}"


def test_artefacts_claiming_an_in_file_marker_actually_carry_one():
    """F3. The four artefacts that model the role as AUTHORIZATION must say so in
    the file itself, so the contradiction cannot be read as current intent."""
    missing = []
    for a in REGISTER["registered_stale_artefacts"]:
        if not a["in_file_marker"]:
            continue
        text = (ROOT / a["path"]).read_text(encoding="utf-8")
        if "STATUS=STALE_DESIGN_ARTEFACT" not in text or "DO_NOT_IMPLEMENT_FROM_THIS_FILE" not in text:
            missing.append(a["path"])
    assert missing == [], f"artefacts claiming an in-file stale marker without one: {missing}"
