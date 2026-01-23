import { NavLink, Outlet } from "react-router-dom";
import { 
  LayoutDashboard, 
  FolderArchive, 
  Shield, 
  ScrollText, 
  Brain, 
  Lock,
  FileText,
  Menu,
  X
} from "lucide-react";
import { useState } from "react";

const navItems = [
  { path: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { path: "/evidence", label: "Evidence Packs", icon: FolderArchive },
  { path: "/governance", label: "Governance", icon: Shield },
  { path: "/audit", label: "Audit Events", icon: ScrollText },
  { path: "/explainability", label: "Explainability", icon: Brain },
  { path: "/security", label: "Security", icon: Lock },
  { path: "/report", label: "Day-3 Report", icon: FileText },
];

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
          data-testid="sidebar-backdrop"
        />
      )}

      {/* Sidebar */}
      <aside 
        className={`
          fixed top-0 left-0 z-50 h-full w-64 bg-slate-50 border-r border-slate-200 
          transform transition-transform duration-200 ease-in-out
          lg:translate-x-0 lg:static lg:z-0
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
        data-testid="sidebar"
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-16 px-6 border-b border-slate-200">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-slate-900 rounded-lg flex items-center justify-center">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-lg text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
                PetCare
              </span>
            </div>
            <button 
              className="lg:hidden p-1 hover:bg-slate-200 rounded"
              onClick={() => setSidebarOpen(false)}
              data-testid="close-sidebar-btn"
            >
              <X className="w-5 h-5 text-slate-600" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={({ isActive }) =>
                  `sidebar-nav-item ${isActive ? 'active' : ''}`
                }
                data-testid={`nav-${item.path.replace('/', '')}`}
              >
                <item.icon className="w-5 h-5" />
                {item.label}
              </NavLink>
            ))}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-slate-200">
            <div className="text-xs text-slate-500 leading-relaxed">
              <p className="font-medium text-slate-700">PetCare Standalone</p>
              <p className="mt-1">No portfolio/Crédito artifacts included.</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="sticky top-0 z-30 h-16 bg-white border-b border-slate-200 flex items-center px-6">
          <button 
            className="lg:hidden p-2 -ml-2 hover:bg-slate-100 rounded-lg mr-4"
            onClick={() => setSidebarOpen(true)}
            data-testid="open-sidebar-btn"
          >
            <Menu className="w-5 h-5 text-slate-600" />
          </button>
          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-500">Sprint 6</span>
            <span className="text-slate-300">/</span>
            <span className="text-sm font-medium text-slate-900">Day-3 Evidence</span>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
