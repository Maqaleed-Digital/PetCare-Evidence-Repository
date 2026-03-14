import type { ClinicOperations, ClinicStatus } from "@/types/admin";

interface ClinicOperationsOverviewProps {
  ops: ClinicOperations;
}

const STATUS_STYLES: Record<ClinicStatus, string> = {
  operational: "bg-green-100 text-green-800 border-green-200",
  degraded: "bg-yellow-100 text-yellow-800 border-yellow-200",
  closed: "bg-gray-100 text-gray-600 border-gray-200",
};

const STATUS_LABEL: Record<ClinicStatus, string> = {
  operational: "Operational",
  degraded: "Degraded",
  closed: "Closed",
};

export function ClinicOperationsOverview({ ops }: ClinicOperationsOverviewProps) {
  const utilizationPct = Math.round((ops.capacityUsed / ops.capacityTotal) * 100);
  const completionPct = Math.round(
    (ops.appointmentsCompleted / (ops.appointmentsToday || 1)) * 100
  );

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-900">{ops.clinicName}</h3>
        <span
          className={`rounded border px-2 py-0.5 text-xs font-medium ${STATUS_STYLES[ops.status]}`}
        >
          {STATUS_LABEL[ops.status]}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <p className="text-xs text-gray-500 mb-1">Capacity</p>
          <div className="w-full bg-gray-100 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full"
              style={{ width: `${utilizationPct}%` }}
            />
          </div>
          <p className="text-xs text-gray-600 mt-1">
            {ops.capacityUsed} / {ops.capacityTotal} ({utilizationPct}%)
          </p>
        </div>

        <div>
          <p className="text-xs text-gray-500 mb-1">Appointments</p>
          <div className="w-full bg-gray-100 rounded-full h-2">
            <div
              className="bg-green-500 h-2 rounded-full"
              style={{ width: `${completionPct}%` }}
            />
          </div>
          <p className="text-xs text-gray-600 mt-1">
            {ops.appointmentsCompleted} / {ops.appointmentsToday} done ({completionPct}%)
          </p>
        </div>
      </div>

      <div className="flex gap-4 text-xs text-gray-500">
        <span>Open: {ops.openSince}</span>
        <span>Closes: {ops.closesAt}</span>
      </div>
    </div>
  );
}
