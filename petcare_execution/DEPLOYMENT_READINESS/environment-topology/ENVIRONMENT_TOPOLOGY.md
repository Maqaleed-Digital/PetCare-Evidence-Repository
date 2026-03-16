ENVIRONMENT TOPOLOGY

Environments:
- dev
- test
- stage
- prod

Rules:
- promotion path must be deterministic
- prod is reachable only through governed promotion path
- environment roles and purposes must remain distinct
- deployment evidence must reference target environment
