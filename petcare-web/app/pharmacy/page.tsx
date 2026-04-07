import type {
  PharmacyKpi,
  Prescription,
  DispenseStep,
  InventoryItem,
  MedicationSafetyAlert,
  ColdChainReading,
  RecallException,
  FulfillmentDispatch,
} from "@/types/pharmacy";
import {
  PharmacyKpiStrip,
  PrescriptionQueue,
  DispenseWorkflowPreview,
  InventoryStatusSummary,
  MedicationSafetyPanel,
  ColdChainMonitor,
  RecallExceptionsPanel,
  FulfillmentDispatchSummary,
} from "@/components/pharmacy";

// ---------------------------------------------------------------------------
// Placeholder data — no real backend calls. PH-UI-5 read-only shell.
// ---------------------------------------------------------------------------

const KPIS: PharmacyKpi[] = [
  { label: "وصفات اليوم",      value: 18,  variant: "default"  },
  { label: "تم الصرف",         value: 12,  variant: "success"  },
  { label: "قيد الانتظار",     value: 4,   variant: "warning"  },
  { label: "تنبيهات السلامة",  value: 2,   variant: "danger"   },
  { label: "السلسلة الباردة",  value: "3/4", variant: "warning", sub: "1 تحذير" },
  { label: "استرجاعات نشطة",  value: 1,   variant: "danger"   },
];

const PRESCRIPTIONS: Prescription[] = [
  {
    id: "rx-001", petName: "Luna", ownerName: "Sara Al-Rashidi",
    vetName: "Dr. Khalid Al-Otaibi",
    issuedAt: "2026-03-14T09:00:00Z", expiresAt: "2026-04-14",
    status: "dispensing", urgent: true,
    items: [
      { medicationName: "Amoxicillin", strength: "250mg", form: "capsule", quantity: 14, unit: "capsules", instructions: "1 capsule twice daily with food" },
      { medicationName: "Prednisolone", strength: "5mg",  form: "tablet",  quantity: 7,  unit: "tablets",  instructions: "1 tablet once daily, taper over 7 days" },
    ],
    notes: "Dispensing in progress — verify second item.",
  },
  {
    id: "rx-002", petName: "Rex", ownerName: "Faisal Al-Harbi",
    vetName: "Dr. Nora Al-Qahtani",
    issuedAt: "2026-03-14T08:30:00Z", expiresAt: "2026-04-14",
    status: "ready_for_collection", urgent: false,
    items: [
      { medicationName: "Meloxicam", strength: "1.5mg/mL", form: "oral solution", quantity: 30, unit: "mL", instructions: "0.1mg/kg once daily with food for 5 days" },
    ],
    notes: null,
  },
  {
    id: "rx-003", petName: "Mimi", ownerName: "Mona Al-Zahrani",
    vetName: "Dr. Khalid Al-Otaibi",
    issuedAt: "2026-03-14T10:15:00Z", expiresAt: "2026-04-14",
    status: "pending_verification", urgent: false,
    items: [
      { medicationName: "Fenbendazole", strength: "150mg", form: "granules", quantity: 3, unit: "sachets", instructions: "1 sachet daily for 3 days mixed with food" },
    ],
    notes: null,
  },
  {
    id: "rx-004", petName: "Buddy", ownerName: "Omar Al-Ghamdi",
    vetName: "Dr. Ahmed Al-Shehri",
    issuedAt: "2026-03-13T14:00:00Z", expiresAt: "2026-04-13",
    status: "on_hold", urgent: false,
    items: [
      { medicationName: "Cyclosporine", strength: "25mg", form: "capsule", quantity: 30, unit: "capsules", instructions: "25mg once daily on empty stomach" },
    ],
    notes: "On hold — safety interaction review pending.",
  },
];

