"""A10 — the retired role FAMILY, detected in authorization contexts only.

`test_retired_role_absence.py` scans for one literal, `pharmacy_operator`, and it
is correct about that literal. PRE-2 found what a single-literal guard cannot
see: the web carried a **short form**, `pharmacy`, as an alias in `ROLE_ALIAS`, a
protected-route allowlist entry, and an `/account` allow-list member. The guard
passed throughout, because `"pharmacy_operator" not in "pharmacy"`.

Widening that guard's needle to `pharmacy` would be the wrong repair. Dispensing
is a real veterinary function with its own routes and T-DISP controls; the
pharmacy SURFACE is retained by Sponsor ruling
(`PHARMACY_DOMAIN_CAPABILITIES=RETAIN_PENDING_ROLE_REBINDING`). A guard that
banned the word would fail the build on legitimate clinical vocabulary, and would
be widened with exclusions until it meant nothing.

So this guard is **context-aware**: it looks for a pharmacy-family term used AS
AN AUTHORIZATION PRINCIPAL, and ignores the same word used as a domain term, a
page title, a route path, or a business capability.

Authority: Sponsor ruling `PHARMACY_ROLE=REMOVE` +
`PHARMACY_DOMAIN_CAPABILITIES=RETAIN_PENDING_ROLE_REBINDING`, recorded in
`MVC-PREPROD-SPONSOR-DECISION-PACK-001`.
"""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

#: Live trees. Matches the custody register's list, plus the web surfaces where
#: the short form actually survived.
LIVE_TREES = [
    "petcare_api",
    "petcare_runtime/src",
    "scripts",
    "petcare_web/app",
    "petcare_web/components",
    "petcare_web/lib",
]
EXTRA_FILES = ["petcare_web/middleware.ts"]

SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx"}

#: Terms naming the removed principal, in any spelling the estate could produce.
#: Deliberately a family and not a literal — the defect was a spelling nobody had
#: written down.
_PHARMACY_FAMILY = re.compile(
    r"\b(pharmacy|pharmacist|pharma)[a-z_]*\b", re.IGNORECASE
)

#: Markers that a line is deciding or declaring AUTHORITY rather than naming a
#: domain concept. This is the whole of the guard's context-awareness.
_AUTHORITY_CONTEXT = re.compile(
    r"(ALLOWED_ROLES|VALID_ROLES|ROLE_MAP|ROLE_ALIAS|ROUTE_CATEGORY_BY_ROLE"
    r"|allowed_?[Rr]oles|protectedRoutes|require_role|require_admin"
    r"|actor_role|\brole\s*(==|!=|=|:)|\bROLE_[A-Z_]+\s*="
    r"|roles\s*[:=]|\brole\s+in\b|\brole\s+not\s+in\b"
    r"|['\"]role['\"]\s*\]?\s*(=|:))"
)

#: A declaration that OPENS a multi-line authority structure. Line-by-line
#: context is not enough on its own: the entry that actually shipped the defect
#: was `'/account': ['owner', 'vet', 'pharmacy', 'admin'],` — a line that names
#: no role keyword at all, three lines inside `protectedRoutes`. A guard that
#: could not see the enclosing block would miss the exact thing it exists for.
_AUTHORITY_BLOCK_OPEN = re.compile(
    r"(ROLE_ALIAS|ROUTE_CATEGORY_BY_ROLE|protectedRoutes|ALLOWED_ROLES"
    r"|VALID_ROLES|ROLE_MAP|allowed_?[Rr]oles)\b[^\n]*[\{\[\(]\s*$"
)
_BLOCK_CLOSE = re.compile(r"^\s*[\}\]\)]")

#: A route PATH is not a principal. `/pharmacy` is a retained surface.
_ROUTE_PATH = re.compile(r"['\"`]/[\w/:*-]*pharmacy[\w/:*-]*['\"`]")

#: This file must name the terms in order to forbid them.
_GUARD_FILES = {"tests/governance/test_retired_role_family.py"}

