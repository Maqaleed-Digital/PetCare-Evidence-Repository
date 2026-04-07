"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV = [
  { href: "/", label: "الرئيسية" },
  { href: "/owner", label: "المالك" },
  { href: "/vet", label: "البيطري" },
  { href: "/admin", label: "الإدارة" },
  { href: "/pharmacy", label: "الصيدلية" },
  { href: "/emergency", label: "الطوارئ" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-48 bg-gray-50 border-e border-gray-200 flex flex-col py-4 shrink-0">
      <nav className="flex flex-col gap-1 px-3">
        {NAV.map(({ href, label }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={`rounded px-3 py-2 text-sm font-medium transition-colors ${
                active
                  ? "bg-blue-50 text-blue-700"
                  : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
              }`}
            >
              {label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
