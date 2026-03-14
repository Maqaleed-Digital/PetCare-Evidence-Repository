import type {
  AdminKpi,
  ClinicOperations,
  AppointmentSlot,
  VetAvailability,
  Alert,
  AuditEvent,
  ExportOption,
  ClinicConfiguration,
} from "@/types/admin";
import {
  AdminKpiStrip,
  ClinicOperationsOverview,
  AppointmentLoadBoard,
  VetAvailabilityPanel,
  AlertsEscalationsPanel,
  AuditEventViewer,
  EvidenceExportPanel,
  ClinicConfigurationSummary,
} from "@/components/admin";

// ---------------------------------------------------------------------------
// Placeholder data — no real backend calls. PH-UI-4 read-only shell.
// ---------------------------------------------------------------------------

const KPIS: AdminKpi[] = [
  { label: "Patients Registered", value: 312, variant: "default", trend: "up", trendLabel: "vs last week" },
  { label: "Appointments Today", value: 24, variant: "default" },
  { label: "Completed", value: 17, variant: "success" },
  { label: "Vets On Duty", value: 4, variant: "default" },
  { label: "Active Alerts", value: 3, variant: "warning" },
  { label: "No-Shows", value: 2, variant: "danger" },
];

const CLINIC_OPS: ClinicOperations = {
  clinicName: "Riyadh Central Vet Clinic",
  status: "operational",
  capacityTotal: 30,
  capacityUsed: 24,
  appointmentsToday: 24,
  appointmentsCompleted: 17,
  openSince: "08:00",
  closesAt: "20:00",
};

const SLOTS: AppointmentSlot[] = [
  { id: "s1", time: "08:00", patientName: "Sara Al-Rashidi",  petName: "Luna",   vetName: "Dr. Khalid", reason: "Annual wellness",        status: "completed"    },
  { id: "s2", time: "09:00", patientName: "Faisal Al-Harbi",  petName: "Rex",    vetName: "Dr. Nora",   reason: "Post-surgery follow-up", status: "completed"    },
  { id: "s3", time: "10:00", patientName: "Mona Al-Zahrani",  petName: "Mimi",   vetName: "Dr. Khalid", reason: "Vaccination booster",    status: "in_progress"  },
  { id: "s4", time: "11:00", patientName: "Omar Al-Ghamdi",   petName: "Buddy",  vetName: "Dr. Ahmed",  reason: "Skin allergy check",     status: "scheduled"    },
  { id: "s5", time: "11:30", patientName: "Reem Al-Otaibi",   petName: "Cleo",   vetName: "Dr. Nora",   reason: "Dental scaling",         status: "scheduled"    },
  { id: "s6", time: "09:30", patientName: "Turki Al-Dossari", petName: "Max",    vetName: "Dr. Leila",  reason: "General check",          status: "no_show"      },
  { id: "s7", time: "10:30", patientName: "Hessa Al-Mutairi", petName: "Koko",   vetName: "Dr. Ahmed",  reason: "Weight management",      status: "cancelled"    },
];

const VETS: VetAvailability[] = [
  { id: "v1", name: "Dr. Khalid Al-Otaibi", specialisation: "General Practice",  status: "in_consultation", currentPatient: "Mimi",  appointmentsRemaining: 3, shiftsEndsAt: "16:00" },
  { id: "v2", name: "Dr. Nora Al-Qahtani",  specialisation: "Surgery & Dental",  status: "available",        currentPatient: null,    appointmentsRemaining: 4, shiftsEndsAt: "18:00" },
  { id: "v3", name: "Dr. Ahmed Al-Shehri",  specialisation: "Dermatology",       status: "break",            currentPatient: null,    appointmentsRemaining: 2, shiftsEndsAt: "17:00" },
  { id: "v4", name: "Dr. Leila Al-Matrafi", specialisation: "Nutrition & Diet",  status: "available",        currentPatient: null,    appointmentsRemaining: 5, shiftsEndsAt: "19:00" },
  { id: "v5", name: "Dr. Sami Al-Harbi",    specialisation: "Cardiology",        status: "off_duty",         currentPatient: null,    appointmentsRemaining: 0, shiftsEndsAt: null    },
];

const ALERTS: Alert[] = [
  {
    id: "a1", severity: "critical", category: "compliance",
    title: "Consent Missing — 3 Patients",
    description: "3 patient records have no PDPL consent on file. Review required before next appointment.",
    raisedAt: "2026-03-14T07:30:00Z", acknowledged: false,
  },
  {
    id: "a2", severity: "warning", category: "overdue_vaccination",
    title: "Overdue Vaccinations — 12 Pets",
    description: "12 registered pets have one or more overdue vaccinations. Owner notifications pending.",
    raisedAt: "2026-03-14T06:00:00Z", acknowledged: false,
  },
  {
    id: "a3", severity: "warning", category: "missed_appointment",
    title: "No-Shows Today — 2",
    description: "2 patients did not attend scheduled appointments. Slots have been released.",
    raisedAt: "2026-03-14T10:05:00Z", acknowledged: true,
  },
];

