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
  current: "Current",
  due_soon: "Due Soon",
  overdue: "Overdue",
};

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-GB", {
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
        <p>Administered: {formatDate(vaccination.administeredDate)}</p>
        <p>Next due: {formatDate(vaccination.nextDueDate)}</p>
        {vaccination.vetName && <p>Vet: {vaccination.vetName}</p>}
        {vaccination.batchNumber && (
          <p>Batch: {vaccination.batchNumber}</p>
        )}
      </div>
    </div>
  );
}
