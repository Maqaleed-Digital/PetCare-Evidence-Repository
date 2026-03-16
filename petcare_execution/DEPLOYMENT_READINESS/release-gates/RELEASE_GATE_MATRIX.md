RELEASE GATE MATRIX

Required gate classes:
- security
- clinical
- ai_governance
- ops_readiness

Rules:
- all required gates must pass before prod promotion
- failed gate classes must be explicitly listed
- evidence bundle reference required
- release decision must remain reproducible
