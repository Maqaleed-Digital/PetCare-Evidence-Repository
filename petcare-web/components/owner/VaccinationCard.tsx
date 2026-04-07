import type { Vaccination, VaccinationStatus } from "@/types/owner";

interface VaccinationCardProps {
  vaccination: Vaccination;
}

const STATUS_STYLES: Record<VaccinationStatus, string> = {
  current: "bg-green-50 border-green-200 text-green-700",
  due_soon: "bg-yellow-50 border-yellow-200 text-yellow-700",
  overdue: "bg-red-50 border-red-200 text-red-600",
};

const STATUS_LABEL: Record<VaccinationStatus, string> = {
  current: "حالية",
  due_soon: "مستحقة قريباً",
  overdue: "متأخرة",
};

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("ar-SA", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export function VaccinationCard({ vaccination }: VaccinationCardProps) {
  const style = STATUS_STYLES[vaccination.status];
  const label = STATUS_LABEL[vaccination.status];

  return (
    <div className={`rounded-lg border p-3 space-y-1 ${style}`}>
      <div className="flex items-center justify-between gap-2">
        <p className="text-sm font-semibold">{vaccination.name}</p>
        <span className="text-xs font-medium">{label}</span>
      </div>
      <div className="text-xs space-y-0.5 opacity-80">
        <p>تاريخ التطبيق: {formatDate(vaccination.administeredDate)}</p>
        <p>الاستحقاق القادم: {formatDate(vaccination.nextDueDate)}</p>
        {vaccination.vetName && <p>الطبيب البيطري: {vaccination.vetName}</p>}
        {vaccination.batchNumber && (
          <p>رقم الدفعة: {vaccination.batchNumber}</p>
        )}
      </div>
    </div>
  );
}
