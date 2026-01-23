import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { 
  Shield, 
  Activity, 
  Brain, 
  ScrollText, 
  Lock, 
  FileText, 
  ArrowRight,
  ExternalLink,
  CheckCircle,
  AlertTriangle,
  Database,
  Users
} from "lucide-react";
import api from "../lib/api";

const sectionConfig = {
  A: { icon: Activity, gradient: "from-sky-500 to-blue-600" },
  B: { icon: Shield, gradient: "from-emerald-500 to-teal-600" },
  C: { icon: Brain, gradient: "from-violet-500 to-purple-600" },
  D: { icon: ScrollText, gradient: "from-slate-500 to-slate-600" },
  E: { icon: Lock, gradient: "from-amber-500 to-orange-600" },
};

const statusStyles = {
  green: { bg: "bg-emerald-50", border: "border-emerald-200", text: "text-emerald-700", dot: "bg-emerald-500" },
  complete: { bg: "bg-emerald-50", border: "border-emerald-200", text: "text-emerald-700", dot: "bg-emerald-500" },
  clear: { bg: "bg-emerald-50", border: "border-emerald-200", text: "text-emerald-700", dot: "bg-emerald-500" },
  amber: { bg: "bg-amber-50", border: "border-amber-200", text: "text-amber-700", dot: "bg-amber-500" },
  idle: { bg: "bg-slate-100", border: "border-slate-200", text: "text-slate-600", dot: "bg-slate-400" },
  active: { bg: "bg-blue-50", border: "border-blue-200", text: "text-blue-700", dot: "bg-blue-500" },
  red: { bg: "bg-red-50", border: "border-red-200", text: "text-red-700", dot: "bg-red-500" },
};

