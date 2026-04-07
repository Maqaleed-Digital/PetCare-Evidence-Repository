import type { Vaccination } from "@/types/owner";
import { VaccinationCard } from "./VaccinationCard";

interface VaccinationSummaryProps {
  vaccinations: Vaccination[];
}

export function VaccinationSummary({ vaccinations }: VaccinationSummaryProps) {
  if (vaccinations.length === 0) {
    return (
      <p className="text-sm text-gray-400 italic">
        لا توجد سجلات تطعيم.
      </p>
    );
  }

  const overdue = vaccinations.filter((v) => v.status === "overdue");
  const dueSoon = vaccinations.filter((v) => v.status === "due_soon");
  const current = vaccinations.filter((v) => v.status === "current");

  return (
    <div className="space-y-3">
      {overdue.length > 0 && (
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-red-600 mb-2">
            متأخرة ({overdue.length})
          </p>
          <div className="space-y-2">
            {overdue.map((v) => (
              <VaccinationCard key={v.id} vaccination={v} />
            ))}
          </div>
        </div>
      )}

      {dueSoon.length > 0 && (
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-yellow-700 mb-2">
            مستحقة قريباً ({dueSoon.length})
          </p>
          <div className="space-y-2">
            {dueSoon.map((v) => (
              <VaccinationCard key={v.id} vaccination={v} />
            ))}
          </div>
        </div>
      )}

      {current.length > 0 && (
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-green-700 mb-2">
            حالية ({current.length})
          </p>
          <div className="space-y-2">
            {current.map((v) => (
              <VaccinationCard key={v.id} vaccination={v} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
