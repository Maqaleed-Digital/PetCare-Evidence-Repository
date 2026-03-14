import type { EmergencyTimelineEvent, EmergencyEventType } from "@/types/emergency";

interface EmergencyTimelineProps {
  events: EmergencyTimelineEvent[];
  caseLabel: string;
}

type EvtType = EmergencyEventType;

const TYPE_STYLES: Record<EvtType, { dot: string; badge: string; label: string }> = {
  alert_raised:       { dot: "bg-red-600",    badge: "bg-red-100 text-red-700",     label: "Alert Raised"        },
  acknowledged:       { dot: "bg-orange-500", badge: "bg-orange-100 text-orange-700",label: "Acknowledged"       },
  triage_assessment:  { dot: "bg-yellow-500", badge: "bg-yellow-100 text-yellow-800",label: "Triage"             },
  treatment_started:  { dot: "bg-blue-600",   badge: "bg-blue-100 text-blue-700",   label: "Treatment Started"   },
  medication_given:   { dot: "bg-indigo-500", badge: "bg-indigo-100 text-indigo-700",label: "Medication Given"   },
  vitals_recorded:    { dot: "bg-teal-500",   badge: "bg-teal-100 text-teal-700",   label: "Vitals Recorded"     },
  handoff_initiated:  { dot: "bg-purple-500", badge: "bg-purple-100 text-purple-700",label: "Handoff Initiated"  },
  handoff_complete:   { dot: "bg-purple-700", badge: "bg-purple-100 text-purple-800",label: "Handoff Complete"   },
  case_closed:        { dot: "bg-green-600",  badge: "bg-green-100 text-green-700", label: "Case Closed"         },
};

function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString("en-GB", {
    day: "numeric", month: "short", hour: "2-digit", minute: "2-digit", second: "2-digit",
  });
}

export function EmergencyTimeline({ events, caseLabel }: EmergencyTimelineProps) {
  if (events.length === 0) {
    return <p className="text-sm text-gray-400 italic">No timeline events.</p>;
  }

  const sorted = [...events].sort(
    (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  );

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5 space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm font-semibold text-gray-900">Case Timeline</p>
        <p className="text-xs font-mono text-gray-400">{caseLabel}</p>
      </div>

      <ol className="relative border-l border-gray-200 space-y-4 pl-5">
        {sorted.map((evt) => {
          const s = TYPE_STYLES[evt.eventType];
          return (
            <li key={evt.id} className="relative">
              <span
                className={`absolute -left-[22px] top-1 h-3 w-3 rounded-full border-2 border-white ${s.dot}`}
              />
              <div className="flex items-start justify-between gap-2 flex-wrap">
                <div>
                  <span className={`rounded px-1.5 py-0.5 text-xs font-medium ${s.badge}`}>
                    {s.label}
                  </span>
                  <p className="text-sm text-gray-800 mt-1">{evt.description}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{evt.actor}</p>
                </div>
                <p className="text-xs text-gray-400 whitespace-nowrap">
                  {formatDateTime(evt.timestamp)}
                </p>
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