export default function Governance() {
  const [summary, setSummary] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const res = await api.getGovernanceSummary();
        setSummary(res.data);
      } catch (err) {
        console.error("Error fetching governance summary:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchSummary();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64" data-testid="governance-loading">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900"></div>
      </div>
    );
  }

  // Calculate overall status
  const greenCount = summary.filter(s => ['green', 'complete', 'clear'].includes(s.status)).length;
  const amberCount = summary.filter(s => s.status === 'amber').length;

  return (
    <div className="space-y-8 animate-fade-in" data-testid="governance-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Governance Dashboard
          </h1>
          <p className="mt-2 text-slate-500">
            A–E analysis sections from Sprint 6 Day-3 evidence review
          </p>
        </div>
        <Link
          to="/report"
          className="inline-flex items-center gap-2 bg-slate-900 text-white px-5 py-2.5 rounded-xl font-medium hover:bg-slate-800 transition-colors shadow-lg shadow-slate-900/20"
          data-testid="read-report-btn"
        >
          <FileText className="w-4 h-4" />
          Read Full Report
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      {/* Overall Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white border border-slate-200 rounded-xl p-5 flex items-center gap-4">
          <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center">
            <CheckCircle className="w-6 h-6 text-emerald-600" />
          </div>
          <div>
            <p className="text-sm text-slate-500">Sections Green/Clear</p>
            <p className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>{greenCount}/5</p>
          </div>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-5 flex items-center gap-4">
          <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center">
            <AlertTriangle className="w-6 h-6 text-amber-600" />
          </div>
          <div>
            <p className="text-sm text-slate-500">Sections Amber</p>
            <p className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>{amberCount}</p>
          </div>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-5 flex items-center gap-4">
          <div className="w-12 h-12 bg-slate-100 rounded-xl flex items-center justify-center">
            <Database className="w-6 h-6 text-slate-600" />
          </div>
          <div>
            <p className="text-sm text-slate-500">Data Source</p>
            <p className="text-lg font-semibold text-slate-900">CSV Snapshots</p>
          </div>
        </div>
      </div>

      {/* A-E Section Cards */}
      <div className="space-y-4">
        {summary.map((item) => {
          const config = sectionConfig[item.section] || { icon: Shield, gradient: "from-slate-500 to-slate-600" };
          const Icon = config.icon;
          const styles = statusStyles[item.status] || statusStyles.idle;

          return (
            <div 
              key={item.section}
              className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition-shadow"
              data-testid={`governance-section-${item.section}`}
            >
              <div className="flex flex-col lg:flex-row">
                {/* Left - Section Header */}
                <div className={`lg:w-64 p-6 bg-gradient-to-br ${config.gradient} text-white flex flex-col justify-between`}>
                  <div>
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
                        <Icon className="w-5 h-5" />
                      </div>
                      <span className="text-white/80 text-sm font-medium">Section {item.section}</span>
                    </div>
                    <h3 className="text-xl font-bold" style={{ fontFamily: 'Manrope, sans-serif' }}>
                      {item.title}
                    </h3>
                  </div>
                  <div className="mt-4">
                    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-semibold bg-white/20`}>
                      <span className={`w-2 h-2 rounded-full ${styles.dot}`}></span>
                      {item.status.toUpperCase()}
                    </span>
                  </div>
                </div>

                {/* Right - Content */}
                <div className="flex-1 p-6">
                  <p className="text-slate-700 font-medium mb-4">{item.finding}</p>
                  
                  {/* Details Grid */}
                  {item.details && (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      {Object.entries(item.details).slice(0, 4).map(([key, value]) => (
                        <div key={key} className="bg-slate-50 rounded-lg p-3">
                          <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">
                            {formatKey(key)}
                          </p>
                          <p className="text-sm font-semibold text-slate-900">
                            {formatValue(value)}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Source Files */}
                  {item.source_files && (
                    <div className="flex flex-wrap gap-2 pt-3 border-t border-slate-100">
                      <span className="text-xs text-slate-400">Sources:</span>
                      {item.source_files.map(file => (
                        <span key={file} className="text-xs font-mono bg-slate-100 text-slate-600 px-2 py-0.5 rounded">
                          {file}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Special: Activity Snapshot for Section A */}
                  {item.section === "A" && item.activity_snapshot && (
                    <ActivitySnapshot data={item.activity_snapshot} />
                  )}

                  {/* Special: Bypass Roles for Section E */}
                  {item.section === "E" && item.bypass_roles_detail && (
                    <BypassRolesTable roles={item.bypass_roles_detail} />
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Navigation */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <NavCard 
          to="/audit" 
          icon={ScrollText} 
          title="Audit Events" 
          description="Explore audit event logs"
          testId="nav-audit"
        />
        <NavCard 
          to="/explainability" 
          icon={Brain} 
          title="AI Explainability" 
          description="TCF rule runs and logs"
          testId="nav-explainability"
        />
        <NavCard 
          to="/security" 
          icon={Lock} 
          title="Security Review" 
          description="RLS status and permissions"
          testId="nav-security"
        />
      </div>

      {/* Report Deep Link Banner */}
      <Link 
        to="/report"
        className="block bg-gradient-to-r from-slate-900 to-slate-800 rounded-2xl p-6 text-white hover:from-slate-800 hover:to-slate-700 transition-all group"
        data-testid="report-banner"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-white/10 rounded-xl flex items-center justify-center">
              <FileText className="w-7 h-7" />
            </div>
            <div>
              <h3 className="text-xl font-bold" style={{ fontFamily: 'Manrope, sans-serif' }}>
                Sprint 6 Day-3 Analysis Report
              </h3>
              <p className="text-slate-300 mt-1">
                Complete A–E governance review with findings, recommendations, and UI-0 readiness signals
              </p>
            </div>
          </div>
          <div className="hidden md:flex items-center gap-2 text-slate-300 group-hover:text-white transition-colors">
            <span className="font-medium">Read Report</span>
            <ExternalLink className="w-5 h-5" />
          </div>
        </div>
      </Link>
    </div>
  );
}

function ActivitySnapshot({ data }) {
  const entries = Object.entries(data);
  if (entries.length === 0) return null;

  return (
    <div className="mt-4 pt-4 border-t border-slate-100">
      <p className="text-xs text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-2">
        <Database className="w-3 h-3" />
        Window Activity Snapshot
      </p>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
        {entries.map(([table, info]) => (
          <div key={table} className="bg-slate-50 rounded px-3 py-2">
            <p className="text-xs font-mono text-slate-600 truncate" title={table}>{table}</p>
            <p className="text-sm font-semibold text-slate-900">{info.rows} rows</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function BypassRolesTable({ roles }) {
  if (!roles || roles.length === 0) return null;

  return (
    <div className="mt-4 pt-4 border-t border-slate-100">
      <p className="text-xs text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-2">
        <Users className="w-3 h-3" />
        Bypass RLS Roles
      </p>
      <div className="flex flex-wrap gap-2">
        {roles.map(role => (
          <span 
            key={role.rolname}
            className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
              role.rolbypassrls === 't' 
                ? 'bg-amber-100 text-amber-700' 
                : 'bg-slate-100 text-slate-600'
            }`}
          >
            {role.rolname}
            {role.rolbypassrls === 't' && (
              <AlertTriangle className="w-3 h-3" />
            )}
          </span>
        ))}
      </div>
      <p className="text-xs text-slate-500 mt-2 italic">
        Note: service_role/postgres bypass is expected for Supabase architecture
      </p>
    </div>
  );
}

function NavCard({ to, icon: Icon, title, description, testId }) {
  return (
    <Link
      to={to}
      className="bg-white border border-slate-200 rounded-xl p-5 hover:border-slate-300 hover:shadow-sm transition-all flex items-center gap-4 group"
      data-testid={testId}
    >
      <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center group-hover:bg-slate-200 transition-colors">
        <Icon className="w-5 h-5 text-slate-600" />
      </div>
      <div className="flex-1 min-w-0">
        <h4 className="font-semibold text-slate-900">{title}</h4>
        <p className="text-sm text-slate-500 truncate">{description}</p>
      </div>
      <ArrowRight className="w-5 h-5 text-slate-300 group-hover:text-slate-600 transition-colors" />
    </Link>
  );
}

function formatKey(key) {
  return key.replace(/_/g, ' ').replace(/([A-Z])/g, ' $1').trim();
}

function formatValue(value) {
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  if (value === null || value === undefined) return '—';
  return String(value);
}
