"""FR-04 AC-FR-04-02 (U17) — static control: the restricted-substance gate is a constant that no environment
variable, feature flag, setting or rebinding can reach. Not a served-app test (no served_app marker); the served
behaviour is proven in test_fr04_restricted_substances.py."""
import inspect
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import inventory  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def test_the_gate_is_a_constant_no_setting_can_reach():
    src = inspect.getsource(inventory.restricted_substance_workflow_enabled)
    body = src.split('"""')[-1]
    assert body.strip() == "return False"
    assert not re.search(r"environ|getenv|flag|setting|config", body)
    code = [p for p in (ROOT / "petcare_api").rglob("*.py") if "tests" not in p.parts]
    rebinds = [str(p) for p in code if re.search(r"restricted_substance_workflow_enabled\s*=[^=]", p.read_text("utf-8"))]
    assert rebinds == []
    assert re.search(r"restricted_substance_workflow_enabled\s*=[^=]", "restricted_substance_workflow_enabled = x")
    flags = (ROOT / "petcare_web" / "lib" / "featureFlags.ts").read_text("utf-8")
    assert not re.search(r"(?i)restricted|controlled|ev-?11", flags)
