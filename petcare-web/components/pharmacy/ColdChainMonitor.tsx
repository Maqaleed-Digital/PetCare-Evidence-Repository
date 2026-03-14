import type { ColdChainReading, ColdChainStatus } from "@/types/pharmacy";

interface ColdChainMonitorProps {
  readings: ColdChainReading[];
}

type Status = ColdChainStatus;

const STATUS_STYLES: Record<Status, string> = {
  normal:  "border-green-200 bg-green-50",
  warning: "border-yellow-200 bg-yellow-50",
  breach:  "border-red-300 bg-red-50",
};

const STATUS_DOT: Record<Status, string> = {
  normal:  "bg-green-500",
  warning: "bg-yellow-500",
  breach:  "bg-red-500",
};

const STATUS_LABEL: Record<Status, string> = {
  normal:  "Normal",
  warning: "Warning",
  breach:  "Breach",
};

function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString("en-GB", {
    day: "numeric", month: "short", hour: "2-digit", minute: "2-digit",
  });
}

function tempBar(temp: number, min: number, max: number): { pct: number; color: string } {
  const range = max - min;
  const clamped = Math.min(Math.max(temp, min - range * 0.5), max + range * 0.5);
  const pct = ((clamped - (min - range * 0.5)) / (range * 2)) * 100;
  if (temp < min || temp > max) return { pct, color: "bg-red-500" };
  if (temp > max - 0.5 || temp < min + 0.5) return { pct, color: "bg-yellow-400" };
  return { pct, color: "bg-green-500" };
}

export function ColdChainMonitor({ readings }: ColdChainMonitorProps) {
  if (readings.length === 0) {
    return <p className="text-sm text-gray-400 italic">No cold chain sensors configured.</p>;
  }

  const priority: Status[] = ["breach", "warning", "normal"];
  const sorted = [...readings].sort(
    (a, b) => priority.indexOf(a.status) - priority.indexOf(b.status)
  );

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
      {sorted.map((r) => {
        const bar = tempBar(r.temperatureCelsius, r.targetMin, r.targetMax);
        return (
          <div
            key={r.id}
            className={`rounded-lg border p-4 space-y-3 ${STATUS_STYLES[r.status]}`}
          >
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <span className={`h-2.5 w-2.5 rounded-full ${STATUS_DOT[r.status]}`} />
                <p className="text-sm font-semibold text-gray-900">{r.location}</p>
              </div>
              <span className="text-xs font-medium text-gray-500">
                {STATUS_LABEL[r.status]}
              </span>
            </div>

            <div>
              <div className="flex items-end justify-between text-xs text-gray-500 mb-1">
                <span>{r.targetMin}°C</span>
                <span className="text-base font-bold text-gray-900">
                  {r.temperatureCelsius.toFixed(1)}°C
                </span>
                <span>{r.targetMax}°C</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${bar.color}`}
                  style={{ width: `${bar.pct}%` }}
                />
              </div>
            </div>

            <div className="flex justify-between text-xs text-gray-500">
              <span>Sensor: {r.sensorId}</span>
              <span>{formatDateTime(r.recordedAt)}</span>
            </div>

            {r.alertSent && (
              <p className="text-xs text-red-600 font-medium">Alert sent</p>
            )}
          </div>
        );
      })}
    </div>
  );
}