const DISPENSE_STEPS: DispenseStep[] = [
  { id: "ds-1", order: 1, label: "Prescription Verification",   description: "Confirm Rx authenticity, vet signature, expiry", status: "complete",     completedBy: "Pharm. Aisha", completedAt: "2026-03-14T09:05:00Z" },
  { id: "ds-2", order: 2, label: "Safety Check",                description: "Drug interaction and contraindication screen",   status: "complete",     completedBy: "Pharm. Aisha", completedAt: "2026-03-14T09:07:00Z" },
  { id: "ds-3", order: 3, label: "Product Pull & Count",        description: "Retrieve items from inventory, count and verify", status: "in_progress", completedBy: null,           completedAt: null },
  { id: "ds-4", order: 4, label: "Label & Package",             description: "Print dispensing label, package per instructions", status: "pending",   completedBy: null,           completedAt: null },
  { id: "ds-5", order: 5, label: "Final Pharmacist Sign-Off",   description: "Pharmacist reviews and signs before release",    status: "pending",     completedBy: null,           completedAt: null },
  { id: "ds-6", order: 6, label: "Owner Handoff / Dispatch",    description: "Dispense to owner or initiate delivery",         status: "pending",     completedBy: null,           completedAt: null },
];

const INVENTORY: InventoryItem[] = [
  { id: "inv-1", medicationName: "Amoxicillin",   strength: "250mg",     form: "capsule",       batchNumber: "AMX-2025-09", quantityOnHand: 48,  quantityUnit: "caps",  reorderLevel: 100, expiryDate: "2027-03-01", status: "low_stock",      storageRequirement: "ambient",      supplier: "VetPharm KSA"     },
  { id: "inv-2", medicationName: "Meloxicam",      strength: "1.5mg/mL",  form: "oral solution", batchNumber: "MEL-2024-11", quantityOnHand: 12,  quantityUnit: "bottle",reorderLevel: 10,  expiryDate: "2026-06-15", status: "in_stock",       storageRequirement: "refrigerated", supplier: "Gulf Medical Dist" },
  { id: "inv-3", medicationName: "Prednisolone",   strength: "5mg",       form: "tablet",        batchNumber: "PRD-2023-07", quantityOnHand: 200, quantityUnit: "tabs",  reorderLevel: 50,  expiryDate: "2026-03-28", status: "expiring_soon",  storageRequirement: "ambient",      supplier: "VetPharm KSA"     },
  { id: "inv-4", medicationName: "Cyclosporine",   strength: "25mg",      form: "capsule",       batchNumber: "CYC-2022-04", quantityOnHand: 0,   quantityUnit: "caps",  reorderLevel: 20,  expiryDate: "2025-12-01", status: "out_of_stock",   storageRequirement: "refrigerated", supplier: "MedVet Import"    },
  { id: "inv-5", medicationName: "Fenbendazole",   strength: "150mg",     form: "granules",      batchNumber: "FBZ-2025-01", quantityOnHand: 30,  quantityUnit: "sachets",reorderLevel: 15, expiryDate: "2027-01-01", status: "in_stock",       storageRequirement: "ambient",      supplier: "Gulf Medical Dist" },
  { id: "inv-6", medicationName: "Dexamethasone",  strength: "2mg/mL",    form: "injection",     batchNumber: "DEX-2021-12", quantityOnHand: 5,   quantityUnit: "vials", reorderLevel: 10,  expiryDate: "2025-11-01", status: "expired",        storageRequirement: "refrigerated", supplier: "VetPharm KSA"     },
];

const SAFETY_ALERTS: MedicationSafetyAlert[] = [
  {
    id: "sa-1", prescriptionId: "rx-004", alertLevel: "interaction",
    title: "Cyclosporine + NSAIDs — Nephrotoxicity Risk",
    detail: "Concurrent use of Cyclosporine and NSAIDs significantly increases the risk of nephrotoxicity. Review prior NSAID use before dispensing.",
    medications: ["Cyclosporine 25mg", "Meloxicam 1.5mg/mL"],
    acknowledged: false, raisedAt: "2026-03-14T09:20:00Z",
  },
  {
    id: "sa-2", prescriptionId: "rx-001", alertLevel: "caution",
    title: "Prednisolone — GI Protection Recommended",
    detail: "Long-term corticosteroid use in cats may cause GI irritation. Consider gastric protectant.",
    medications: ["Prednisolone 5mg"],
    acknowledged: true, raisedAt: "2026-03-14T09:06:00Z",
  },
];

