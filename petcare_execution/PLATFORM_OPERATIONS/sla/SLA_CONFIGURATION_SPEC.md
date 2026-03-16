SLA CONFIGURATION SPEC

Purpose:
Define deterministic service-level agreement configuration and evaluation.

Supported thresholds:
- response
- fulfillment
- availability

Rules:
- SLA configuration must define measurable thresholds
- breach evaluation must emit explicit reason code
- breach events may not be silently suppressed
- SLA state must be readable for reporting
