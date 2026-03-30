# Governance & Evidence Policy (UI-5)

## Deterministic Evidence
- EVIDENCE/MANIFEST.json must list all tracked files with sha256
- Export bundles must include:
  - MANIFEST.json
  - FILES.txt sorted by path
  - HASHES.txt sorted by path
  - EXPORT_LOG.txt redaction-safe
  - SCOPE.json tenant-scoped

## Acceptance
- Running ./scripts/petcare_land_pack.sh regenerates EVIDENCE/MANIFEST.json deterministically
- UI6 files must be present and referenced
