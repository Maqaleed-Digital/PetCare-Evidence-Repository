import type { AppointmentSlot } from "@/types/admin";

interface AppointmentLoadBoardProps {
  slots: AppointmentSlot[];
}

type SlotStatus = AppointmentSlot["status"];

const STATUS_STYLES: Record<SlotStatus, string> = {
  scheduled: "bg-blue-50 text-blue-700 border-blue-200",
  in_progress: "bg-indigo-50 text-indigo-700 border-indigo-200",
  completed: "bg-green-50 text-green-700 border-green-200",
  no_show: "bg-red-50 text-red-700 border-red-200",
  cancelled: "bg-gray-100 text-gray-500 border-gray-200",
};

const STATUS_LABEL: Record<SlotStatus, string> = {
  scheduled: "Scheduled",
  in_progress: "In Progress",
  completed: "Completed",
  no_show: "No Show",
  cancelled: "Cancelled",
};

export function AppointmentLoadBoard({ slots }: AppointmentLoadBoardProps) {
  if (slots.length === 0) {
    return (
      <p className="text-sm text-gray-400 italic">No appointments today.</p>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="border-b border-gray-200 text-xs uppercase tracking-wider text-gray-500">
            <th className="py-2 pr-4 text-left font-medium">Time</th>
            <th className="py-2 pr-4 text-left font-medium">Patient</th>
            <th className="py-2 pr-4 text-left font-medium">Pet</th>
            <th className="py-2 pr-4 text-left font-medium">Vet</th>
            <th className="py-2 pr-4 text-left font-medium">Reason</th>
            <th className="py-2 text-left font-medium">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {slots.map((slot) => (
            <tr key={slot.id} className="hover:bg-gray-50">
              <td className="py-2 pr-4 font-mono text-xs text-gray-700">
                {slot.time}
              </td>
              <td className="py-2 pr-4 text-gray-900">{slot.patientName}</td>
              <td className="py-2 pr-4 text-gray-600">{slot.petName}</td>
              <td className="py-2 pr-4 text-gray-600">{slot.vetName}</td>
              <td className="py-2 pr-4 text-gray-600 max-w-[160px] truncate">
                {slot.reason}
              </td>
              <td className="py-2">
                <span
                  className={`rounded border px-1.5 py-0.5 text-xs font-medium whitespace-nowrap ${
                    STATUS_STYLES[slot.status]
                  }`}
                >
                  {STATUS_LABEL[slot.status]}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
