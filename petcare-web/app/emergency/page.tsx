import type {
  EmergencyKpi,
  EmergencyAlert,
  TriageCase,
  EmergencyTimelineEvent,
  ClinicAvailability,
  PreArrivalPacket,
  HandoffRecord,
  GovernanceEntry,
} from "@/types/emergency";
import {
  EmergencyKpiStrip,
  EmergencyAlertsQueue,
  TriageEscalationSummary,
  EmergencyTimeline,
  ClinicAvailabilityBoard,
  PreArrivalPacketPanel,
  HandoffStatusPanel,
  EmergencyGovernanceSummary,
} from "@/components/emergency";

// ---------------------------------------------------------------------------
// Placeholder data — no real backend calls. PH-UI-6 read-only shell.
// ---------------------------------------------------------------------------

const KPIS: EmergencyKpi[] = [
  { label: "Active Cases",    value: 3,      variant: "danger",   sub: "1 × P1" },
  { label: "P1 Critical",    value: 1,      variant: "critical"                },
  { label: "Avg Response",   value: "4.2",  unit: "min", variant: "warning"   },
  { label: "Clinics Open",   value: "2/4",  variant: "warning"                 },
  { label: "Handoffs Today", value: 2,      variant: "default"                 },
  { label: "SLA Compliance", value: "83",   unit: "%",   variant: "warning"   },
];

const ALERTS: EmergencyAlert[] = [
  {
    id: "ea-1", severity: "p1_critical", status: "dispatched",
    petName: "Rex",   species: "Dog",
    ownerName: "Faisal Al-Harbi", ownerPhone: "+966 50 000 0011",
    chiefComplaint: "Suspected gastric dilatation-volvulus (GDV). Rapid abdominal distension, unproductive retching.",
    raisedAt: "2026-03-14T10:42:00Z", acknowledgedAt: "2026-03-14T10:43:30Z",
    dispatchedAt: "2026-03-14T10:45:00Z",
    assignedVet: "Dr. Nora Al-Qahtani", location: "Riyadh — Al Malaz",
  },
  {
    id: "ea-2", severity: "p2_urgent", status: "acknowledged",
    petName: "Luna",  species: "Cat",
    ownerName: "Sara Al-Rashidi", ownerPhone: "+966 50 000 0001",
    chiefComplaint: "Respiratory distress. Laboured breathing, blue-tinged gums observed.",
    raisedAt: "2026-03-14T11:05:00Z", acknowledgedAt: "2026-03-14T11:07:00Z",
    dispatchedAt: null, assignedVet: "Dr. Khalid Al-Otaibi", location: "Riyadh — Al Wurud",
  },
  {
    id: "ea-3", severity: "p3_moderate", status: "open",
    petName: "Koko",  species: "Rabbit",
    ownerName: "Hessa Al-Mutairi", ownerPhone: "+966 50 000 0033",
    chiefComplaint: "Not eating for 24 hours. Reduced faecal output. Suspected GI stasis.",
    raisedAt: "2026-03-14T11:20:00Z", acknowledgedAt: null,
    dispatchedAt: null, assignedVet: null, location: null,
  },
];

const TRIAGE_CASES: TriageCase[] = [
  {
    id: "tc-1", priority: "P1", status: "treatment",
    petName: "Rex",  species: "Dog",   age: "4y",
    ownerName: "Faisal Al-Harbi",
    complaint: "GDV — gastric dilatation-volvulus",
    arrivalTime: "2026-03-14T10:55:00Z",
    assignedVet: "Dr. Nora", bay: "ER-1", notes: "Pre-op stabilisation in progress",
  },
  {
    id: "tc-2", priority: "P2", status: "in_assessment",
    petName: "Luna", species: "Cat",   age: "5y",
    ownerName: "Sara Al-Rashidi",
    complaint: "Respiratory distress — pleural effusion suspected",
    arrivalTime: "2026-03-14T11:15:00Z",
    assignedVet: "Dr. Khalid", bay: "ER-2", notes: null,
  },
  {
    id: "tc-3", priority: "P3", status: "waiting",
    petName: "Koko", species: "Rabbit", age: "2y",
    ownerName: "Hessa Al-Mutairi",
    complaint: "GI stasis — 24h anorexia, reduced output",
    arrivalTime: "2026-03-14T11:35:00Z",
    assignedVet: null, bay: null, notes: null,
  },
];

