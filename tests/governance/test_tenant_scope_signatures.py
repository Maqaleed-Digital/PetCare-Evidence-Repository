"""Estate-level guard — a tenant parameter may not carry a permissive default.

Found in W0-I, generalised here. `ProfessionalAuthorityRegistry.held_at` took
`tenant_id: Optional[str] = None`, and the filter read `None` as *"match a grant
in any tenant"*. A caller who simply omitted the argument got a cross-tenant
authority check that looked correct at every call site.

The defect class is what makes it worth an estate guard rather than a one-line
fix: a permissive default is invisible at the call sites that pass the argument,
which is all of them until the one that does not. Behavioural tests cannot catch
it, because they exercise the call sites the tests themselves write. Only the
signature shows it.

So the property asserted here is structural: **a function that takes a tenant
must require it.** Where a default is genuinely correct, it is allowlisted by
name with a reason, so the exception is a recorded decision rather than an
oversight.

Authority: MVC-GOV-CANON-001 · W0-C (tenant scope is established server-side) ·
W0-I security review.
"""
import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

#: Live source. Excludes tests, which legitimately construct partial fixtures,
#: and petcare_execution, which is not compiled or executed.
LIVE_TREES = [
    "petcare_api",
    "petcare_runtime/src",
    "scripts",
]


def _is_tenant_param(name: str) -> bool:
    """Whether a parameter name refers to a tenant.

    Matched on the normalised name so `tenantId`, `TENANT_ID` and `tenant` are
    all caught. A guard that depends on one exact spelling stops working the
    first time someone writes it differently.
    """
    n = name.replace("_", "").lower()
    return n.startswith("tenant") or n.endswith("tenantid") or n == "tenant"


#: Allowlisted permissive defaults, as {location: reason}.
#: An entry here is a recorded decision, and the reason is what a reviewer checks.
ALLOWLIST: dict[str, str] = {
    "petcare_api/routers/auth.py:172:seed_user(tenant_id)":
        "Data constructor, not an authorization check. None means the seeded "
        "identity holds NO tenant assignment, and the consuming path fails "
        "closed on exactly that: require_tenant() raises 403 NO_TENANT_AUTHORITY "
        "when the session carries no tenant. Requiring a value here would force "
        "callers to invent one, which is the opposite of the intent. "
        "BOUND TO: " + "petcare_api/tests/test_tenant_authority.py"
        "::test_t_ten_02_identity_without_tenant_assignment_fails_closed",
}

#: Every allowlist rationale that claims a fail-closed consumer must name the
#: test that proves it, as `<path>::<test name>`. An exemption justified by
#: prose alone decays the moment the behaviour it describes changes; an
#: exemption bound to a test fails with it.
_BINDING_RE = re.compile(r"BOUND TO:\s*([^\s:]+\.py)::(\w+)")


def _python_files() -> list[Path]:
    files: list[Path] = []
    for tree in LIVE_TREES:
        base = ROOT / tree
        if not base.exists():
            continue
        files.extend(
            p for p in base.rglob("*.py")
            if "__pycache__" not in str(p) and "/tests/" not in str(p)
        )
    return files


def _offenders(files: list[Path]) -> list[str]:
    found = []
    for f in files:
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            args = node.args
            positional = args.posonlyargs + args.args
            # Defaults align to the TAIL of the positional list.
            pairs = list(zip(positional[len(positional) - len(args.defaults):], args.defaults))
            pairs += [
                (a, d) for a, d in zip(args.kwonlyargs, args.kw_defaults) if d is not None
            ]
            for arg, default in pairs:
                if not _is_tenant_param(arg.arg):
                    continue
                # `None` is the classic shape; a hard-coded scope is the same
                # defect wearing a value. `tenant_id: Optional[str] = "platform"`
                # on the audit probe let any unauthenticated caller file events
                # under the platform scope — caught by this branch, not the None
                # one, which is why both are checked.
                is_none = isinstance(default, ast.Constant) and default.value is None
                is_literal_scope = (
                    isinstance(default, ast.Constant)
                    and isinstance(default.value, str)
                    and default.value.strip() != ""
                )
                if is_none or is_literal_scope:
                    try:
                        rel = f.relative_to(ROOT)
                    except ValueError:
                        rel = f
                    loc = f"{rel}:{node.lineno}:{node.name}({arg.arg})"
                    if loc in ALLOWLIST:
                        continue
                    found.append(loc)
    return found


