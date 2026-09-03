# FR-ACQUIRE — Notification Templates

## File: `app/backend/services/notification_service.py`

## Template catalogue

### VACCINATION_REMINDER
| Locale | Text |
|--------|------|
| AR | `تذكير: موعد تطعيم {pet_name} خلال {days_left} أيام.` |
| EN | `{pet_name} vaccination due in {days_left} days.` |

### APPOINTMENT_CONFIRMED
| Locale | Text |
|--------|------|
| AR | `تم تأكيد موعدك مع د. {vet_name} في {datetime}.` |
| EN | `Appointment confirmed with Dr {vet_name} at {datetime}.` |

### MEDICATION_REFILL
| Locale | Text |
|--------|------|
| AR | `دواء {medication_name} لـ{pet_name} يحتاج تجديداً خلال {days_left} أيام.` |
| EN | `{pet_name} medication {medication_name} needs refill in {days_left} days.` |

### PRESCRIPTION_READY
| Locale | Text |
|--------|------|
| AR | `وصفة {pet_name} جاهزة من صيدلية {pharmacy_name}.` |
| EN | `{pet_name} prescription ready at {pharmacy_name}.` |

### RECALL_ALERT
| Locale | Text |
|--------|------|
| AR | `تنبيه: تم سحب دفعة الدواء {batch_number}. تحقق من مخزونك فوراً.` |
| EN | `RECALL: Medication batch {batch_number} recalled. Check stock now.` |

## Channels

| Channel | Provider | Credential env var | Stub mode |
|---------|---------|-------------------|-----------|
| sms | Unifonic | `UNIFONIC_API_KEY` | Yes (logs only) |
| whatsapp | Unifonic | `UNIFONIC_API_KEY` | Yes (logs only) |
| email | SMTP | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS` | Yes (logs only) |

## Scheduled job

`scheduler.py` → `_vaccination_reminder_job()` runs daily at 08:00 AST (05:00 UTC)
via APScheduler `CronTrigger`. Job is idempotent.
Vaccination date field is scaffolded — activate when `Pet.next_vaccination_date` column added.
