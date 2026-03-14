// ---------------------------------------------------------------------------
// Pharmacy surface types — PH-UI-5 read-only shell
// ---------------------------------------------------------------------------

export interface PharmacyKpi {
  label: string;
  value: string | number;
  unit?: string;
  variant: "default" | "success" | "warning" | "danger";
  sub?: string;
}

// ── Prescriptions ──────────────────────────────────────────────────────────

export type PrescriptionStatus =
  | "pending_verification"
  | "verified"
  | "dispensing"
  | "ready_for_collection"
  | "dispensed"
  | "cancelled"
  | "on_hold";

export interface PrescriptionItem {
  medicationName: string;
  strength: string;
  form: string; // tablet, liquid, injection, etc.
  quantity: number;
  unit: string;
  instructions: string;
}

export interface Prescription {
  id: string;
  petName: string;
  ownerName: string;
  vetName: string;
  issuedAt: string; // ISO datetime
  expiresAt: string; // ISO date
  status: PrescriptionStatus;
  items: PrescriptionItem[];
  notes: string | null;
  urgent: boolean;
}

// ── Dispense Workflow ──────────────────────────────────────────────────────

export type DispenseStepStatus = "pending" | "in_progress" | "complete" | "skipped" | "blocked";

export interface DispenseStep {
  id: string;
  order: number;
  label: string;
  description: string;
  status: DispenseStepStatus;
  completedBy: string | null;
  completedAt: string | null; // ISO datetime
}

// ── Inventory ──────────────────────────────────────────────────────────────

export type InventoryStatus = "in_stock" | "low_stock" | "out_of_stock" | "expiring_soon" | "expired";

export interface InventoryItem {
  id: string;
  medicationName: string;
  strength: string;
  form: string;
  batchNumber: string;
  quantityOnHand: number;
  quantityUnit: string;
  reorderLevel: number;
  expiryDate: string; // ISO date
  status: InventoryStatus;
  storageRequirement: "ambient" | "refrigerated" | "frozen";
  supplier: string;
}

// ── Medication Safety ──────────────────────────────────────────────────────

export type SafetyAlertLevel = "contraindication" | "interaction" | "caution";

export interface MedicationSafetyAlert {
  id: string;
  prescriptionId: string;
  alertLevel: SafetyAlertLevel;
  title: string;
  detail: string;
  medications: string[];
  acknowledged: boolean;
  raisedAt: string; // ISO datetime
}

// ── Cold Chain ─────────────────────────────────────────────────────────────

export type ColdChainStatus = "normal" | "warning" | "breach";

export interface ColdChainReading {
  id: string;
  sensorId: string;
  location: string;
  temperatureCelsius: number;
  targetMin: number;
  targetMax: number;
  status: ColdChainStatus;
  recordedAt: string; // ISO datetime
  alertSent: boolean;
}

// ── Recall Exceptions ──────────────────────────────────────────────────────

export type RecallSeverity = "class_i" | "class_ii" | "class_iii";
export type RecallStatus = "active" | "resolved" | "under_review";

export interface RecallException {
  id: string;
  medicationName: string;
  batchNumbers: string[];
  manufacturer: string;
  recallDate: string; // ISO date
  severity: RecallSeverity;
  status: RecallStatus;
  reason: string;
  unitsAffected: number;
  unitsQuarantined: number;
}

// ── Fulfillment & Dispatch ─────────────────────────────────────────────────

export type DispatchStatus =
  | "awaiting_collection"
  | "out_for_delivery"
  | "delivered"
  | "returned"
  | "failed";

export interface FulfillmentDispatch {
  id: string;
  prescriptionId: string;
  petName: string;
  ownerName: string;
  dispatchedAt: string; // ISO datetime
  estimatedDelivery: string | null; // ISO datetime
  status: DispatchStatus;
  method: "clinic_collection" | "home_delivery" | "courier";
  trackingRef: string | null;
}
