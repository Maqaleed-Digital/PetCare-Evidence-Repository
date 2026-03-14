import type { DispenseStep, DispenseStepStatus } from "@/types/pharmacy";

interface DispenseWorkflowPreviewProps {
  steps: DispenseStep[];
  prescriptionRef: string;
}

type StepStatus = DispenseStepStatus;

const STEP_STYLES: Record<StepStatus, { dot: string; text: string; badge: string }> = {
  pending:     { dot: "bg-gray-300",  text: "text-gray-400",  badge: "bg-gray-100 text-gray-500"   },
  in_progress: { dot: "bg-blue-500",  text: "text-gray-900",  badge: "bg-blue-100 text-blue-700"   },
  complete:    { dot: "bg-green-500", text: "text-gray-700",  badge: "bg-green-100 text-green-700" },
  skipped:     { dot: "bg-gray-200",  text: "text-gray-400",  badge: "bg-gray-50 text-gray-400"    },
  blocked:     { dot: "bg-red-500",   text: "text-red-800",   badge: "bg-red-100 text-red-700"     },
};

const STEP_LABEL: Record<StepStatus, string> = {
  pending:     "Pending",
  in_progress: "In Progress",
  complete:    "Complete",
  skipped:     "Skipped",
  blocked:     "Blocked",
};

function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString("en-GB", {
    day: "numeric", month: "short", hour: "2-digit", minute: "2-digit",
  });
}

export function DispenseWorkflowPreview({
  steps,
  prescriptionRef,
}: DispenseWorkflowPreviewProps) {
  const sorted = [...steps].sort((a, b) => a.order - b.order);

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5 space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm font-semibold text-gray-900">
          Dispense Workflow
        </p>
        <p className="text-xs font-mono text-gray-400">{prescriptionRef}</p>
      </div>

      <ol className="relative border-l border-gray-200 space-y-4 pl-5">
        {sorted.map((step) => {
          const styles = STEP_STYLES[step.status];
          return (
            <li key={step.id} className="relative">
              <span
                className={`absolute -left-[22px] top-1 h-3 w-3 rounded-full border-2 border-white ${styles.dot}`}
              />
              <div className="flex items-start justify-between gap-2">
                <div className={styles.text}>
                  <p className="text-sm font-medium">{step.label}</p>
                  <p className="text-xs opacity-70 mt-0.5">{step.description}</p>
                  {step.completedBy && step.completedAt && (
                    <p className="text-xs opacity-50 mt-0.5">
                      {step.completedBy} · {formatDateTime(step.completedAt)}
                    </p>
                  )}
                </div>
                <span
                  className={`shrink-0 rounded px-1.5 py-0.5 text-xs font-medium ${styles.badge}`}
                >
                  {STEP_LABEL[step.status]}
                </span>
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
