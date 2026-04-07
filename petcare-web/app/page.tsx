import { ApiHealthIndicator } from "@/components/ApiHealthIndicator";

export default function Home() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-gray-900">لوحة التحكم</h1>
        <p className="mt-1 text-sm text-gray-500">
          نظرة عامة على المنصة — قراءة فقط
        </p>
      </div>
      <ApiHealthIndicator />
    </div>
  );
}
