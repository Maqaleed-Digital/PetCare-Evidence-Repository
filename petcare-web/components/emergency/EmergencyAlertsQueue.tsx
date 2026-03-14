import type { EmergencyAlert, AlertSeverity, AlertStatus } from "@/types/emergency";

interface EmergencyAlertsQueueProps {
  alerts: EmergencyAlert[];
}

const SEV_STYLES: Record<AlertSeverity, string> = {
  p1_critical: "border-l-red-600 bg-red-50 border-red-200",
  p2_urgent:   "border-l-orange-500 bg-orange-50 border-orange-200",
  p3_moderate: "border-l-yellow-400 bg-yellow-50 border-yellow-200",
  p4_minor:    "border-l-blue-400 bg-blue-50 border-blue-200",
};

const SEV_BADGE: Record<AlertSeverity, string> = {
  p1_critical: "bg-red-600 text-white",
  p2_urgent:   "bg-orange-500 text-white",
  p3_moderate: "bg-yellow-400 text-yellow-900",
  p4_minor:    "bg-blue-400 text-white",
};

const SEV_LABEL: Record<AlertSeverity, string> = {
  p1_critical: "P1 CRITICAL",
  p2_urgent:   "P2 URGENT",
  p3_moderate: "P3 MODERATE",
  p4_minor:    "P4 MINOR",
};

const STATUS_LABEL: Record<AlertStatus, string> = {
  open:         "Open",
  acknowledged: "Acknowledged",
  dispatched:   "Dispatched",
  resolved:     "Resolved",
};

const STATUS_STYLES: Record<AlertStatus, string> = {
  open:         "text-red-700 font-bold",
  acknowledged: "text-orange-600",
  dispatched:   "text-blue-600",
  resolved:     "text-green-700",
};

function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString("en-GB", {
    day: "numeric", month: "short", hour: "2-digit", minute: "2-digit",
  });
}

export function EmergencyAlertsQueue({ alerts }: EmergencyAlertsQueueProps) {
  if (alerts.length === 0) {
    return <p className="text-sm text-gray-400 italic">No active emergency alerts.</p>;
  }

  const sevOrder: AlertSeverity[] = ["p1_critical", "p2_urgent", "p3_moderate", "p4_minor"];
  const sorted = [...alerts].sort(
    (a, b) => sevOrder.indexOf(a.severity) - sevOrder.indexOf(b.severity)
  );

  return (
    <div className="space-y-3">
      {sorted.map((alert) => (
        <div
          key={alert.id}
          className={`rounded-lg border border-l-4 px-4 py-3 space-y-2 ${SEV_STYLES[alert.severity]}`}
        >
          <div className="flex items-start justify-between gap-2 flex-wrap">
            <div className="flex items-center gap-2 flex-wrap">
              <span className={`rounded px-2 py-0.5 text-xs font-bold ${SEV_BADGE[alert.severity]}`}>
                {SEV_LABEL[alert.severity]}
              </span>
              <p className="text-sm font-semibold text-gray-900">
                {alert.petName}
                <span className="text-gray-500 font-normal"> ({alert.species})</span>
              </p>
            </div>
            <span className={`text-xs ${STATUS_STYLES[alert.status]}`}>
              {STATUS_LABEL[alert.status]}
            </span>
          </div>

          <p className="text-sm text-gray-800">{alert.chiefComplaint}</p>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-1 text-xs text-gray-600">
            <span>Owner: {alert.ownerName}</span>
            <span>📞 {alert.ownerPhone}</span>
            {alert.location && <span>📍 {alert.location}</span>}
            {alert.assignedVet && <span>Vet: {alert.assignedVet}</span>}
            <span>Raised: {formatDateTime(alert.raisedAt)}</span>
            {alert.acknowledgedAt && (
              <span>Ack: {formatDateTime(alert.acknowledgedAt)}</span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
