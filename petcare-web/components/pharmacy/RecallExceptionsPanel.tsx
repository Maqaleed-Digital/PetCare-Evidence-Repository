import type { RecallException, RecallSeverity, RecallStatus } from "@/types/pharmacy";

interface RecallExceptionsPanelProps {
  recalls: RecallException[];
}

type Severity = RecallSeverity;
type Status = RecallStatus;

const SEV_STYLES: Record<Severity, string> = {
  class_i:   "border-red-300 bg-red-50",
  class_ii:  "border-orange-300 bg-orange-50",
  class_iii: "border-yellow-200 bg-yellow-50",
};

const SEV_BADGE: Record<Severity, string> = {
  class_i:   "bg-red-200 text-red-800",
  class_ii:  "bg-orange-200 text-orange-800",
  class_iii: "bg-yellow-200 text-yellow-800",
};

const SEV_LABEL: Record<Severity, string> = {
  class_i:   "Class I — Critical",
  class_ii:  "Class II — Significant",
  class_iii: "Class III — Minor",
};

const STATUS_STYLES: Record<Status, string> = {
  active:       "text-red-700",
  resolved:     "text-green-700",
  under_review: "text-orange-700",
};

const STATUS_LABEL: Record<Status, string> = {
  active:       "Active",
  resolved:     "Resolved",
  under_review: "Under Review",
};

export function RecallExceptionsPanel({ recalls }: RecallExceptionsPanelProps) {
  if (recalls.length === 0) {
    return <p className="text-sm text-gray-400 italic">No recall exceptions.</p>;
  }

  const priority: Severity[] = ["class_i", "class_ii", "class_iii"];
  const sorted = [...recalls].sort(
    (a, b) => priority.indexOf(a.severity) - priority.indexOf(b.severity)
  );

  return (
    <div className="space-y-3">
      {sorted.map((recall) => (
        <div
          key={recall.id}
          className={`rounded-lg border px-4 py-3 space-y-2 ${SEV_STYLES[recall.severity]}`}
        >
          <div className="flex items-start justify-between gap-2 flex-wrap">
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <span
                  className={`rounded px-1.5 py-0.5 text-xs font-bold ${SEV_BADGE[recall.severity]}`}
                >
                  {SEV_LABEL[recall.severity]}
                </span>
                <p className="text-sm font-semibold text-gray-900">
                  {recall.medicationName}
                </p>
              </div>
              <p className="text-xs text-gray-600 mt-0.5">{recall.manufacturer}</p>
            </div>
            <span
              className={`text-xs font-semibold ${STATUS_STYLES[recall.status]}`}
            >
              {STATUS_LABEL[recall.status]}
            </span>
          </div>

          <p className="text-xs text-gray-700">{recall.reason}</p>

          <div className="flex flex-wrap gap-1">
            {recall.batchNumbers.map((b) => (
              <span
                key={b}
                className="rounded bg-white/60 border border-gray-300 px-1.5 py-0.5 text-xs font-mono"
              >
                {b}
              </span>
            ))}
          </div>

          <div className="flex gap-4 text-xs text-gray-500">
            <span>Recalled: {recall.recallDate}</span>
            <span>
              {recall.unitsQuarantined} / {recall.unitsAffected} units quarantined
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
