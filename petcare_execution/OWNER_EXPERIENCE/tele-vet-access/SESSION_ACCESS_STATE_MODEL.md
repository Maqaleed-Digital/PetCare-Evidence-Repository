SESSION ACCESS STATE MODEL

States:
- not_ready
- ready_to_join
- in_session
- completed
- access_denied

Requirements:
- state derivation must be deterministic
- invalid appointment or owner mismatch must deny access
- completed sessions remain visible in history only
