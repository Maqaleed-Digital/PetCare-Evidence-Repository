import type { FulfillmentDispatch, DispatchStatus } from "@/types/pharmacy";

interface FulfillmentDispatchSummaryProps {
  dispatches: FulfillmentDispatch[];
}

type Status = DispatchStatus;

const STATUS_STYLES: Record<Status, string> = {
  awaiting_collection: "bg-blue-50 text-blue-700 border-blue-200",
  out_for_delivery:    "bg-indigo-50 text-indigo-700 border-indigo-200",
  delivered:           "bg-green-50 text-green-700 border-green-200",
  returned:            "bg-orange-50 text-orange-700 border-orange-200",
  failed:              "bg-red-50 text-red-700 border-red-200",
};

const STATUS_LABEL: Record<Status, string> = {
  awaiting_collection: "Awaiting Collection",
  out_for_delivery:    "Out for Delivery",
  delivered:           "Delivered",
  returned:            "Returned",
  failed:              "Failed",
};

const METHOD_LABEL: Record<FulfillmentDispatch["method"], string> = {
  clinic_collection: "Clinic",
  home_delivery:     "Home Delivery",
  courier:           "Courier",
};

function formatDateTime(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("en-GB", {
    day: "numeric", month: "short", hour: "2-digit", minute: "2-digit",
  });
}

export function FulfillmentDispatchSummary({ dispatches }: FulfillmentDispatchSummaryProps) {
  if (dispatches.length === 0) {
    return <p className="text-sm text-gray-400 italic">No dispatch records.</p>;
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200">
      <table className="w-full text-sm border-collapse">
        <thead className="bg-gray-50">
          <tr className="border-b border-gray-200 text-xs uppercase tracking-wider text-gray-500">
            <th className="py-2 px-3 text-left font-medium">Rx Ref</th>
            <th className="py-2 px-3 text-left font-medium">Patient</th>
            <th className="py-2 px-3 text-left font-medium">Method</th>
            <th className="py-2 px-3 text-left font-medium">Dispatched</th>
            <th className="py-2 px-3 text-left font-medium">ETA</th>
            <th className="py-2 px-3 text-left font-medium">Tracking</th>
            <th className="py-2 px-3 text-left font-medium">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100 bg-white">
          {dispatches.map((d) => (
            <tr key={d.id} className="hover:bg-gray-50">
              <td className="py-2 px-3 font-mono text-xs text-gray-500">
                {d.prescriptionId}
              </td>
              <td className="py-2 px-3">
                <p className="text-sm text-gray-900">{d.petName}</p>
                <p className="text-xs text-gray-500">{d.ownerName}</p>
              </td>
              <td className="py-2 px-3 text-xs text-gray-600">
                {METHOD_LABEL[d.method]}
              </td>
              <td className="py-2 px-3 text-xs text-gray-500">
                {formatDateTime(d.dispatchedAt)}
              </td>
              <td className="py-2 px-3 text-xs text-gray-500">
                {formatDateTime(d.estimatedDelivery)}
              </td>
              <td className="py-2 px-3 font-mono text-xs text-gray-400">
                {d.trackingRef ?? "—"}
              </td>
              <td className="py-2 px-3">
                <span
                  className={`rounded border px-1.5 py-0.5 text-xs font-medium whitespace-nowrap ${STATUS_STYLES[d.status]}`}
                >
                  {STATUS_LABEL[d.status]}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