def test_live_source_is_scannable():
    """Without this, the absence assertion below would pass vacuously."""
    files = _python_files()
    assert len(files) > 50, f"live source scan collapsed to {len(files)} files"


def test_no_tenant_parameter_carries_a_permissive_default():
    """The guard. A tenant that may be omitted is a tenant that may be ignored."""
    offenders = _offenders(_python_files())
    assert offenders == [], (
        "tenant-bearing parameter defaults to None — a caller that omits it gets "
        f"an unscoped check: {offenders}"
    )


def test_allowlist_entries_carry_a_reason():
    """An allowlist without reasons is a list of unexplained exceptions."""
    unexplained = [k for k, v in ALLOWLIST.items() if not v or not v.strip()]
    assert unexplained == [], f"allowlisted permissive tenant defaults with no reason: {unexplained}"


def test_guard_detects_a_planted_permissive_default(tmp_path):
    """Meta-test — the guard must FAIL on a fixture carrying the defect.

    A static guard that has never fired is indistinguishable from one whose
    matcher is broken. This plants the exact shape it is meant to catch and
    asserts it is caught, so the guard's own detection is proven rather than
    assumed.
    """
    planted = tmp_path / "planted.py"
    planted.write_text(
        "from typing import Optional\n"
        "def resolve(actor_id: str, tenant_id: Optional[str] = None) -> bool:\n"
        "    return True\n",
        encoding="utf-8",
    )
    assert _offenders([planted]), "the guard failed to detect a planted permissive tenant default"

    fixed = tmp_path / "fixed.py"
    fixed.write_text(
        "def resolve(actor_id: str, tenant_id: str) -> bool:\n"
        "    return True\n",
        encoding="utf-8",
    )
    assert _offenders([fixed]) == [], "the guard fired on a correctly-required tenant"


def test_guard_is_not_spelling_dependent(tmp_path):
    """A guard that only knows one spelling stops working the first time someone
    writes `tenantId` or `TENANT_ID`."""
    for spelling in ("tenant_id", "tenantId", "TENANT_ID", "tenant"):
        f = tmp_path / f"s_{spelling}.py"
        f.write_text(f"def q(a: str, {spelling}=None):\n    return True\n", encoding="utf-8")
        assert _offenders([f]), f"guard missed the spelling {spelling!r}"


def test_guard_detects_a_hardcoded_tenant_scope(tmp_path):
    """Meta-test for the second shape — a default that is a real scope.

    `tenant_id: Optional[str] = "platform"` on the audit probe let any
    unauthenticated caller file events under the platform scope. It is the same
    defect as `= None`, wearing a value instead of an absence, and a guard that
    only looked for None missed it entirely — which is how it survived until the
    sweep.
    """
    planted = tmp_path / "scope.py"
    planted.write_text(
        'from typing import Optional\n'
        'def probe(event: str, tenant_id: Optional[str] = "platform") -> bool:\n'
        '    return True\n',
        encoding="utf-8",
    )
    assert _offenders([planted]), (
        "the guard failed to detect a tenant defaulting to a hard-coded scope"
    )


def test_allowlist_binding_tests_exist_and_are_named():
    """The allowlist entry for seed_user(tenant_id=None) rests on require_tenant()
    failing closed. That claim is bound to a real test by identifier here, so the
    exemption cannot outlive the behaviour it depends on.

    A4. The binding test exercises the actual authorization path — it drives a
    route with a session carrying no tenant and asserts 403 NO_TENANT_AUTHORITY —
    rather than inspecting source, because what is being justified is runtime
    behaviour, not a code shape.
    """
    bound = 0
    for location, reason in ALLOWLIST.items():
        m = _BINDING_RE.search(reason)
        assert m, f"allowlist entry {location} claims no binding test"
        rel, test_name = m.group(1), m.group(2)
        path = ROOT / rel
        assert path.exists(), f"{location} is bound to a missing file: {rel}"
        src = path.read_text(encoding="utf-8")
        assert f"def {test_name}(" in src, (
            f"{location} is bound to {rel}::{test_name}, which no longer exists"
        )
        bound += 1
    assert bound == len(ALLOWLIST)
