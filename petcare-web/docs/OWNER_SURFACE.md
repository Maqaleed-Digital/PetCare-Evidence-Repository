# Owner Surface — petcare-web (PH-UI-2)

## Scope

PH-UI-2 delivers the read-only Owner portal MVP. No backend mutations. All data
is placeholder / mock — real data binding is out of scope for this phase.

## Components

| Component             | File                                        | Purpose                                      |
|-----------------------|---------------------------------------------|----------------------------------------------|
| `PetProfileCard`      | `components/owner/PetProfileCard.tsx`       | Pet identity, weight, microchip, owner, consent |
| `AppointmentCard`     | `components/owner/AppointmentCard.tsx`      | Single appointment with status badge         |
| `HealthTimeline`      | `components/owner/HealthTimeline.tsx`       | Chronological health event list              |
| `VaccinationCard`     | `components/owner/VaccinationCard.tsx`      | Single vaccination record with due-date status |
| `VaccinationSummary`  | `components/owner/VaccinationSummary.tsx`   | Grouped vaccination list (overdue / due soon / current) |
| `QuickActions`        | `components/owner/QuickActions.tsx`         | Action panel — disabled in read-only shell    |

## Quick Actions Surface

Four actions are visible in the Owner portal. All are disabled (`disabled` attr,
`cursor-default`) in PH-UI-2 — they are placeholders for future interactivity:

| Action              | Variant   | Description                                        |
|---------------------|-----------|----------------------------------------------------|
| Book Appointment    | primary   | Schedule a new visit with the vet                  |
| View Records        | secondary | Access full medical history and documents          |
| Emergency Access    | danger    | Share critical health data with an emergency vet   |
| Consent Settings    | neutral   | Manage data sharing and consent preferences        |

## Types

Defined in `types/owner.ts`:

- `Pet` — species, breed, DOB, weight, microchip
- `Owner` — name, email, phone, consent flag, emergency contact
- `Appointment` — vet, clinic, datetime, reason, status, notes
- `HealthTimelineEvent` — type, title, description, vet, date
- `Vaccination` — name, dates, status (`current` / `due_soon` / `overdue`), batch, vet
- `OwnerDashboard` — composite view of all owner data

## Vaccination Status Rules

| Status      | Meaning                              |
|-------------|--------------------------------------|
| `current`   | Next due date is in the future       |
| `due_soon`  | Next due date is within 30 days      |
| `overdue`   | Next due date has passed             |

## Constraints

- No backend calls from this surface — data is passed as props / mock constants.
- No mutations — all `QuickActions` buttons are `disabled`.
- PDPL: no PII is transmitted; all data shown is mock placeholder only.
