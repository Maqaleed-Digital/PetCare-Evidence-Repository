import type { AuditEvent } from "@/types/admin";

interface AuditEventViewerProps {
  events: AuditEvent[];
}

type Outcome = AuditEvent["outcome"];
type ActorRole = AuditEvent["actorRole"];

const OUTCOME_STYLES: Record<Outcome, string> = {
  success: "text-green-700 bg-green-50",
  failure: "text-red-700 bg-red-50",
  denied: "text-yellow-700 bg-yellow-50",
};

const ROLE_LABEL: Record<ActorRole, string> = {
  owner: "Owner",
  vet: "Vet",
  admin: "Admin",
  system: "System",
};

function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString("en-GB", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export function AuditEventViewer({ events }: AuditEventViewerProps) {
  if (events.length === 0) {
    return (
      <p className="text-sm text-gray-400 italic">No audit events recorded.</p>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200">
      <table className="w-full text-xs border-collapse">
        <thead className="bg-gray-50">
          <tr className="border-b border-gray-200 text-gray-500 uppercase tracking-wider">
            <th className="py-2 px-3 text-left font-medium">Timestamp</th>
            <th className="py-2 px-3 text-left font-medium">Actor</th>
            <th className="py-2 px-3 text-left font-medium">Role</th>
            <th className="py-2 px-3 text-left font-medium">Action</th>
            <th className="py-2 px-3 text-left font-medium">Resource</th>
            <th className="py-2 px-3 text-left font-medium">Outcome</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100 bg-white">
          {events.map((evt) => (
            <tr key={evt.id} className="hover:bg-gray-50">
              <td className="py-2 px-3 font-mono text-gray-500 whitespace-nowrap">
                {formatDateTime(evt.timestamp)}
              </td>
              <td className="py-2 px-3 text-gray-900">{evt.actor}</td>
              <td className="py-2 px-3 text-gray-500">
                {ROLE_LABEL[evt.actorRole]}
              </td>
              <td className="py-2 px-3 font-mono text-gray-700">{evt.action}</td>
              <td className="py-2 px-3 text-gray-500">
                {evt.resourceType}/{evt.resourceId}
              </td>
              <td className="py-2 px-3">
                <span
                  className={`rounded px-1.5 py-0.5 font-semibold ${OUTCOME_STYLES[evt.outcome]}`}
                >
                  {evt.outcome}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