const TIMELINE_EVENTS: EmergencyTimelineEvent[] = [
  { id: "te-1", caseId: "tc-1", eventType: "alert_raised",      timestamp: "2026-03-14T10:42:00Z", actor: "System (owner app)",     description: "Emergency alert raised: GDV suspected. Owner reported rapid abdominal distension." },
  { id: "te-2", caseId: "tc-1", eventType: "acknowledged",       timestamp: "2026-03-14T10:43:30Z", actor: "Dr. Nora Al-Qahtani",   description: "Alert acknowledged. Dispatching emergency team." },
  { id: "te-3", caseId: "tc-1", eventType: "triage_assessment",  timestamp: "2026-03-14T10:57:00Z", actor: "Dr. Nora Al-Qahtani",   description: "P1 triage confirmed. Distended abdomen, weak pulse. Assigned ER-1." },
  { id: "te-4", caseId: "tc-1", eventType: "vitals_recorded",    timestamp: "2026-03-14T10:59:00Z", actor: "Nurse Fatima",          description: "HR 160bpm, RR 40rpm, SpO2 88%, temp 38.9°C, CRT >2s." },
  { id: "te-5", caseId: "tc-1", eventType: "medication_given",   timestamp: "2026-03-14T11:02:00Z", actor: "Dr. Nora Al-Qahtani",   description: "IV fluids started. Butorphanol 0.2mg/kg IV for pain management." },
  { id: "te-6", caseId: "tc-1", eventType: "treatment_started",  timestamp: "2026-03-14T11:08:00Z", actor: "Dr. Nora Al-Qahtani",   description: "Stomach decompression initiated. IV catheter placed. Pre-op bloodwork ordered." },
];

const CLINICS: ClinicAvailability[] = [
  { id: "cl-1", clinicName: "Riyadh Central Vet Clinic",       distanceKm: 0.0,  status: "open_emergency",  emergencyBedsAvailable: 2, emergencyBedsTotal: 4, onCallVet: "Dr. Nora Al-Qahtani",  phoneNumber: "+966 11 000 0001", specialisms: ["Surgery", "Internal Medicine"], acceptingCases: true  },
  { id: "cl-2", clinicName: "Al Malaz Emergency Vet",          distanceKm: 3.2,  status: "open_emergency",  emergencyBedsAvailable: 3, emergencyBedsTotal: 6, onCallVet: "Dr. Sami Al-Harbi",    phoneNumber: "+966 11 000 0002", specialisms: ["Cardiology", "Neurology"],      acceptingCases: true  },
  { id: "cl-3", clinicName: "Olaya 24hr Animal Hospital",      distanceKm: 5.8,  status: "limited",         emergencyBedsAvailable: 1, emergencyBedsTotal: 5, onCallVet: "Dr. Leila Al-Matrafi", phoneNumber: "+966 11 000 0003", specialisms: ["General Practice"],            acceptingCases: true  },
  { id: "cl-4", clinicName: "King Fahd Road Vet Centre",       distanceKm: 9.1,  status: "on_call_only",    emergencyBedsAvailable: 0, emergencyBedsTotal: 3, onCallVet: "Dr. Ahmed Al-Shehri",  phoneNumber: "+966 11 000 0004", specialisms: ["Dermatology", "Dentistry"],    acceptingCases: false },
];

const PRE_ARRIVAL: PreArrivalPacket = {
  caseId: "tc-1",
  petName: "Rex", species: "Dog", breed: "German Shepherd",
  ageYears: 4, weightKg: 32.5, microchipId: "982000987654321",
  ownerName: "Faisal Al-Harbi", ownerPhone: "+966 50 000 0011",
  consentGiven: true,
  chiefComplaint: "Suspected GDV — rapid abdominal distension, unproductive retching, restlessness.",
  currentMedications: ["Rimadyl 75mg (carprofen) — once daily", "Probiotic supplement — daily"],
  knownAllergies: ["Penicillin-class antibiotics"],
  lastVitals: [
    { label: "HR",   value: "160 bpm",  normal: false },
    { label: "RR",   value: "40 rpm",   normal: false },
    { label: "SpO2", value: "88%",      normal: false },
    { label: "Temp", value: "38.9°C",   normal: true  },
    { label: "CRT",  value: ">2 sec",   normal: false },
    { label: "BP",   value: "80/50 mmHg", normal: false },
  ],
  vaccinationStatus: "current",
  sharedAt: "2026-03-14T10:44:00Z",
};

