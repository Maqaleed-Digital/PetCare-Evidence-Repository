PROMOTION PATH RULES

Allowed promotion path:
- dev to test
- test to stage
- stage to prod

Rules:
- direct dev to prod promotion not allowed
- release candidate id required for promotion
- failed release gate blocks promotion
- promotion decision must be audit compatible
