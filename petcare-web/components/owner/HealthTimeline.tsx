import type { HealthTimelineEvent, TimelineEventType } from "@/types/owner";

interface HealthTimelineProps {
  events: HealthTimelineEvent[];
}

const TYPE_STYLES: Record<TimelineEventType, string> = {
  checkup: "bg-blue-100 text-blue-700",
  vaccination: "bg-green-100 text-green-700",
  surgery: "bg-red-100 text-red-700",
  diagnosis: "bg-orange-100 text-orange-700",
  prescription: "bg-purple-100 text-purple-700",
  observation: "bg-gray-100 text-gray-600",
};

const TYPE_LABEL: Record<TimelineEventType, string> = {
  checkup: "Check-up",
  vaccination: "Vaccination",
  surgery: "Surgery",
  diagnosis: "Diagnosis",
  prescription: "Prescription",
  observation: "Observation",
};

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export function HealthTimeline({ events }: HealthTimelineProps) {
  if (events.length === 0) {
    return (
      <p className="text-sm text-gray-400 italic">No health events recorded.</p>
    );
  }

  return (
    <ol className="relative border-l border-gray-200 space-y-4 pl-5">
      {events.map((event) => (
        <li key={event.id} className="relative">
          <span className="absolute -left-[22px] top-1 h-3 w-3 rounded-full border-2 border-white bg-blue-400 ring-1 ring-blue-200" />
          <div className="flex items-start gap-2 flex-wrap">
            <span
              className={`rounded px-1.5 py-0.5 text-xs font-medium ${TYPE_STYLES[event.type]}`}
            >
              {TYPE_LABEL[event.type]}
            </span>
            <span className="text-xs text-gray-400">{formatDate(event.date)}</span>
          </div>
          <p className="mt-1 text-sm font-medium text-gray-900">{event.title}</p>
          <p className="text-xs text-gray-500">{event.description}</p>
          {event.vetName && (
            <p className="text-xs text-gray-400 mt-0.5">{event.vetName}</p>
          )}
        </li>
      ))}
    </ol>
  );
}
