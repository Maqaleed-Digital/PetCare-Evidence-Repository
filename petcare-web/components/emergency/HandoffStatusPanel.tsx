import type { HandoffRecord, HandoffStatus } from "@/types/emergency";

interface HandoffStatusPanelProps {
  handoffs: HandoffRecord[];
}

type Status = HandoffStatus;

const STATUS_STYLES: Record<Status, string> = {
  pending:    "border-yellow-200 bg-yellow-50 text-yellow-800",
  in_transit: "border-blue-200 bg-blue-50 text-blue-800",
  received:   "border-green-200 bg-green-50 text-green-800",
  failed:     "border-red-200 bg-red-50 text-red-800",
  cancelled:  "border-gray-200 bg-gray-100 text-gray-500",
};

const STATUS_LABEL: Record<Status, string> = {
  pending:    "Pending",
  in_transit: "In Transit",
  received:   "Received",
  failed:     "Failed",
  cancelled:  "Cancelled",
};

const MODE_LABEL: Record<HandoffRecord["transportMode"], string> = {
  owner_vehicle:    "Owner Vehicle",
  ambulance:        "Ambulance",
  clinic_transport: "Clinic Transport",
};

function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString("en-GB", {
    day: "numeric", month: "short", hour: "2-digit", minute: "2-digit",
  });
}

export function HandoffStatusPanel({ handoffs }: HandoffStatusPanelProps) {
  if (handoffs.length === 0) {
    return <p className="text-sm text-gray-400 italic">No handoff records.</p>;
  }

  return (
    <div className="space-y-3">
      {handoffs.map((h) => (
        <div
          key={h.id}
          className={`rounded-lg border px-4 py-3 space-y-2 ${STATUS_STYLES[h.status]}`}
        >
          <div className="flex items-start justify-between gap-2 flex-wrap">
            <div>
              <p className="text-sm font-semibold">{h.petName}</p>
              <p className="text-xs opacity-70">
                {h.fromClinic} → {h.toClinic}
              </p>
            </div>
            <span className="text-xs font-semibold">{STATUS_LABEL[h.status]}</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-1 text-xs opacity-80">
            <span>Mode: {MODE_LABEL[h.transportMode]}</span>
            <span>From: {h.handoffVet}</span>
            {h.receivingVet && <span>To: {h.receivingVet}</span>}
            <span>Initiated: {formatDateTime(h.initiatedAt)}</span>
            {h.receivedAt && <span>Received: {formatDateTime(h.receivedAt)}</span>}
          </div>

          {h.notes && (
            <p className="text-xs italic opacity-70 border-t border-current/10 pt-2">
              {h.notes}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}
