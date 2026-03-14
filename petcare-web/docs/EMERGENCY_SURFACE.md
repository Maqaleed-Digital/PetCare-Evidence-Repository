# Emergency Surface — petcare-web (PH-UI-6)

## Scope

PH-UI-6 delivers the read-only Emergency Coordination surface. All data is
placeholder/mock. No mutations. No real backend calls.

## Route

`/emergency` — static prerender, server component, all data passed as
mock constants.

## Components

| Component                    | File                                                | Purpose                                              |
|------------------------------|-----------------------------------------------------|------------------------------------------------------|
| `EmergencyKpiStrip`          | `components/emergency/EmergencyKpiStrip.tsx`        | Live KPIs: active cases, P1s, avg response, capacity |
| `EmergencyAlertsQueue`       | `components/emergency/EmergencyAlertsQueue.tsx`     | Severity-sorted alert queue (P1→P4) with owner/pet   |
| `TriageEscalationSummary`    | `components/emergency/TriageEscalationSummary.tsx`  | Triage table with priority, status, elapsed time     |
| `EmergencyTimeline`          | `components/emergency/EmergencyTimeline.tsx`        | Chronological case event log                         |
| `ClinicAvailabilityBoard`    | `components/emergency/ClinicAvailabilityBoard.tsx`  | Nearby clinic cards with bed capacity and status     |
| `PreArrivalPacketPanel`      | `components/emergency/PreArrivalPacketPanel.tsx`    | Shared patient summary (vitals, meds, allergies)     |
| `HandoffStatusPanel`         | `components/emergency/HandoffStatusPanel.tsx`       | Inter-clinic transfer status                         |
| `EmergencyGovernanceSummary` | `components/emergency/EmergencyGovernanceSummary.tsx` | Response time SLA, consent, data-share compliance  |

## Types (`types/emergency.ts`)

- `EmergencyKpi`
- `EmergencyAlert` / `AlertSeverity` (`p1_critical`→`p4_minor`) / `AlertStatus`
- `TriageCase` / `TriagePriority` (`P1`–`P4`) / `TriageStatus`
- `EmergencyTimelineEvent` / `EmergencyEventType`
- `ClinicAvailability` / `ClinicStatus`
- `PreArrivalPacket` / `VitalReading`
- `HandoffRecord` / `HandoffStatus`
- `GovernanceEntry`

## Triage Priority Scheme

| Priority | Colour | Meaning                                  |
|----------|--------|------------------------------------------|
| P1       | Red    | Immediately life-threatening             |
| P2       | Orange | Urgent — deterioration likely            |
| P3       | Yellow | Moderate — stable, needs monitoring      |
| P4       | Blue   | Minor — can safely wait                  |

## Constraints

- No interactive dispatch, alert acknowledgement, or handoff creation in PH-UI-6.
- Pre-arrival packet is display-only; no transmission of real PII.
- Governance summary reflects mock data only.
- Real-time alert polling/WebSocket is out of scope for this phase.
- PDPL: consent field rendered for visibility; no consent mutation permitted.
