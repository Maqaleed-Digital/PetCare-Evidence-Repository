import type { ExportOption } from "@/types/admin";

interface EvidenceExportPanelProps {
  options: ExportOption[];
}

const FORMAT_STYLES: Record<ExportOption["format"], string> = {
  json: "bg-blue-50 text-blue-700 border-blue-200",
  csv: "bg-green-50 text-green-700 border-green-200",
  pdf: "bg-red-50 text-red-700 border-red-200",
};

export function EvidenceExportPanel({ options }: EvidenceExportPanelProps) {
  if (options.length === 0) {
    return (
      <p className="text-sm text-gray-400 italic">No export options configured.</p>
    );
  }

  return (
    <div className="space-y-2">
      <p className="text-xs text-yellow-700 bg-yellow-50 border border-yellow-200 rounded px-3 py-2">
        Read-only shell — export actions are disabled in PH-UI-4. No data
        transmission occurs.
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {options.map((opt) => (
          <button
            key={opt.id}
            type="button"
            disabled
            title="Export disabled — read-only shell"
            className="flex items-start gap-3 rounded-lg border border-gray-200 bg-white p-4 text-left opacity-60 cursor-default hover:bg-gray-50"
          >
            <span
              className={`shrink-0 rounded border px-1.5 py-0.5 text-xs font-bold uppercase ${
                FORMAT_STYLES[opt.format]
              }`}
            >
              {opt.format}
            </span>
            <div>
              <p className="text-sm font-medium text-gray-800">{opt.label}</p>
              <p className="text-xs text-gray-500 mt-0.5">{opt.description}</p>
              <p className="text-xs text-gray-400 mt-0.5">Scope: {opt.scope}</p>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
