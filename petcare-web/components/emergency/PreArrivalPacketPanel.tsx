import type { PreArrivalPacket } from "@/types/emergency";

interface PreArrivalPacketPanelProps {
  packet: PreArrivalPacket;
}

const VAX_STYLES: Record<PreArrivalPacket["vaccinationStatus"], string> = {
  current:  "text-green-700 bg-green-50 border-green-200",
  partial:  "text-yellow-700 bg-yellow-50 border-yellow-200",
  overdue:  "text-red-700 bg-red-50 border-red-200",
  unknown:  "text-gray-600 bg-gray-50 border-gray-200",
};

const VAX_LABEL: Record<PreArrivalPacket["vaccinationStatus"], string> = {
  current:  "Vaccinations Current",
  partial:  "Partial Vaccinations",
  overdue:  "Vaccinations Overdue",
  unknown:  "Vaccination Status Unknown",
};

function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString("en-GB", {
    day: "numeric", month: "short", hour: "2-digit", minute: "2-digit",
  });
}

export function PreArrivalPacketPanel({ packet }: PreArrivalPacketPanelProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white overflow-hidden space-y-0">
      {/* Header */}
      <div className="bg-red-50 border-b border-red-200 px-5 py-3 flex items-center justify-between">
        <div>
          <p className="text-sm font-bold text-red-800">
            Pre-Arrival Packet — {packet.petName}
          </p>
          <p className="text-xs text-red-600 mt-0.5">
            Case {packet.caseId} · Shared {formatDateTime(packet.sharedAt)}
          </p>
        </div>
        <span
          className={`rounded border px-2 py-0.5 text-xs font-medium ${VAX_STYLES[packet.vaccinationStatus]}`}
        >
          {VAX_LABEL[packet.vaccinationStatus]}
        </span>
      </div>

      <div className="p-5 grid grid-cols-1 sm:grid-cols-2 gap-6">
        {/* Patient */}
        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-wider text-gray-500">
            Patient
          </p>
          <dl className="text-sm space-y-1">
            {[
              ["Species", packet.species],
              ["Breed", packet.breed],
              ["Age", `${packet.ageYears} yr`],
              ["Weight", `${packet.weightKg} kg`],
              ["Microchip", packet.microchipId ?? "Not registered"],
            ].map(([label, value]) => (
              <div key={label} className="flex gap-2">
                <dt className="text-gray-500 w-24 shrink-0">{label}</dt>
                <dd className="text-gray-900 font-medium">{value}</dd>
              </div>
            ))}
          </dl>
        </div>

        {/* Owner */}
        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-wider text-gray-500">
            Owner
          </p>
          <dl className="text-sm space-y-1">
            {[
              ["Name", packet.ownerName],
              ["Phone", packet.ownerPhone],
              ["Consent", packet.consentGiven ? "Given ✓" : "Not Given ✗"],
            ].map(([label, value]) => (
              <div key={label} className="flex gap-2">
                <dt className="text-gray-500 w-24 shrink-0">{label}</dt>
                <dd className={`font-medium ${label === "Consent" && !packet.consentGiven ? "text-red-600" : "text-gray-900"}`}>
                  {value}
                </dd>
              </div>
            ))}
          </dl>
        </div>

        {/* Chief Complaint */}
        <div className="sm:col-span-2 space-y-1">
          <p className="text-xs font-semibold uppercase tracking-wider text-gray-500">
            Chief Complaint
          </p>
          <p className="text-sm text-gray-900 bg-red-50 border border-red-200 rounded px-3 py-2">
            {packet.chiefComplaint}
          </p>
        </div>

        {/* Vitals */}
        {packet.lastVitals.length > 0 && (
          <div className="sm:col-span-2 space-y-2">
            <p className="text-xs font-semibold uppercase tracking-wider text-gray-500">
              Last Vitals
            </p>
            <div className="flex flex-wrap gap-2">
              {packet.lastVitals.map((v) => (
                <div
                  key={v.label}
                  className={`rounded border px-3 py-1.5 text-xs ${
                    v.normal
                      ? "border-green-200 bg-green-50 text-green-800"
                      : "border-red-200 bg-red-50 text-red-800"
                  }`}
                >
                  <span className="font-medium">{v.label}</span>{" "}
                  <span>{v.value}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Medications */}
        {packet.currentMedications.length > 0 && (
          <div className="space-y-1">
            <p className="text-xs font-semibold uppercase tracking-wider text-gray-500">
              Current Medications
            </p>
            <ul className="text-sm text-gray-700 space-y-0.5 list-disc list-inside">
              {packet.currentMedications.map((m) => (
                <li key={m}>{m}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Allergies */}
        {packet.knownAllergies.length > 0 && (
          <div className="space-y-1">
            <p className="text-xs font-semibold uppercase tracking-wider text-red-600">
              Known Allergies
            </p>
            <ul className="text-sm text-red-700 space-y-0.5 list-disc list-inside">
              {packet.knownAllergies.map((a) => (
                <li key={a}>{a}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
