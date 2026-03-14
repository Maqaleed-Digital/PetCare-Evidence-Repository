import type { TriageCase, TriagePriority, TriageStatus } from "@/types/emergency";

interface TriageEscalationSummaryProps {
  cases: TriageCase[];
}

const PRIORITY_STYLES: Record<TriagePriority, { row: string; badge: string }> = {
  P1: { row: "bg-red-50",     badge: "bg-red-600 text-white"       },
  P2: { row: "bg-orange-50",  badge: "bg-orange-500 text-white"    },
  P3: { row: "bg-yellow-50",  badge: "bg-yellow-400 text-yellow-900" },
  P4: { row: "bg-blue-50",    badge: "bg-blue-400 text-white"      },
};

const STATUS_STYLES: Record<TriageStatus, string> = {
  waiting:       "text-red-600 font-semibold",
  in_assessment: "text-orange-600 font-semibold",
  treatment:     "text-indigo-600",
  stable:        "text-green-700",
  transferred:   "text-gray-500",
};

const STATUS_LABEL: Record<TriageStatus, string> = {
  waiting:       "Waiting",
  in_assessment: "In Assessment",
  treatment:     "Treatment",
  stable:        "Stable",
  transferred:   "Transferred",
};

function elapsed(iso: string): string {
  const ms = Date.now() - new Date(iso).getTime();
  const m = Math.floor(ms / 60000);
  if (m < 60) return `${m}m ago`;
  return `${Math.floor(m / 60)}h ${m % 60}m ago`;
}

export function TriageEscalationSummary({ cases }: TriageEscalationSummaryProps) {
  if (cases.length === 0) {
    return <p className="text-sm text-gray-400 italic">No triage cases.</p>;
  }

  const sorted = [...cases].sort((a, b) => {
    const order: TriagePriority[] = ["P1", "P2", "P3", "P4"];
    return order.indexOf(a.priority) - order.indexOf(b.priority);
  });

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200">
      <table className="w-full text-sm border-collapse">
        <thead className="bg-gray-50">
          <tr className="border-b border-gray-200 text-xs uppercase tracking-wider text-gray-500">
            <th className="py-2 px-3 text-left font-medium">P</th>
            <th className="py-2 px-3 text-left font-medium">Patient</th>
            <th className="py-2 px-3 text-left font-medium">Complaint</th>
            <th className="py-2 px-3 text-left font-medium">Arrived</th>
            <th className="py-2 px-3 text-left font-medium">Vet</th>
            <th className="py-2 px-3 text-left font-medium">Bay</th>
            <th className="py-2 px-3 text-left font-medium">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {sorted.map((c) => {
            const styles = PRIORITY_STYLES[c.priority];
            return (
              <tr key={c.id} className={`hover:brightness-[0.98] ${styles.row}`}>
                <td className="py-2 px-3">
                  <span className={`rounded px-2 py-0.5 text-xs font-bold ${styles.badge}`}>
                    {c.priority}
                  </span>
                </td>
                <td className="py-2 px-3">
                  <p className="font-medium text-gray-900">{c.petName}</p>
                  <p className="text-xs text-gray-500">{c.species} · {c.age}</p>
                  <p className="text-xs text-gray-400">{c.ownerName}</p>
                </td>
                <td className="py-2 px-3 text-xs text-gray-700 max-w-[160px]">
                  {c.complaint}
                </td>
                <td className="py-2 px-3 text-xs text-gray-500 whitespace-nowrap">
                  {elapsed(c.arrivalTime)}
                </td>
                <td className="py-2 px-3 text-xs text-gray-600">
                  {c.assignedVet ?? "—"}
                </td>
                <td className="py-2 px-3 text-xs font-mono text-gray-600">
                  {c.bay ?? "—"}
                </td>
                <td className="py-2 px-3 text-xs">
                  <span className={STATUS_STYLES[c.status]}>
                    {STATUS_LABEL[c.status]}
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
