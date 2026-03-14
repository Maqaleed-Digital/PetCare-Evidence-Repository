import type { ClinicConfiguration } from "@/types/admin";

interface ClinicConfigurationSummaryProps {
  config: ClinicConfiguration;
}

export function ClinicConfigurationSummary({
  config,
}: ClinicConfigurationSummaryProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white overflow-hidden">
      <div className="bg-gray-50 px-5 py-3 border-b border-gray-200">
        <h3 className="text-sm font-semibold text-gray-900">
          {config.clinicName}
        </h3>
        <p className="text-xs text-gray-500 mt-0.5">
          ID: {config.clinicId} · TZ: {config.timezone}
        </p>
      </div>

      <table className="w-full text-sm">
        <tbody className="divide-y divide-gray-100">
          {config.entries.map((entry) => (
            <tr key={entry.key} className="hover:bg-gray-50">
              <td className="px-5 py-2.5 text-xs font-medium text-gray-500 w-1/2">
                {entry.label}
              </td>
              <td className="px-5 py-2.5 text-sm text-gray-900 font-mono">
                {entry.value}
                {!entry.editable && (
                  <span className="ml-2 text-xs text-gray-400 font-sans">
                    (locked)
                  </span>
                )}
              </td>
            </tr>
          ))}
          <tr className="hover:bg-gray-50">
            <td className="px-5 py-2.5 text-xs font-medium text-gray-500">
              Data Retention
            </td>
            <td className="px-5 py-2.5 text-sm text-gray-900 font-mono">
              {config.dataRetentionDays} days
            </td>
          </tr>
          <tr className="hover:bg-gray-50">
            <td className="px-5 py-2.5 text-xs font-medium text-gray-500">
              PDPL Consent Version
            </td>
            <td className="px-5 py-2.5 text-sm text-gray-900 font-mono">
              {config.pdplConsentVersion}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}
