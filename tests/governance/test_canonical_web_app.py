"""X-24 (MVC-EPC-D-001 Lane D, D2; Sponsor ruling ONE_CANONICAL_CI_TESTED_WEB_APP).

The product web app is `petcare_web`: it is the only web app the CI `verify` job builds and tests, and the one the D0
full-stack journey harness serves. `petcare-web` is an earlier create-next-app prototype (PH-UI dashboards) that no
workflow references. Lane D builds product UI ONLY in `petcare_web`; `petcare-web` is frozen by content digest so
product UI cannot land there by mistake. Retirement of `petcare-web` is recommended, and needs a separate authorisation.
"""
import hashlib
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANONICAL, PROTOTYPE = "petcare_web", "petcare-web"
#: sha256 of the concatenated tracked files of petcare-web (sorted paths) at MVC-EPC-D-001 D2 (base e1a6e2d).
PROTOTYPE_DIGEST = "42d89e2ed1b59ac23030488be92e525cd5f0d5cc37ba1f8ad20300910aa4424d"


def _tracked(prefix: str) -> list:
    out = subprocess.run(["git", "ls-files", "-z", prefix], cwd=ROOT, capture_output=True, check=True).stdout
    return sorted(p for p in out.decode().split("\0") if p)


def test_ci_builds_and_tests_only_the_canonical_web_app():
    wf = (ROOT / ".github" / "workflows" / "verify.yml").read_text(encoding="utf-8")
    dirs = set(re.findall(r"working-directory:\s*(\S+)", wf))
    assert dirs == {CANONICAL}, dirs
    assert PROTOTYPE not in wf
    for other in (ROOT / ".github" / "workflows").glob("*.yml"):
        assert PROTOTYPE not in other.read_text(encoding="utf-8"), other.name


def test_the_full_stack_harness_serves_the_canonical_web_app_and_the_real_api():
    cfg = ROOT / CANONICAL / "playwright.full.config.ts"
    text = cfg.read_text(encoding="utf-8")
    assert "python3 ../tools/e2e_stack.py" in text and "npx next dev" in text   # next dev runs in petcare_web (config dir)
    assert "import main as api" in (ROOT / "tools" / "e2e_stack.py").read_text(encoding="utf-8")
    assert not (ROOT / PROTOTYPE / "playwright.full.config.ts").exists()


def test_the_prototype_web_app_is_frozen():
    files = _tracked(PROTOTYPE)
    assert files, "petcare-web must stay in place (not deleted by Lane D)"
    digest = hashlib.sha256(b"".join((ROOT / p).read_bytes() for p in files)).hexdigest()
    assert digest == PROTOTYPE_DIGEST, "petcare-web changed: product UI belongs in petcare_web (X-24)"
