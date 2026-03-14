interface QuickAction {
  label: string;
  description: string;
  icon: string;
  variant: "primary" | "secondary" | "danger" | "neutral";
}

const ACTIONS: QuickAction[] = [
  {
    label: "Book Appointment",
    description: "Schedule a new visit with your vet",
    icon: "📅",
    variant: "primary",
  },
  {
    label: "View Records",
    description: "Access full medical history and documents",
    icon: "📋",
    variant: "secondary",
  },
  {
    label: "Emergency Access",
    description: "Share critical health data with emergency vet",
    icon: "🚨",
    variant: "danger",
  },
  {
    label: "Consent Settings",
    description: "Manage data sharing and consent preferences",
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
          title="Read-only shell — not yet interactive"
          className={`flex items-start gap-3 rounded-lg border p-4 text-left transition-colors cursor-default opacity-80 ${
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
