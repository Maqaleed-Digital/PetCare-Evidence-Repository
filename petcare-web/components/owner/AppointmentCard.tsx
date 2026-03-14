import type { Appointment, AppointmentStatus } from "@/types/owner";

interface AppointmentCardProps {
  appointment: Appointment;
}

const STATUS_STYLES: Record<AppointmentStatus, string> = {
  scheduled: "bg-blue-50 text-blue-700 border-blue-200",
  completed: "bg-green-50 text-green-700 border-green-200",
  cancelled: "bg-gray-100 text-gray-500 border-gray-200",
  pending: "bg-yellow-50 text-yellow-700 border-yellow-200",
};

const STATUS_LABEL: Record<AppointmentStatus, string> = {
  scheduled: "Scheduled",
  completed: "Completed",
  cancelled: "Cancelled",
  pending: "Pending",
};

function formatDateTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function AppointmentCard({ appointment }: AppointmentCardProps) {
  const statusStyle = STATUS_STYLES[appointment.status];
  const statusLabel = STATUS_LABEL[appointment.status];

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 space-y-2">
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-sm font-semibold text-gray-900">
            {appointment.reason}
          </p>
          <p className="text-xs text-gray-500 mt-0.5">
            {appointment.vetName} · {appointment.clinicName}
          </p>
        </div>
        <span
          className={`shrink-0 rounded border px-2 py-0.5 text-xs font-medium ${statusStyle}`}
        >
          {statusLabel}
        </span>
      </div>
      <p className="text-xs text-gray-600">{formatDateTime(appointment.dateTime)}</p>
      {appointment.notes && (
        <p className="text-xs text-gray-500 italic border-t border-gray-100 pt-2">
          {appointment.notes}
        </p>
      )}
    </div>
  );
}
