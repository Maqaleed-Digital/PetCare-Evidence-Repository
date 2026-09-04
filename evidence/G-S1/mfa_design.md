# G-S1 — MFA Design

## File: `app/backend/services/mfa_service.py`

## OTP specification

| Property | Value |
|----------|-------|
| Format | 6-char uppercase hex (e.g. `A3F7C2`) |
| TTL | 5 minutes |
| Storage | In-process dict (pilot phase) → Redis in production |
| Algorithm | `secrets.token_hex(3).upper()` |
| Hash stored | SHA-256 of plaintext OTP — plaintext never persisted |
| Use | One-time: consumed on verification |

## Routes requiring MFA (X-MFA-Token header)

| Route | Rationale |
|-------|-----------|
| `POST /api/consultations/{id}/sign` | Clinical record immutability |
| `POST /api/prescriptions` | Drug dispensing authority |
| `GET /api/admin/audit-export` | Sensitive audit data |
| `DELETE /api/users/{id}` | Irreversible destructive action |

## Audit events

| Event | Trigger |
|-------|---------|
| `mfa.otp_generated` | `generate_otp()` called |
| `mfa.verified` | OTP matches, within TTL |
| `mfa.failed` | reason: `no_record` \| `expired` \| `invalid` |

## Production migration note

Replace `OTP_STORE: dict` with Redis `SETEX(user_id, 300, hash)`.
No code changes required beyond swapping the storage backend.
