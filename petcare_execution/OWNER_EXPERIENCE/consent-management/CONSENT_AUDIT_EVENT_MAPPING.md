CONSENT AUDIT EVENT MAPPING

Baseline events:
- consent.updated
- pet.viewed
- appointment.created

Rules:
- consent grant and revoke actions must emit consent.updated
- owner-facing reads may emit governed view events
- audit event naming must remain compatible with existing taxonomy
