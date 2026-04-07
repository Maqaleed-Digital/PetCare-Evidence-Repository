interface QuickAction {
  label: string;
  description: string;
  icon: string;
  variant: "primary" | "secondary" | "danger" | "neutral";
}

const ACTIONS: QuickAction[] = [
  {
    label: "حجز موعد",
    description: "جدولة زيارة جديدة مع طبيبك البيطري",
    icon: "📅",
    variant: "primary",
  },
  {
    label: "عرض السجلات",
    description: "الوصول إلى السجل الطبي الكامل والوثائق",
    icon: "📋",
    variant: "secondary",
  },
  {
    label: "الوصول الطارئ",
    description: "مشاركة البيانات الصحية الحرجة مع الطبيب البيطري للطوارئ",
    icon: "🚨",
    variant: "danger",
  },
  {
    label: "إعدادات الموافقة",
    description: "إدارة مشاركة البيانات وتفضيلات الموافقة",
    icon: "🔒",
    variant: "neutral",
  },
];

const VARIANT_STYLES: Record<QuickAction["variant"], string> = {
  primary:
    "border-blue-200 bg-blue-50 text-blue-800 hover:bg-blue-100",
  secondary:
    "border-gray-200 bg-white text-gray-700 hover:bg-gray-50",
  danger:
    "border-red-200 bg-red-50 text-red-800 hover:bg-red-100",
  neutral:
    "border-gray-200 bg-gray-50 text-gray-700 hover:bg-gray-100",
};

export function QuickActions() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
      {ACTIONS.map((action) => (
        <button
          key={action.label}
          type="button"
          disabled
          title="قراءة فقط — غير تفاعلي بعد"
          className={`flex items-start gap-3 rounded-lg border p-4 text-start transition-colors cursor-default opacity-80 ${
            VARIANT_STYLES[action.variant]
          }`}
        >
          <span className="text-xl select-none">{action.icon}</span>
          <div>
            <p className="text-sm font-semibold">{action.label}</p>
            <p className="text-xs opacity-70 mt-0.5">{action.description}</p>
          </div>
        </button>
      ))}
    </div>
  );
}
