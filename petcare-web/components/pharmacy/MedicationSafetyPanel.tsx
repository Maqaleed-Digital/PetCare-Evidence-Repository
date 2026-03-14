import type { MedicationSafetyAlert, SafetyAlertLevel } from "@/types/pharmacy";

interface MedicationSafetyPanelProps {
  alerts: MedicationSafetyAlert[];
}

type Level = SafetyAlertLevel;

const LEVEL_STYLES: Record<Level, string> = {
  contraindication: "border-red-300 bg-red-50 text-red-900",
  interaction:      "border-orange-300 bg-orange-50 text-orange-900",
  caution:          "border-yellow-300 bg-yellow-50 text-yellow-900",
};

const LEVEL_BADGE: Record<Level, string> = {
  contraindication: "bg-red-200 text-red-800",
  interaction:      "bg-orange-200 text-orange-800",
  caution:          "bg-yellow-200 text-yellow-800",
};

const LEVEL_LABEL: Record<Level, string> = {
  contraindication: "Contraindication",
  interaction:      "Drug Interaction",
  caution:          "Caution",
};

function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString("en-GB", {
    day: "numeric", month: "short", hour: "2-digit", minute: "2-digit",
  });
}

export function MedicationSafetyPanel({ alerts }: MedicationSafetyPanelProps) {
  if (alerts.length === 0) {
    return (
      <p className="text-sm text-gray-400 italic">No medication safety alerts.</p>
    );
  }

  const priority: Level[] = ["contraindication", "interaction", "caution"];
  const sorted = [...alerts].sort(
    (a, b) => priority.indexOf(a.alertLevel) - priority.indexOf(b.alertLevel)
  );

  return (
    <div className="space-y-2">
      {sorted.map((alert) => (
        <div
          key={alert.id}
          className={`rounded-lg border px-4 py-3 space-y-2 ${LEVEL_STYLES[alert.alertLevel]} ${
            alert.acknowledged ? "opacity-50" : ""
          }`}
        >
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-2 flex-wrap">
              <span
                className={`rounded px-1.5 py-0.5 text-xs font-bold ${LEVEL_BADGE[alert.alertLevel]}`}
              >
                {LEVEL_LABEL[alert.alertLevel]}
              </span>
              <p className="text-sm font-semibold">{alert.title}</p>
            </div>
            {alert.acknowledged && (
              <span className="text-xs opacity-60 shrink-0">Acknowledged</span>
            )}
          </div>
          <p className="text-xs opacity-80">{alert.detail}</p>
          <div className="flex flex-wrap gap-1">
            {alert.medications.map((med) => (
              <span
                key={med}
                className="rounded bg-white/60 border border-current/20 px-1.5 py-0.5 text-xs font-medium"
              >
                {med}
              </span>
            ))}
          </div>
          <p className="text-xs opacity-50">
            Rx: {alert.prescriptionId} · {formatDateTime(alert.raisedAt)}
          </p>
        </div>
      ))}
    </div>
  );
}
