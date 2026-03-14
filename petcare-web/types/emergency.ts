// ---------------------------------------------------------------------------
// Emergency surface types — PH-UI-6 read-only shell
// ---------------------------------------------------------------------------

export interface EmergencyKpi {
  label: string;
  value: string | number;
  unit?: string;
  variant: "default" | "success" | "warning" | "danger" | "critical";
  sub?: string;
}

// ── Alerts ─────────────────────────────────────────────────────────────────

export type AlertSeverity = "p1_critical" | "p2_urgent" | "p3_moderate" | "p4_minor";
export type AlertStatus = "open" | "acknowledged" | "dispatched" | "resolved";

export interface EmergencyAlert {
  id: string;
  severity: AlertSeverity;
  status: AlertStatus;
  petName: string;
  species: string;
  ownerName: string;
  ownerPhone: string;
  chiefComplaint: string;
  raisedAt: string; // ISO datetime
  acknowledgedAt: string | null;
  dispatchedAt: string | null;
  assignedVet: string | null;
  location: string | null;
}

// ── Triage ─────────────────────────────────────────────────────────────────

export type TriagePriority = "P1" | "P2" | "P3" | "P4";
export type TriageStatus = "waiting" | "in_assessment" | "treatment" | "stable" | "transferred";

export interface TriageCase {
  id: string;
  priority: TriagePriority;
  status: TriageStatus;
  petName: string;
  species: string;
  age: string;
  ownerName: string;
  complaint: string;
  arrivalTime: string; // ISO datetime
  assignedVet: string | null;
  bay: string | null;
  notes: string | null;
}

// ── Timeline ───────────────────────────────────────────────────────────────

export type EmergencyEventType =
  | "alert_raised"
  | "acknowledged"
  | "triage_assessment"
  | "treatment_started"
  | "medication_given"
  | "vitals_recorded"
  | "handoff_initiated"
  | "handoff_complete"
  | "case_closed";

export interface EmergencyTimelineEvent {
  id: string;
  caseId: string;
  eventType: EmergencyEventType;
  timestamp: string; // ISO datetime
  actor: string;
  description: string;
  severity?: AlertSeverity;
}

// ── Clinic Availability ────────────────────────────────────────────────────

export type ClinicStatus = "open_emergency" | "limited" | "closed" | "on_call_only";

export interface ClinicAvailability {
  id: string;
  clinicName: string;
  distanceKm: number;
  status: ClinicStatus;
  emergencyBedsAvailable: number;
  emergencyBedsTotal: number;
  onCallVet: string | null;
  phoneNumber: string;
  specialisms: string[];
  acceptingCases: boolean;
}

// ── Pre-Arrival Packet ─────────────────────────────────────────────────────

export interface VitalReading {
  label: string;
  value: string;
  normal: boolean;
}

export interface PreArrivalPacket {
  caseId: string;
  petName: string;
  species: string;
  breed: string;
  ageYears: number;
  weightKg: number;
  microchipId: string | null;
  ownerName: string;
  ownerPhone: string;
  consentGiven: boolean;
  chiefComplaint: string;
  currentMedications: string[];
  knownAllergies: string[];
  lastVitals: VitalReading[];
  vaccinationStatus: "current" | "partial" | "unknown" | "overdue";
  sharedAt: string; // ISO datetime
}

// ── Handoff ────────────────────────────────────────────────────────────────

export type HandoffStatus =
  | "pending"
  | "in_transit"
  | "received"
  | "failed"
  | "cancelled";

export interface HandoffRecord {
  id: string;
  caseId: string;
  petName: string;
  fromClinic: string;
  toClinic: string;
  initiatedAt: string; // ISO datetime
  receivedAt: string | null;
  status: HandoffStatus;
  handoffVet: string;
  receivingVet: string | null;
  transportMode: "owner_vehicle" | "ambulance" | "clinic_transport";
  notes: string | null;
}

// ── Governance ─────────────────────────────────────────────────────────────

export interface GovernanceEntry {
  id: string;
  category: "response_time" | "consent" | "data_share" | "handoff_audit" | "sla";
  label: string;
  value: string;
  compliant: boolean;
  detail: string | null;
}
