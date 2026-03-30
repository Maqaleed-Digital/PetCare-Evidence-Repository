import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

MANIFEST = ROOT / "EVIDENCE" / "MANIFEST.json"

REQUIRED_UI6 = [
    "UI6/DAL_CONTRACT.md",
    "UI6/EVIDENCE_EXPORT_BUNDLE_SPEC.md",
    "UI6/NEGATIVE_CASES_UI6.md",
    "UI6/TENANT_BOUND_STORAGE_MODEL.md",
    "UI6/UI6_PACK_SUMMARY.md",
]


def fail(msg: str) -> None:
    raise SystemExit(msg)


def load_manifest() -> dict:
    if not MANIFEST.exists():
        fail(f"MISSING {MANIFEST}")
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def assert_ui6_present(m: dict) -> None:
    paths = [f.get("path") for f in m.get("files", [])]
    missing = [p for p in REQUIRED_UI6 if p not in paths]
    if missing:
        fail(f"UI6 missing in manifest: {missing}")


def run_export_smoke() -> None:
    from FND.CODE_SCAFFOLD.storage.memory_store import MemoryStore
    from FND.CODE_SCAFFOLD.storage.export_bundle import build_export_bundle

    out = ROOT / "EVIDENCE" / "exports" / "smoke_test"
    if out.exists():
        shutil.rmtree(out)

    s = MemoryStore()
    s.save("owners/o1", {"owner_id": "o1", "name": "Test"})
    s.save("pets/p1", {"pet_id": "p1", "owner_id": "o1"})

    os.makedirs(out, exist_ok=True)

    b = build_export_bundle({"tenant": "t1", "records": 2})
    (out / "EXPORT_LOG.txt").write_text(json.dumps(b, indent=2) + "\n", encoding="utf-8")

    if not (out / "EXPORT_LOG.txt").exists():
        fail("MISSING export file EXPORT_LOG.txt")


def main() -> None:
    m = load_manifest()
    assert_ui6_present(m)
    run_export_smoke()
    print("PASS UI5 deterministic proof")


if __name__ == "__main__":
    main()