#: Occurrences OUTSIDE the serving authorization surface, each registered with a
#: reason and a disposition. Registered rather than excluded: an exclusion by
#: tree would hide the next one, and these are exactly the kind of thing that
#: should be re-read when the pending binding is decided.
#:
#: Sponsor ruling `PHARMACY_ROLE=REMOVE` governs the authorization PRINCIPAL —
#: the backend role guards, the storage catalogue and the web middleware. All
#: three are clean. `PHARMACY_DOMAIN_CAPABILITIES=RETAIN_PENDING_ROLE_REBINDING`
#: explicitly forbids deleting domain capability, and `petcare_runtime` is a
#: separate package whose role vocabulary the serving layer never authorizes
#: against.
REGISTERED_PENDING: dict[str, str] = {
    "petcare_runtime/src/petcare/auth/access_control.py:9":
        "A DEAD constant. Declared and referenced by nothing — no authorize_* "
        "function compares against it and the pharmacy package does not import "
        "it. It is the value `role_probes` DERIVES the refused role from, so "
        "removing it would take away the only non-naming way tests can reach "
        "one. Disposition: remove when the domain package is next opened; it "
        "authorizes nothing today. DOMAIN_CAPABILITY_PENDING_ROLE_BINDING.",
    "petcare_runtime/src/petcare/ai_hitl/service.py:25":
        "A human-in-the-loop REVIEWER routing map in the AI runtime. The key "
        "`pharmacy` is a review CONTEXT, not a principal; the value "
        "`pharmacist` names an eligible reviewer class that has no "
        "authorization principal behind it. It decides who is asked to review, "
        "not who may act. Disposition: rebind to a governed reviewer role when "
        "PRE-2D is decided. DOMAIN_CAPABILITY_PENDING_ROLE_BINDING.",
}


def _files() -> list[Path]:
    out: list[Path] = []
    for tree in LIVE_TREES:
        base = ROOT / tree
        if not base.exists():
            continue
        for p in base.rglob("*"):
            s = str(p)
            if not p.is_file() or p.suffix not in SUFFIXES:
                continue
            if "node_modules" in s or "__pycache__" in s or "/.next/" in s:
                continue
            out.append(p)
    for extra in EXTRA_FILES:
        p = ROOT / extra
        if p.exists():
            out.append(p)
    return out


def _code_lines(path: Path) -> list[str]:
    """Lines with comments removed. Prose may discuss a retired principal; code
    may not declare one."""
    out = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("*"):
            continue
        out.append(re.sub(r"//.*$", "", re.sub(r"#.*$", "", line)))
    return out


def authority_offenders() -> list[str]:
    offenders = []
    for path in _files():
        rel = str(path.relative_to(ROOT))
        if rel in _GUARD_FILES:
            continue
        # Test code is excluded: a control that asserts a term's ABSENCE has to
        # name it, and test files are not a serving authorization path. The
        # storage catalogue refuses the value regardless (test_pharm_role_01).
        if "/tests/" in rel.replace("\\", "/") or "__tests__" in rel:
            continue
        in_authority_block = False
        for n, line in enumerate(_code_lines(path), 1):
            if _AUTHORITY_BLOCK_OPEN.search(line):
                in_authority_block = True
            elif in_authority_block and _BLOCK_CLOSE.match(line):
                in_authority_block = False
            if not _PHARMACY_FAMILY.search(line):
                continue
            if not (in_authority_block or _AUTHORITY_CONTEXT.search(line)):
                continue          # domain language, not authority
            without_paths = _ROUTE_PATH.sub("", line)
            if not _PHARMACY_FAMILY.search(without_paths):
                continue          # only a retained route path remained
            location = f"{rel}:{n}"
            if location in REGISTERED_PENDING:
                continue
            offenders.append(f"{location} -> {line.strip()[:90]}")
    return offenders


def test_the_scan_is_not_vacuous():
    files = _files()
    assert len(files) > 40, f"live source scan collapsed to {len(files)} files"


def test_no_pharmacy_family_term_is_used_as_an_authorization_principal():
    """The guard. PHARMACY_ROLE=REMOVE."""
    offenders = authority_offenders()
    assert offenders == [], (
        "a pharmacy-family term is used as an authorization principal: "
        f"{offenders}"
    )


def test_every_registered_pending_occurrence_still_exists_and_still_matches():
    """A register entry that protects nothing is worse than no entry: it reads
    as a considered exception while the thing it described has moved.

    Each entry must still be a real occurrence that the guard WOULD have flagged
    — so an entry cannot quietly become a blanket exemption for a file.
    """
    stale = []
    for location, reason in REGISTERED_PENDING.items():
        rel, _, lineno = location.rpartition(":")
        path = ROOT / rel
        if not path.exists():
            stale.append(f"{location} (file gone)")
            continue
        lines = _code_lines(path)
        idx = int(lineno) - 1
        if idx >= len(lines) or not _PHARMACY_FAMILY.search(lines[idx]):
            stale.append(f"{location} (no pharmacy-family term on that line)")
            continue
        assert reason.strip(), f"{location} has no recorded reason"
    assert stale == [], f"registered pending entries that no longer hold: {stale}"


