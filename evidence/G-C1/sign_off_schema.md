# G-C1 — Consultation Sign-off Schema

## New columns added to `consultations` table (models.py)

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `signed_at` | DateTime(timezone=True) | Yes | None | UTC timestamp set on first sign |
| `signed_by` | String | Yes | None | PilotUser.id of signing vet |
| `record_hash` | String(64) | Yes | None | SHA-256 of canonical payload |
| `is_immutable` | Boolean | No | False | Set True on sign — never reverts |

## Migration method
No Alembic present in codebase — columns added directly to `Consultation` SQLAlchemy model.
`Base.metadata.create_all(bind=engine)` called on startup via `auth_bootstrap.create_tables()`.

## Hash construction

SHA-256 of the following JSON (keys sorted, timezone normalised):
```json
{
  "diagnosis": "<text|null>",
  "id": <int>,
  "notes": "<text|null>",
  "pet_id": <int>,
  "signed_at": "<ISO datetime, timezone stripped>",
  "vet_id": "<string>"
}
```

Timezone stripping: `signed_at_iso.split('+')[0].rstrip('Z')`
Rationale: SQLite does not preserve timezone info on read-back; normalising ensures the hash is
reproducible across write (timezone-aware) and verify (naive) contexts.

## Immutability guard

In `PATCH /api/consultations/{id}`: if `is_immutable=True`, the route emits
`consultation.tamper_attempt` to the audit log and immediately raises `HTTP 409`
before any field mutation occurs.

## Sign-off flow

```
POST /api/consultations/{id}/sign
  → sign_consultation(db, id, vet_user_id)
  → compute canonical payload + SHA-256
  → set signed_at, signed_by, record_hash, is_immutable=True
  → db.commit()
  → emit_audit('consultation.signed', {...})
  → return signed consultation
```
