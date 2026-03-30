# Test Checklist (UI-5)

Manual deterministic checks:

1) Compile
- python3 -m compileall FND/CODE_SCAFFOLD

2) Manifest regeneration
- ./scripts/petcare_land_pack.sh
- Verify EVIDENCE/MANIFEST.json exists

3) UI6 presence
- Verify UI6/ files in manifest

4) Export bundle
- Call /api/platform-admin/export/bundle
- Verify bundle files exist and are sorted