const HANDOFFS: HandoffRecord[] = [
  {
    id: "hf-1", caseId: "tc-1", petName: "Rex",
    fromClinic: "Riyadh Central Vet Clinic",
    toClinic: "Al Malaz Emergency Vet — Surgical Suite",
    initiatedAt: "2026-03-14T11:30:00Z", receivedAt: null,
    status: "in_transit", handoffVet: "Dr. Nora Al-Qahtani",
    receivingVet: "Dr. Sami Al-Harbi",
    transportMode: "ambulance",
    notes: "Patient stabilised pre-transit. Surgery prep requested at receiving clinic.",
  },
  {
    id: "hf-2", caseId: "tc-4", petName: "Max",
    fromClinic: "Al Malaz Emergency Vet",
    toClinic: "Riyadh Central Vet Clinic",
    initiatedAt: "2026-03-14T08:00:00Z", receivedAt: "2026-03-14T08:22:00Z",
    status: "received", handoffVet: "Dr. Khalid Al-Otaibi",
    receivingVet: "Dr. Ahmed Al-Shehri",
    transportMode: "owner_vehicle",
    notes: null,
  },
];

const GOVERNANCE: GovernanceEntry[] = [
  { id: "g1", category: "response_time",  label: "P1 Acknowledgement SLA",  value: "< 2 min",    compliant: true,  detail: "Actual: 1m 30s"                            },
  { id: "g2", category: "response_time",  label: "P2 Acknowledgement SLA",  value: "< 5 min",    compliant: true,  detail: "Actual: 2m 00s"                            },
  { id: "g3", category: "response_time",  label: "P3 Acknowledgement SLA",  value: "< 15 min",   compliant: false, detail: "Koko (ea-3) unacknowledged — 18m elapsed"  },
  { id: "g4", category: "consent",        label: "Emergency Consent on File", value: "2/3 cases", compliant: false, detail: "Koko (tc-3) — consent not confirmed"        },
  { id: "g5", category: "data_share",     label: "Pre-Arrival Packet Shared", value: "1/3 cases", compliant: true,  detail: "Shared for tc-1 (Rex)"                     },
  { id: "g6", category: "handoff_audit",  label: "Handoff Records Complete",  value: "2/2",       compliant: true,  detail: "Both transfers fully documented"            },
  { id: "g7", category: "sla",            label: "Overall SLA Pass Rate",     value: "83%",       compliant: false, detail: "4/5 checks passing this session"            },
];

// ---------------------------------------------------------------------------

export default function EmergencyPage() {
  return (
    <div className="space-y-8 max-w-5xl">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div>
          <h1 className="text-xl font-semibold text-gray-900">Emergency</h1>
          <p className="mt-1 text-sm text-gray-500">
            Coordination surface — read-only shell · placeholder data · PH-UI-6
          </p>
        </div>
        <span className="ml-auto rounded bg-red-600 px-3 py-1 text-xs font-bold text-white animate-pulse">
          1 × P1 ACTIVE
        </span>
      </div>

      {/* KPIs */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          Live Metrics
        </h2>
        <EmergencyKpiStrip kpis={KPIS} />
      </section>

      {/* Alerts Queue */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          Alert Queue
        </h2>
        <EmergencyAlertsQueue alerts={ALERTS} />
      </section>

      {/* Triage */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          Triage Escalation Board
        </h2>
        <TriageEscalationSummary cases={TRIAGE_CASES} />
      </section>

      {/* Clinic Availability */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          Clinic Availability
        </h2>
        <ClinicAvailabilityBoard clinics={CLINICS} />
      </section>

      {/* Pre-Arrival Packet */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          Pre-Arrival Packet — Rex (tc-1)
        </h2>
        <PreArrivalPacketPanel packet={PRE_ARRIVAL} />
      </section>

      {/* Case Timeline */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          Case Timeline — Rex (tc-1)
        </h2>
        <EmergencyTimeline events={TIMELINE_EVENTS} caseLabel="tc-1 · Rex · GDV" />
      </section>

      {/* Handoff */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          Handoff Status
        </h2>
        <HandoffStatusPanel handoffs={HANDOFFS} />
      </section>

      {/* Governance */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          Emergency Governance
        </h2>
        <EmergencyGovernanceSummary entries={GOVERNANCE} />
      </section>
    </div>
  );
}
