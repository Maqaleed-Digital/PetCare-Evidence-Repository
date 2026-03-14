import type { ApiStatus } from "@/types/api";

interface StatusCardProps {
  title: string;
  value: string | null;
  status?: ApiStatus | null;
  sub?: string | null;
}

const STATUS_STYLES: Record<ApiStatus, string> = {
  ok: "bg-green-50 border-green-200 text-green-700",
  degraded: "bg-red-50 border-red-200 text-red-700",
  unknown: "bg-gray-50 border-gray-200 text-gray-500",
};

export function StatusCard({ title, value, status, sub }: StatusCardProps) {
  const style = status ? STATUS_STYLES[status] : STATUS_STYLES.unknown;
  return (
    <div className={`rounded-lg border p-4 ${style}`}>
      <p className="text-xs font-medium uppercase tracking-wider opacity-70">
        {title}
      </p>
      <p className="mt-1 text-lg font-semibold">{value ?? "—"}</p>
      {sub && <p className="mt-1 text-xs opacity-60 truncate">{sub}</p>}
    </div>
  );
}
