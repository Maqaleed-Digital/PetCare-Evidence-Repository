"""R19.4 (MVC-EPC-D-001, D2k): the per-run TOTP step-up seeding of the journey suite (finding D2G-JO7-SQ3-STEP-UP) is
unreachable under production configuration. Standing test.

Production configuration is `PETCARE_SECRET_MODE=aws_secrets_manager` (petcare_api/secret_provider.py: `environment` is
admissible only off production). The seeding writes a CONFIRMED TOTP factor directly, bypassing enrolment + confirmation.
This test proves, on every run:
  1. the seeding exists in exactly one place, the test-only tool `tools/e2e_stack.py` (positive control — the scan is not vacuous);
  2. no APPLICATION source (API, runtime, web app) contains it or references the tool or its per-run secret file;
  3. no application source constructs a CONFIRMED factor: a factor is confirmed only by a valid TOTP code (`use_step(confirm_at=…)`);
  4. the served app exposes no seeding route, and importing it creates no factor;
  5. the tool itself refuses to run, and refuses to seed, under production configuration — before it touches a database;
  6. neither deployable image copies the tool, the API tests or the web e2e suites.
If (2) or (3) ever fails, R19.4 classifies it as a CP1 defect to fix before any further journey work."""
import ast
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools" / "e2e_stack.py"
PRODUCTION_ENV = {"PETCARE_SECRET_MODE": "aws_secrets_manager"}
MARKERS = re.compile(r"e2e_stack|PETCARE_E2E_MFA_FILE|\.mfa\.json|MFA_FILE")

API_SOURCE = [p for p in (ROOT / "petcare_api").rglob("*.py") if "tests" not in p.relative_to(ROOT / "petcare_api").parts]
RUNTIME_SOURCE = list((ROOT / "petcare_runtime" / "src").rglob("*.py"))
WEB_SOURCE = [p for d in ("app", "components", "lib") for p in (ROOT / "petcare_web" / d).rglob("*")
              if p.suffix in {".ts", ".tsx", ".js", ".jsx", ".mjs"}] + [ROOT / "petcare_web" / "middleware.ts"]


def test_the_seeding_lives_only_in_the_test_tool():
    src = TOOL.read_text(encoding="utf-8")
    assert "put_factor(" in src and "confirmed_at=now" in src and "MFA_FILE" in src     # positive control: it is there
    names = {p.relative_to(ROOT).as_posix() for p in API_SOURCE + WEB_SOURCE}               # the scans below are not empty:
    assert {"petcare_api/main.py", "petcare_api/mfa.py", "petcare_api/postgres_repositories.py",
            "petcare_web/components/StepUp.tsx"} <= names                                    # they cover the MFA code paths


@pytest.mark.parametrize("group", ["api", "runtime", "web"])
def test_no_application_source_contains_or_references_the_seeding(group):
    files = {"api": API_SOURCE, "runtime": RUNTIME_SOURCE, "web": WEB_SOURCE}[group]
    hits = [str(p.relative_to(ROOT)) for p in files if p.is_file() and MARKERS.search(p.read_text(encoding="utf-8", errors="ignore"))]
    assert hits == [], f"R19.4 CP1 defect — test-only step-up seeding referenced from application source: {hits}"
    if group == "web":
        imports = [str(p.relative_to(ROOT)) for p in files if p.is_file()
                   and re.search(r"""from\s+['"][^'"]*e2e(-full)?/""", p.read_text(encoding="utf-8", errors="ignore"))]
        assert imports == [], imports


def _factor_calls(path):
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Call) and (getattr(node.func, "attr", None) == "Factor" or getattr(node.func, "id", None) == "Factor"):
            yield node


def test_no_application_source_constructs_a_confirmed_factor():
    """Only the repository's own row reader may rebuild a stored (possibly confirmed) factor; every other construction is a
    NEW, unconfirmed factor (enrolment), confirmed later only by a valid code."""
    offenders = []
    for p in API_SOURCE + RUNTIME_SOURCE:
        for call in _factor_calls(p):
            confirms = len(call.args) >= 5 or any(k.arg in ("confirmed_at", "last_used_step") for k in call.keywords)
            row_reader = p.name == "postgres_repositories.py" and any(k.arg == "confirmed_at" and "_from_db" in ast.unparse(k.value)
                                                                     for k in call.keywords)
            if confirms and not row_reader:
                offenders.append(f"{p.relative_to(ROOT)}:{call.lineno}")
    assert offenders == [], f"R19.4 CP1 defect — a confirmed TOTP factor is constructed in application source: {offenders}"


def test_the_served_app_has_no_seeding_route_and_creates_no_factor_on_import():
    sys.path[:0] = [str(ROOT / "petcare_api"), str(ROOT / "petcare_runtime" / "src")]
    import main as api
    paths = [getattr(r, "path", "") for r in api.app.routes]
    assert [p for p in paths if re.search(r"seed|e2e|fixture|mfa-file|test-only", p, re.I)] == []
    factors = getattr(api.MFA_REPO, "_factors", None)
    if factors is not None:
        assert not any(uid.startswith("u-e2e-") for uid in factors)


def test_the_tool_refuses_production_configuration_before_touching_a_database():
    env = {**os.environ, **PRODUCTION_ENV, "PETCARE_E2E_PG_URL": "postgresql://refused.invalid:1/never"}
    r = subprocess.run([sys.executable, str(TOOL)], cwd=ROOT, env=env, capture_output=True, text=True, timeout=120)
    assert r.returncode != 0 and "R19.4" in (r.stdout + r.stderr), (r.returncode, r.stdout[-400:], r.stderr[-400:])
    assert "refused.invalid" not in (r.stdout + r.stderr)          # it stopped before any connection attempt


def test_the_seed_step_itself_refuses_production_configuration(monkeypatch):
    sys.path.insert(0, str(TOOL.parent))
    import e2e_stack
    monkeypatch.setenv("PETCARE_SECRET_MODE", "aws_secrets_manager")
    with pytest.raises(SystemExit) as exc:
        e2e_stack._seed()
    assert "R19.4" in str(exc.value)


@pytest.mark.parametrize("dockerfile", ["petcare_api/Dockerfile", "petcare_web/Dockerfile"])
def test_no_deployable_image_copies_the_tool_or_the_test_suites(dockerfile):
    """The shipped image is the FINAL build stage; earlier (builder) stages are discarded."""
    lines = (ROOT / dockerfile).read_text(encoding="utf-8").splitlines()
    final = lines[max(i for i, l in enumerate(lines) if l.strip().upper().startswith("FROM")):]
    copies = [l for l in final if l.strip().upper().startswith(("COPY", "ADD"))]
    assert copies, dockerfile
    bad = [l for l in copies if re.search(r"\btools\b|petcare_api/tests|\be2e(-full)?\b|^\s*(COPY|ADD)\s+\.\s", l)]
    assert bad == [], (dockerfile, bad)