const AUDIT_EVENTS: AuditEvent[] = [
  { id: "e1", timestamp: "2026-03-14T08:02:11Z", actor: "admin@clinic.sa",   actorRole: "admin",  action: "login",              resourceType: "session",     resourceId: "sess-001", outcome: "success", ipAddress: "10.0.0.1"   },
  { id: "e2", timestamp: "2026-03-14T08:15:33Z", actor: "dr.khalid@clinic.sa", actorRole: "vet",  action: "record_view",        resourceType: "patient",     resourceId: "pet-001",  outcome: "success", ipAddress: "10.0.0.12"  },
  { id: "e3", timestamp: "2026-03-14T09:01:07Z", actor: "sara@example.com",  actorRole: "owner", action: "consent_update",     resourceType: "consent",     resourceId: "con-042",  outcome: "success", ipAddress: null         },
  { id: "e4", timestamp: "2026-03-14T09:45:00Z", actor: "system",            actorRole: "system", action: "export_request",    resourceType: "audit_log",   resourceId: "all",      outcome: "denied",  ipAddress: null         },
  { id: "e5", timestamp: "2026-03-14T10:12:55Z", actor: "reem@example.com",  actorRole: "owner", action: "appointment_cancel", resourceType: "appointment", resourceId: "appt-011", outcome: "success", ipAddress: "172.16.0.5" },
];

const EXPORT_OPTIONS: ExportOption[] = [
  { id: "ex1", label: "Full Audit Log",      description: "All audit events for the current month",    format: "json", scope: "audit_log/current_month" },
  { id: "ex2", label: "Appointment Report",  description: "All appointments — date range selectable",  format: "csv",  scope: "appointments/all"        },
  { id: "ex3", label: "Compliance Summary",  description: "PDPL consent status and gaps report",       format: "pdf",  scope: "compliance/pdpl"         },
  { id: "ex4", label: "Vaccination Report",  description: "Overdue and due-soon vaccinations export",  format: "csv",  scope: "vaccinations/due"        },
];

const CLINIC_CONFIG: ClinicConfiguration = {
  clinicId: "clinic-001",
  clinicName: "Riyadh Central Vet Clinic",
  timezone: "Asia/Riyadh",
  dataRetentionDays: 2555,
  pdplConsentVersion: "v2.1.0",
  entries: [
    { key: "lang",          label: "Default Language",   value: "ar",                          editable: false },
    { key: "currency",      label: "Currency",           value: "SAR",                         editable: false },
    { key: "appointment_interval", label: "Slot Interval", value: "30 min",                  editable: true  },
    { key: "max_daily_capacity",   label: "Daily Capacity", value: "30",                     editable: true  },
    { key: "emergency_contact",    label: "Emergency Line",  value: "+966 11 000 0000",      editable: true  },
    { key: "api_base_url",         label: "API Base URL",    value: "https://api.myveticare.com", editable: false },
  ],
};

// ---------------------------------------------------------------------------

export default function AdminPage() {
  return (
    <div className="space-y-8 max-w-5xl">
      {/* Header */}
      <div>
        <h1 className="text-xl font-semibold text-gray-900">Admin Portal</h1>
        <p className="mt-1 text-sm text-gray-500">
          Clinic control surface — read-only shell · placeholder data · PH-UI-4
        </p>
      </div>

      {/* KPI Strip */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          Key Metrics
        </h2>
        <AdminKpiStrip kpis={KPIS} />
      </section>

      {/* Clinic Operations */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          Clinic Operations
        </h2>
        <ClinicOperationsOverview ops={CLINIC_OPS} />
      </section>

      {/* Alerts */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          Alerts & Escalations
        </h2>
        <AlertsEscalationsPanel alerts={ALERTS} />
      </section>

      {/* Vet Availability */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          Vet Availability
        </h2>
        <VetAvailabilityPanel vets={VETS} />
      </section>

      {/* Appointment Load Board */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          Appointment Load Board — Today
        </h2>
        <AppointmentLoadBoard slots={SLOTS} />
      </section>

      {/* Audit Event Viewer */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          Audit Events
        </h2>
        <AuditEventViewer events={AUDIT_EVENTS} />
      </section>

      {/* Evidence Export */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          Evidence Export
        </h2>
        <EvidenceExportPanel options={EXPORT_OPTIONS} />
      </section>

      {/* Clinic Configuration */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          Clinic Configuration
        </h2>
        <ClinicConfigurationSummary config={CLINIC_CONFIG} />
      </section>
    </div>
  );
}
