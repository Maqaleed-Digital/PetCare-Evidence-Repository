import type { VetAvailability, VetStatus } from "@/types/admin";

interface VetAvailabilityPanelProps {
  vets: VetAvailability[];
}

const STATUS_STYLES: Record<VetStatus, string> = {
  available: "bg-green-100 text-green-800",
  in_consultation: "bg-blue-100 text-blue-800",
  break: "bg-yellow-100 text-yellow-800",
  off_duty: "bg-gray-100 text-gray-500",
};

const STATUS_LABEL: Record<VetStatus, string> = {
  available: "Available",
  in_consultation: "In Consultation",
  break: "On Break",
  off_duty: "Off Duty",
};

const STATUS_DOT: Record<VetStatus, string> = {
  available: "bg-green-500",
  in_consultation: "bg-blue-500",
  break: "bg-yellow-500",
  off_duty: "bg-gray-400",
};

export function VetAvailabilityPanel({ vets }: VetAvailabilityPanelProps) {
  if (vets.length === 0) {
    return <p className="text-sm text-gray-400 italic">No vets on roster.</p>;
  }

  return (
    <div className="space-y-2">
      {vets.map((vet) => (
        <div
          key={vet.id}
          className="flex items-center justify-between gap-3 rounded-lg border border-gray-200 bg-white px-4 py-3"
        >
          <div className="flex items-center gap-3">
            <span
              className={`h-2.5 w-2.5 rounded-full shrink-0 ${STATUS_DOT[vet.status]}`}
            />
            <div>
              <p className="text-sm font-medium text-gray-900">{vet.name}</p>
              <p className="text-xs text-gray-500">{vet.specialisation}</p>
            </div>
          </div>

          <div className="flex items-center gap-4 text-xs text-gray-500 shrink-0">
            {vet.currentPatient && (
              <span className="hidden sm:block italic">
                → {vet.currentPatient}
              </span>
            )}
            {vet.appointmentsRemaining > 0 && (
              <span>{vet.appointmentsRemaining} remaining</span>
            )}
            {vet.shiftsEndsAt && <span>Ends {vet.shiftsEndsAt}</span>}
            <span
              className={`rounded px-2 py-0.5 text-xs font-medium ${STATUS_STYLES[vet.status]}`}
            >
              {STATUS_LABEL[vet.status]}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
