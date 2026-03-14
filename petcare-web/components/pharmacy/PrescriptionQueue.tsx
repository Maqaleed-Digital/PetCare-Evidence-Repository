import type { Prescription, PrescriptionStatus } from "@/types/pharmacy";

interface PrescriptionQueueProps {
  prescriptions: Prescription[];
}

type Status = PrescriptionStatus;

const STATUS_STYLES: Record<Status, string> = {
  pending_verification:    "bg-yellow-50 text-yellow-800 border-yellow-200",
  verified:                "bg-blue-50 text-blue-800 border-blue-200",
  dispensing:              "bg-indigo-50 text-indigo-800 border-indigo-200",
  ready_for_collection:    "bg-green-50 text-green-700 border-green-200",
  dispensed:               "bg-gray-100 text-gray-600 border-gray-200",
  cancelled:               "bg-red-50 text-red-700 border-red-200",
  on_hold:                 "bg-orange-50 text-orange-700 border-orange-200",
};

const STATUS_LABEL: Record<Status, string> = {
  pending_verification:  "Pending",
  verified:              "Verified",
  dispensing:            "Dispensing",
  ready_for_collection:  "Ready",
  dispensed:             "Dispensed",
  cancelled:             "Cancelled",
  on_hold:               "On Hold",
};

function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString("en-GB", {
    day: "numeric", month: "short", hour: "2-digit", minute: "2-digit",
  });
}

export function PrescriptionQueue({ prescriptions }: PrescriptionQueueProps) {
  if (prescriptions.length === 0) {
    return <p className="text-sm text-gray-400 italic">No prescriptions in queue.</p>;
  }

  return (
    <div className="space-y-3">
      {prescriptions.map((rx) => (
        <div
          key={rx.id}
          className={`rounded-lg border bg-white p-4 space-y-2 ${
            rx.urgent ? "border-l-4 border-l-red-400" : "border-gray-200"
          }`}
        >
          <div className="flex items-start justify-between gap-2 flex-wrap">
            <div>
              <div className="flex items-center gap-2">
                <p className="text-sm font-semibold text-gray-900">
                  {rx.petName}
                </p>
                {rx.urgent && (
                  <span className="rounded bg-red-100 text-red-700 px-1.5 py-0.5 text-xs font-bold">
                    URGENT
                  </span>
                )}
              </div>
              <p className="text-xs text-gray-500">
                Owner: {rx.ownerName} · Vet: {rx.vetName}
              </p>
            </div>
            <span
              className={`shrink-0 rounded border px-2 py-0.5 text-xs font-medium ${STATUS_STYLES[rx.status]}`}
            >
              {STATUS_LABEL[rx.status]}
            </span>
          </div>

          <ul className="text-xs text-gray-700 space-y-0.5 pl-3">
            {rx.items.map((item, i) => (
              <li key={i} className="list-disc list-inside">
                {item.medicationName} {item.strength} · {item.quantity} {item.unit} · {item.form}
              </li>
            ))}
          </ul>

          <div className="flex gap-4 text-xs text-gray-400">
            <span>Issued: {formatDateTime(rx.issuedAt)}</span>
            <span>Expires: {rx.expiresAt}</span>
          </div>

          {rx.notes && (
            <p className="text-xs text-gray-500 italic border-t border-gray-100 pt-2">
              {rx.notes}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}
