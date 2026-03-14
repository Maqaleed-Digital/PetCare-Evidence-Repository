import type { InventoryItem, InventoryStatus } from "@/types/pharmacy";

interface InventoryStatusSummaryProps {
  items: InventoryItem[];
}

type Status = InventoryStatus;

const STATUS_STYLES: Record<Status, string> = {
  in_stock:       "bg-green-50 text-green-700 border-green-200",
  low_stock:      "bg-yellow-50 text-yellow-700 border-yellow-200",
  out_of_stock:   "bg-red-50 text-red-700 border-red-200",
  expiring_soon:  "bg-orange-50 text-orange-700 border-orange-200",
  expired:        "bg-gray-100 text-gray-500 border-gray-300",
};

const STATUS_LABEL: Record<Status, string> = {
  in_stock:      "In Stock",
  low_stock:     "Low Stock",
  out_of_stock:  "Out of Stock",
  expiring_soon: "Expiring Soon",
  expired:       "Expired",
};

const STORAGE_ICON: Record<InventoryItem["storageRequirement"], string> = {
  ambient:      "🌡",
  refrigerated: "❄️",
  frozen:       "🧊",
};

export function InventoryStatusSummary({ items }: InventoryStatusSummaryProps) {
  if (items.length === 0) {
    return <p className="text-sm text-gray-400 italic">No inventory data.</p>;
  }

  const priority: Status[] = ["out_of_stock", "expired", "expiring_soon", "low_stock", "in_stock"];
  const sorted = [...items].sort(
    (a, b) => priority.indexOf(a.status) - priority.indexOf(b.status)
  );

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200">
      <table className="w-full text-sm border-collapse">
        <thead className="bg-gray-50">
          <tr className="border-b border-gray-200 text-xs uppercase tracking-wider text-gray-500">
            <th className="py-2 px-3 text-left font-medium">Medication</th>
            <th className="py-2 px-3 text-left font-medium">Batch</th>
            <th className="py-2 px-3 text-left font-medium">QOH</th>
            <th className="py-2 px-3 text-left font-medium">Reorder</th>
            <th className="py-2 px-3 text-left font-medium">Expiry</th>
            <th className="py-2 px-3 text-left font-medium">Storage</th>
            <th className="py-2 px-3 text-left font-medium">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100 bg-white">
          {sorted.map((item) => (
            <tr key={item.id} className="hover:bg-gray-50">
              <td className="py-2 px-3">
                <p className="font-medium text-gray-900">{item.medicationName}</p>
                <p className="text-xs text-gray-500">{item.strength} · {item.form}</p>
              </td>
              <td className="py-2 px-3 font-mono text-xs text-gray-500">
                {item.batchNumber}
              </td>
              <td className="py-2 px-3 text-gray-700">
                {item.quantityOnHand} {item.quantityUnit}
              </td>
              <td className="py-2 px-3 text-gray-500 text-xs">
                {item.reorderLevel} {item.quantityUnit}
              </td>
              <td className="py-2 px-3 text-xs text-gray-500">{item.expiryDate}</td>
              <td className="py-2 px-3 text-base" title={item.storageRequirement}>
                {STORAGE_ICON[item.storageRequirement]}
              </td>
              <td className="py-2 px-3">
                <span
                  className={`rounded border px-1.5 py-0.5 text-xs font-medium ${STATUS_STYLES[item.status]}`}
                >
                  {STATUS_LABEL[item.status]}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
