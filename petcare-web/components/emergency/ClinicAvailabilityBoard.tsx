import type { ClinicAvailability, ClinicStatus } from "@/types/emergency";

interface ClinicAvailabilityBoardProps {
  clinics: ClinicAvailability[];
}

type Status = ClinicStatus;

const STATUS_STYLES: Record<Status, string> = {
  open_emergency: "border-green-200 bg-green-50",
  limited:        "border-yellow-200 bg-yellow-50",
  closed:         "border-gray-200 bg-gray-100",
  on_call_only:   "border-blue-200 bg-blue-50",
};

const STATUS_DOT: Record<Status, string> = {
  open_emergency: "bg-green-500",
  limited:        "bg-yellow-500",
  closed:         "bg-gray-400",
  on_call_only:   "bg-blue-500",
};

const STATUS_LABEL: Record<Status, string> = {
  open_emergency: "Open — Emergency",
  limited:        "Limited Capacity",
  closed:         "Closed",
  on_call_only:   "On-Call Only",
};

export function ClinicAvailabilityBoard({ clinics }: ClinicAvailabilityBoardProps) {
  if (clinics.length === 0) {
    return <p className="text-sm text-gray-400 italic">No clinic data available.</p>;
  }

  const sorted = [...clinics].sort((a, b) => a.distanceKm - b.distanceKm);

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
      {sorted.map((clinic) => {
        const bedPct = Math.round(
          (clinic.emergencyBedsAvailable / (clinic.emergencyBedsTotal || 1)) * 100
        );
        return (
          <div
            key={clinic.id}
            className={`rounded-lg border p-4 space-y-3 ${STATUS_STYLES[clinic.status]}`}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-center gap-2">
                <span className={`h-2.5 w-2.5 rounded-full shrink-0 ${STATUS_DOT[clinic.status]}`} />
                <div>
                  <p className="text-sm font-semibold text-gray-900">{clinic.clinicName}</p>
                  <p className="text-xs text-gray-500">{clinic.distanceKm} km away</p>
                </div>
              </div>
              <span className={`text-xs font-medium ${clinic.acceptingCases ? "text-green-700" : "text-red-600"}`}>
                {clinic.acceptingCases ? "Accepting" : "Not Accepting"}
              </span>
            </div>

            <div>
              <div className="flex justify-between text-xs text-gray-500 mb-1">
                <span>Emergency Beds</span>
                <span>{clinic.emergencyBedsAvailable} / {clinic.emergencyBedsTotal}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-1.5">
                <div
                  className={`h-1.5 rounded-full ${bedPct > 50 ? "bg-green-500" : bedPct > 0 ? "bg-yellow-400" : "bg-red-400"}`}
                  style={{ width: `${bedPct}%` }}
                />
              </div>
            </div>

            <div className="text-xs text-gray-600 space-y-0.5">
              <p>{STATUS_LABEL[clinic.status]}</p>
              {clinic.onCallVet && <p>On-call: {clinic.onCallVet}</p>}
              <p>📞 {clinic.phoneNumber}</p>
              {clinic.specialisms.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-1">
                  {clinic.specialisms.map((s) => (
                    <span key={s} className="rounded bg-white/60 border border-gray-200 px-1.5 py-0.5 text-xs">
                      {s}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
