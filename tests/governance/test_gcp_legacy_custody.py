"""F1 — GCP build configuration is retained under custody, never active.

Cloud authority is AWS. GCP is LEGACY_HISTORICAL_NOT_CURRENT_TARGET. Six GCP
Cloud Build files remain in the tree.

Deleting them was deliberately not done: delivery configuration is the record of
how the estate was previously built, and destroying it destroys evidence. So the
governing distinction is not presence but USE —

    file existence      = permitted legacy custody
    active reference    = forbidden

These guards make that distinction testable. The register names every retained
artefact; the guards assert the custody claim is real and that no surface CI or a
hosting provider actually executes references any of them.

Evidence quotations do not count as use. A governance document that names
`cloudbuild.yaml` while explaining why it is retired is doing its job; only the
active deployment surfaces are scanned.

Authority: MVC-GOV-CANON-001 · register MVC-GCP-LEGACY-CUSTODY-001.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTER_PATH = (
    ROOT
    / "petcare_execution/GOVERNANCE/CANONICAL_REPOSITORY_AUTHORITY"
    / "GCP_LEGACY_CUSTODY_REGISTER.json"
)
REGISTER = json.loads(REGISTER_PATH.read_text(encoding="utf-8"))

# The whole of the executed-surface set. Anything CI or a hosting provider runs.
ACTIVE_SURFACES = REGISTER["active_deployment_surfaces"]

#: `gcloud` as a command, not as a substring of prose. Matches an invocation at a
#: line start, after a shell operator, or as a YAML/step entrypoint value.
_GCLOUD_INVOCATION = re.compile(r"(^|[\s;&|`$(])gcloud\s", re.MULTILINE)


def _active_files() -> list[Path]:
    files: list[Path] = []
    for surface in ACTIVE_SURFACES:
        p = ROOT / surface
        if p.is_dir():
            files.extend(f for f in p.rglob("*") if f.is_file())
        elif p.is_file():
            files.append(p)
    return files


def test_active_surface_set_is_not_empty():
    """Without this, every absence assertion below would pass vacuously."""
    files = _active_files()
    assert len(files) >= 4, f"active deployment surface set collapsed: {files}"


def test_every_registered_legacy_artefact_still_exists():
    """Custody is a claim about the tree. A register row naming a file that is
    gone is a custody claim that stopped being true without anyone noticing."""
    missing = [r["path"] for r in REGISTER["retained"] if not (ROOT / r["path"]).exists()]
    assert missing == [], f"registered legacy GCP artefacts absent from the tree: {missing}"


def test_register_covers_every_cloudbuild_file_in_the_tree():
    """The inverse guard. A new GCP build file that nobody registered is exactly
    the drift this register exists to prevent."""
    on_disk = {
        str(p.relative_to(ROOT))
        for p in ROOT.rglob("cloudbuild*.y*ml")
        if ".git/" not in str(p) and "node_modules" not in str(p)
    }
    registered = {r["path"] for r in REGISTER["retained"]}
    unregistered = sorted(on_disk - registered)
    assert unregistered == [], f"unregistered GCP build files: {unregistered}"


def test_no_active_deployment_surface_references_a_retained_gcp_artefact():
    """The load-bearing guard. Retention is permitted; wiring one back into a
    surface that CI or the host executes is not."""
    registered = [r["path"] for r in REGISTER["retained"]]
    basenames = {Path(p).name for p in registered}
    offenders = []
    for f in _active_files():
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for name in basenames:
            if name in text:
                offenders.append(f"{f.relative_to(ROOT)} -> {name}")
    assert offenders == [], f"active deployment surface references retired GCP config: {offenders}"


def test_no_active_deployment_surface_invokes_gcloud():
    """Cloud authority is AWS. A gcloud invocation on an executed surface makes
    GCP a current target again, whatever the registers say."""
    offenders = []
    for f in _active_files():
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if _GCLOUD_INVOCATION.search(text):
            offenders.append(str(f.relative_to(ROOT)))
    assert offenders == [], f"active deployment surface invokes gcloud: {offenders}"
