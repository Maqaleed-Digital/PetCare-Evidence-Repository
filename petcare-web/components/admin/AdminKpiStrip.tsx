import type { AdminKpi } from "@/types/admin";

interface AdminKpiStripProps {
  kpis: AdminKpi[];
}

const VARIANT_STYLES: Record<AdminKpi["variant"], string> = {
  default: "bg-white border-gray-200 text-gray-900",
  success: "bg-green-50 border-green-200 text-green-800",
  warning: "bg-yellow-50 border-yellow-200 text-yellow-800",
  danger: "bg-red-50 border-red-200 text-red-800",
};

const TREND_ICON: Record<NonNullable<AdminKpi["trend"]>, string> = {
  up: "↑",
  down: "↓",
  stable: "→",
};

export function AdminKpiStrip({ kpis }: AdminKpiStripProps) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
      {kpis.map((kpi) => (
        <div
          key={kpi.label}
          className={`rounded-lg border p-4 space-y-1 ${VARIANT_STYLES[kpi.variant]}`}
        >
          <p className="text-xs font-medium uppercase tracking-wider opacity-60">
            {kpi.label}
          </p>
          <p className="text-2xl font-bold leading-none">
            {kpi.value}
            {kpi.unit && (
              <span className="text-sm font-normal ml-1 opacity-70">
                {kpi.unit}
              </span>
            )}
          </p>
          {kpi.trend && kpi.trendLabel && (
            <p className="text-xs opacity-60">
              {TREND_ICON[kpi.trend]} {kpi.trendLabel}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}
