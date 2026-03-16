DOSE GUARDRAIL SPEC

Purpose:
Provide deterministic dose validation using animal-specific attributes.

Inputs:
- species
- breed
- weight
- age
- prescribed dose

Rules:
- dose must be evaluated against supported guardrail window
- out-of-range doses must emit reason codes
- edge-case handling must be explicit
- resulting decision must be audit compatible
