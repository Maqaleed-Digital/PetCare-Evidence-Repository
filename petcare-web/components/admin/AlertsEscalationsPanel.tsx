import type { Alert, AlertSeverity } from "@/types/admin";

interface AlertsEscalationsPanelProps {
  alerts: Alert[];
}

const SEV_STYLES: Record<AlertSeverity, string> = {
  info: "border-blue-200 bg-blue-50 text-blue-800",
  warning: "border-yellow-200 bg-yellow-50 text-yellow-800",
  critical: "border-red-200 bg-red-50 text-red-800",
};

const SEV_BADGE: Record<AlertSeverity, string> = {
  info: "bg-blue-100 text-blue-700",
  warning: "bg-yellow-100 text-yellow-700",
  critical: "bg-red-100 text-red-700",
};

const SEV_LABEL: Record<AlertSeverity, string> = {
  info: "Info",
  warning: "Warning",
  critical: "Critical",
};

function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString("en-GB", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function AlertsEscalationsPanel({ alerts }: AlertsEscalationsPanelProps) {
  if (alerts.length === 0) {
    return (
      <p className="text-sm text-gray-400 italic">No active alerts.</p>
    );
  }

  const sorted = [...alerts].sort((a, b) => {
    const order: AlertSeverity[] = ["critical", "warning", "info"];
    return order.indexOf(a.severity) - order.indexOf(b.severity);
  });

  return (
    <div className="space-y-2">
      {sorted.map((alert) => (
        <div
          key={alert.id}
          className={`rounded-lg border px-4 py-3 space-y-1 ${SEV_STYLES[alert.severity]} ${
            alert.acknowledged ? "opacity-50" : ""
          }`}
        >
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <span
                className={`rounded px-1.5 py-0.5 text-xs font-semibold ${SEV_BADGE[alert.severity]}`}
              >
                {SEV_LABEL[alert.severity]}
              </span>
              <p className="text-sm font-medium">{alert.title}</p>
            </div>
            {alert.acknowledged && (
              <span className="text-xs opacity-60">Acknowledged</span>
            )}
          </div>
          <p className="text-xs opacity-80">{alert.description}</p>
          <p className="text-xs opacity-60">{formatDateTime(alert.raisedAt)}</p>
        </div>
      ))}
    </div>
  );
}
