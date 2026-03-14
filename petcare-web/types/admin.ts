// ---------------------------------------------------------------------------
// Admin surface types — PH-UI-4 read-only shell
// ---------------------------------------------------------------------------

export interface AdminKpi {
  label: string;
  value: string | number;
  unit?: string;
  trend?: "up" | "down" | "stable";
  trendLabel?: string;
  variant: "default" | "success" | "warning" | "danger";
}

// ── Clinic Operations ──────────────────────────────────────────────────────

export type ClinicStatus = "operational" | "degraded" | "closed";

export interface ClinicOperations {
  clinicName: string;
  status: ClinicStatus;
  capacityTotal: number;
  capacityUsed: number;
  appointmentsToday: number;
  appointmentsCompleted: number;
  openSince: string; // "HH:MM"
  closesAt: string;  // "HH:MM"
}

// ── Appointment Load ───────────────────────────────────────────────────────

export interface AppointmentSlot {
  id: string;
  time: string; // "HH:MM"
  patientName: string;
  petName: string;
  vetName: string;
  reason: string;
  status: "scheduled" | "in_progress" | "completed" | "no_show" | "cancelled";
}

// ── Vet Availability ───────────────────────────────────────────────────────

export type VetStatus = "available" | "in_consultation" | "break" | "off_duty";

export interface VetAvailability {
  id: string;
  name: string;
  specialisation: string;
  status: VetStatus;
  currentPatient: string | null;
  appointmentsRemaining: number;
  shiftsEndsAt: string | null; // "HH:MM"
}

// ── Alerts & Escalations ───────────────────────────────────────────────────

export type AlertSeverity = "info" | "warning" | "critical";
export type AlertCategory =
  | "overdue_vaccination"
  | "missed_appointment"
  | "consent_missing"
  | "system"
  | "compliance";

export interface Alert {
  id: string;
  severity: AlertSeverity;
  category: AlertCategory;
  title: string;
  description: string;
  raisedAt: string; // ISO datetime
  acknowledged: boolean;
}

// ── Audit Events ───────────────────────────────────────────────────────────

export type AuditAction =
  | "login"
  | "logout"
  | "record_view"
  | "consent_update"
  | "appointment_create"
  | "appointment_cancel"
  | "export_request"
  | "config_change";

export interface AuditEvent {
  id: string;
  timestamp: string; // ISO datetime
  actor: string;
  actorRole: "owner" | "vet" | "admin" | "system";
  action: AuditAction;
  resourceType: string;
  resourceId: string;
  outcome: "success" | "failure" | "denied";
  ipAddress: string | null;
}

// ── Evidence Export ────────────────────────────────────────────────────────

export type ExportFormat = "json" | "csv" | "pdf";

export interface ExportOption {
  id: string;
  label: string;
  description: string;
  format: ExportFormat;
  scope: string;
}

// ── Clinic Configuration ───────────────────────────────────────────────────

export interface ConfigEntry {
  key: string;
  label: string;
  value: string;
  editable: boolean;
}

export interface ClinicConfiguration {
  clinicId: string;
  clinicName: string;
  timezone: string;
  dataRetentionDays: number;
  pdplConsentVersion: string;
  entries: ConfigEntry[];
}
