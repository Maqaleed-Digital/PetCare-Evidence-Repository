import type { GovernanceEntry } from "@/types/emergency";

interface EmergencyGovernanceSummaryProps {
  entries: GovernanceEntry[];
}

export function EmergencyGovernanceSummary({ entries }: EmergencyGovernanceSummaryProps) {
  if (entries.length === 0) {
    return <p className="text-sm text-gray-400 italic">No governance data.</p>;
  }

  const compliant = entries.filter((e) => e.compliant).length;
  const total = entries.length;
  const allGreen = compliant === total;

  return (
    <div className="space-y-3">
      <div
        className={`rounded-lg border px-4 py-2 flex items-center justify-between text-sm font-medium ${
          allGreen
            ? "border-green-200 bg-green-50 text-green-800"
            : "border-yellow-200 bg-yellow-50 text-yellow-800"
        }`}
      >
        <span>
          {allGreen ? "All governance checks passing" : "Some checks require attention"}
        </span>
        <span>
          {compliant} / {total} compliant
        </span>
      </div>

      <div className="overflow-x-auto rounded-lg border border-gray-200">
        <table className="w-full text-sm border-collapse">
          <thead className="bg-gray-50">
            <tr className="border-b border-gray-200 text-xs uppercase tracking-wider text-gray-500">
              <th className="py-2 px-3 text-left font-medium">Category</th>
              <th className="py-2 px-3 text-left font-medium">Check</th>
              <th className="py-2 px-3 text-left font-medium">Value</th>
              <th className="py-2 px-3 text-left font-medium">Status</th>
              <th className="py-2 px-3 text-left font-medium">Detail</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 bg-white">
            {entries.map((entry) => (
              <tr key={entry.id} className="hover:bg-gray-50">
                <td className="py-2 px-3 text-xs text-gray-500 capitalize">
                  {entry.category.replace(/_/g, " ")}
                </td>
                <td className="py-2 px-3 text-sm text-gray-900">{entry.label}</td>
                <td className="py-2 px-3 font-mono text-xs text-gray-700">{entry.value}</td>
                <td className="py-2 px-3">
                  {entry.compliant ? (
                    <span className="text-green-700 font-semibold text-xs">✓ Pass</span>
                  ) : (
                    <span className="text-red-600 font-semibold text-xs">✗ Fail</span>
                  )}
                </td>
                <td className="py-2 px-3 text-xs text-gray-500">
                  {entry.detail ?? "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