const COLD_CHAIN: ColdChainReading[] = [
  { id: "cc-1", sensorId: "SENS-01", location: "Fridge A — Vaccines",       temperatureCelsius: 4.2,   targetMin: 2, targetMax: 8,  status: "normal",  recordedAt: "2026-03-14T10:50:00Z", alertSent: false },
  { id: "cc-2", sensorId: "SENS-02", location: "Fridge B — Injectables",    temperatureCelsius: 9.1,   targetMin: 2, targetMax: 8,  status: "warning", recordedAt: "2026-03-14T10:50:00Z", alertSent: true  },
  { id: "cc-3", sensorId: "SENS-03", location: "Freezer — Biologics",       temperatureCelsius: -15.4, targetMin: -20, targetMax: -10, status: "normal", recordedAt: "2026-03-14T10:50:00Z", alertSent: false },
  { id: "cc-4", sensorId: "SENS-04", location: "Ambient Store — Oral Meds", temperatureCelsius: 22.3,  targetMin: 15, targetMax: 25,  status: "normal", recordedAt: "2026-03-14T10:50:00Z", alertSent: false },
];

const RECALLS: RecallException[] = [
  {
    id: "rc-1", medicationName: "Dexamethasone 2mg/mL Injection",
    batchNumbers: ["DEX-2021-12", "DEX-2021-13"],
    manufacturer: "VetPharm KSA", recallDate: "2026-02-20",
    severity: "class_ii", status: "active",
    reason: "Possible particulate contamination identified in batch. Risk of local reaction on injection.",
    unitsAffected: 120, unitsQuarantined: 5,
  },
];

const DISPATCHES: FulfillmentDispatch[] = [
  { id: "fd-1", prescriptionId: "rx-002", petName: "Rex",  ownerName: "Faisal Al-Harbi",  dispatchedAt: "2026-03-14T11:00:00Z", estimatedDelivery: null,                      status: "awaiting_collection", method: "clinic_collection", trackingRef: null         },
  { id: "fd-2", prescriptionId: "rx-005", petName: "Cleo", ownerName: "Reem Al-Otaibi",   dispatchedAt: "2026-03-13T15:30:00Z", estimatedDelivery: "2026-03-14T14:00:00Z",    status: "out_for_delivery",    method: "home_delivery",     trackingRef: "TRK-0081"   },
  { id: "fd-3", prescriptionId: "rx-006", petName: "Max",  ownerName: "Turki Al-Dossari", dispatchedAt: "2026-03-12T09:00:00Z", estimatedDelivery: "2026-03-12T17:00:00Z",    status: "delivered",           method: "courier",           trackingRef: "TRK-0074"   },
];

// ---------------------------------------------------------------------------

export default function PharmacyPage() {
  return (
    <div className="space-y-8 max-w-5xl">
      {/* Header */}
      <div>
        <h1 className="text-xl font-semibold text-gray-900">الصيدلية</h1>
        <p className="mt-1 text-sm text-gray-500">
          واجهة العمليات — قراءة فقط · بيانات تجريبية · PH-UI-5
        </p>
      </div>

      {/* KPIs */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          المؤشرات الرئيسية
        </h2>
        <PharmacyKpiStrip kpis={KPIS} />
      </section>

      {/* Safety Alerts */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          سلامة الدواء
        </h2>
        <MedicationSafetyPanel alerts={SAFETY_ALERTS} />
      </section>

      {/* Prescription Queue */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          قائمة انتظار الوصفات
        </h2>
        <PrescriptionQueue prescriptions={PRESCRIPTIONS} />
      </section>

      {/* Dispense Workflow */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          سير صرف الدواء — rx-001 (لونا)
        </h2>
        <DispenseWorkflowPreview steps={DISPENSE_STEPS} prescriptionRef="rx-001" />
      </section>

      {/* Cold Chain */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          مراقبة السلسلة الباردة
        </h2>
        <ColdChainMonitor readings={COLD_CHAIN} />
      </section>

      {/* Inventory */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          حالة المخزون
        </h2>
        <InventoryStatusSummary items={INVENTORY} />
      </section>

      {/* Recalls */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          استثناءات الاسترجاع
        </h2>
        <RecallExceptionsPanel recalls={RECALLS} />
      </section>

      {/* Fulfillment */}
      <section className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          التنفيذ والشحن
        </h2>
        <FulfillmentDispatchSummary dispatches={DISPATCHES} />
      </section>
    </div>
  );
}