def test_the_serving_authorization_surface_is_completely_clean():
    """Stated separately from the tree-wide guard, because this is the set the
    Sponsor ruling actually governs."""
    serving = [o for o in authority_offenders()
               if o.startswith(("petcare_api", "petcare_web", "scripts"))]
    assert serving == [], f"the serving authorization surface is not clean: {serving}"


def test_the_retained_domain_surface_is_still_present():
    """PHARMACY_DOMAIN_CAPABILITIES=RETAIN_PENDING_ROLE_REBINDING.

    Paired with the guard deliberately. A guard that only forbade would be
    satisfied by deleting the product, and the ruling explicitly does not
    authorise that — "do not delete legitimate clinical/dispensing product
    capability merely because the retired role is removed".
    """
    assert (ROOT / "petcare_web/app/pharmacy/page.tsx").exists(), (
        "the pharmacy surface was deleted; the ruling retains it"
    )
    middleware = (ROOT / "petcare_web/middleware.ts").read_text(encoding="utf-8")
    assert "'/pharmacy'" in middleware, "the pharmacy route is no longer protected"


# ---------------------------------------------------------------------------
# Meta-tests — each required case, planted
# ---------------------------------------------------------------------------

def _scan_text(tmp_path, text: str, name: str = "planted.ts") -> bool:
    """Run the real matcher over planted text, block tracking included."""
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    in_block = False
    for line in _code_lines(p):
        if _AUTHORITY_BLOCK_OPEN.search(line):
            in_block = True
        elif in_block and _BLOCK_CLOSE.match(line):
            in_block = False
        if not _PHARMACY_FAMILY.search(line):
            continue
        if not (in_block or _AUTHORITY_CONTEXT.search(line)):
            continue
        if not _PHARMACY_FAMILY.search(_ROUTE_PATH.sub("", line)):
            continue
        return True
    return False


def test_meta_pharmacy_in_an_authorization_allowlist_is_detected(tmp_path):
    """The exact shape that shipped: a member of an allow-list, three lines
    inside `protectedRoutes`, naming no role keyword of its own."""
    assert _scan_text(tmp_path,
                      "const protectedRoutes: Record<string, string[]> = {\n"
                      "  '/owner': ['owner', 'admin'],\n"
                      "  '/account': ['owner', 'vet', 'pharmacy', 'admin'],\n"
                      "}\n")


def test_meta_pharmacy_as_a_role_alias_is_detected(tmp_path):
    assert _scan_text(tmp_path, "const ROLE_ALIAS = { pharmacy: 'pharmacy' }\n")


def test_meta_a_python_role_comparison_is_detected(tmp_path):
    assert _scan_text(tmp_path, 'if role == "pharmacy":\n', name="planted.py")


def test_meta_the_retired_long_form_as_a_role_is_detected(tmp_path):
    assert _scan_text(tmp_path,
                      'VALID_ROLES = {"owner", "pharmacy_operator"}\n',
                      name="planted.py")


def test_meta_a_session_role_of_pharmacy_is_detected(tmp_path):
    assert _scan_text(tmp_path, 'session["role"] = "pharmacy"\n', name="planted.py")


def test_meta_a_legitimate_pharmacy_ui_label_is_NOT_flagged(tmp_path):
    assert not _scan_text(
        tmp_path, "  <h1>{t(s.pharmacyDashboard)}</h1>\n", name="planted.tsx")


def test_meta_a_legitimate_domain_term_is_NOT_flagged(tmp_path):
    assert not _scan_text(
        tmp_path,
        "def record_pharmacy_dispense(prescription_id: str) -> None:\n",
        name="planted.py")


def test_meta_a_retained_route_path_is_NOT_flagged(tmp_path):
    """`'/pharmacy': ['vet', 'admin']` is the rebound surface: a pharmacy PATH
    guarded by roles that are not pharmacy. It must pass, or the guard would
    force the product to be deleted."""
    assert not _scan_text(tmp_path, "  '/pharmacy': ['vet', 'admin'],\n")


def test_meta_the_matcher_listing_the_route_is_NOT_flagged(tmp_path):
    assert not _scan_text(
        tmp_path, "  matcher: ['/vet/:path*', '/pharmacy/:path*'],\n")
