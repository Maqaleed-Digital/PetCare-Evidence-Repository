LIVE PILOT OPERATING MODE

Purpose:
Define the deterministic governed operating posture for live pilot.

Supported statuses:
- ready
- live
- halted
- closed

Rules:
- live status must remain explicit
- halted status must block treated-as-live behavior
- pilot status changes must remain auditable
- live pilot remains distinct from general release
