import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Shield, Activity, Brain, ScrollText, Lock, FileText, ArrowRight } from "lucide-react";
import api from "../lib/api";

const sectionConfig = {
  A: { icon: Activity, color: "emerald" },
  B: { icon: Shield, color: "emerald" },
  C: { icon: Brain, color: "emerald" },
  D: { icon: ScrollText, color: "slate" },
  E: { icon: Lock, color: "amber" },
};

const statusStyles = {
  green: { bg: "bg-emerald-50", border: "border-emerald-200", text: "text-emerald-700", icon: "text-emerald-500" },
  complete: { bg: "bg-emerald-50", border: "border-emerald-200", text: "text-emerald-700", icon: "text-emerald-500" },
  clear: { bg: "bg-emerald-50", border: "border-emerald-200", text: "text-emerald-700", icon: "text-emerald-500" },
  amber: { bg: "bg-amber-50", border: "border-amber-200", text: "text-amber-700", icon: "text-amber-500" },
  idle: { bg: "bg-slate-50", border: "border-slate-200", text: "text-slate-700", icon: "text-slate-500" },
  red: { bg: "bg-red-50", border: "border-red-200", text: "text-red-700", icon: "text-red-500" },
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

  return (
    <div className="space-y-8 animate-fade-in" data-testid="governance-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Governance Summary
          </h1>
          <p className="mt-2 text-slate-500">
            A–E analysis sections from Sprint 6 Day-3 evidence review
          </p>
        </div>
        <Link
          to="/report"
          className="inline-flex items-center gap-2 bg-slate-900 text-white px-4 py-2 rounded-lg font-medium hover:bg-slate-800 transition-colors"
          data-testid="view-full-report"
        >
          <FileText className="w-4 h-4" />
          View Full Report
        </Link>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {summary.map((item) => {
          const config = sectionConfig[item.section] || { icon: Shield, color: "slate" };
          const Icon = config.icon;
          const styles = statusStyles[item.status] || statusStyles.idle;

          return (
            <div 
              key={item.section}
              className={`rounded-xl border-2 ${styles.border} ${styles.bg} p-6`}
              data-testid={`governance-section-${item.section}`}
            >
              <div className="flex items-start gap-4">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${styles.bg} border ${styles.border}`}>
                  <Icon className={`w-6 h-6 ${styles.icon}`} />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                        Section {item.section}
                      </span>
                      <h3 className="text-lg font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
                        {item.title}
                      </h3>
                    </div>
                    <span className={`status-badge ${styles.text} ${styles.bg} border ${styles.border}`}>
                      {item.status.toUpperCase()}
                    </span>
                  </div>
                  
                  <p className="mt-3 text-slate-600">{item.finding}</p>

                  {/* Details */}
                  {item.details && (
                    <div className="mt-4 pt-4 border-t border-slate-200/50">
                      <div className="grid grid-cols-2 gap-3">
                        {Object.entries(item.details).slice(0, 4).map(([key, value]) => (
                          <div key={key}>
                            <p className="text-xs text-slate-500 capitalize">{key.replace(/_/g, ' ')}</p>
                            <p className="text-sm font-semibold text-slate-900">
                              {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : String(value)}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Navigation Links */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <NavCard 
          to="/audit" 
          icon={ScrollText} 
          title="Audit Events" 
          description="Explore audit event logs and filters"
          testId="nav-audit"
        />
        <NavCard 
          to="/explainability" 
          icon={Brain} 
          title="AI Explainability" 
          description="TCF rule runs and reasoning logs"
          testId="nav-explainability"
        />
        <NavCard 
          to="/security" 
          icon={Lock} 
          title="Security Review" 
          description="RLS status and role permissions"
          testId="nav-security"
        />
      </div>

      {/* Legend */}
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <h3 className="font-semibold text-slate-900 mb-4">Status Legend</h3>
        <div className="flex flex-wrap gap-4">
          <LegendItem status="green" label="GREEN / COMPLETE / CLEAR" description="No issues found" />
          <LegendItem status="amber" label="AMBER" description="Requires attention" />
          <LegendItem status="idle" label="IDLE" description="No activity / Pre-production" />
          <LegendItem status="red" label="RED" description="Critical issue" />
        </div>
      </div>
    </div>
  );
}

function NavCard({ to, icon: Icon, title, description, testId }) {
  return (
    <Link
      to={to}
      className="governance-card cursor-pointer hover:border-slate-300 flex items-center gap-4"
      data-testid={testId}
    >
      <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center flex-shrink-0">
        <Icon className="w-5 h-5 text-slate-600" />
      </div>
      <div className="flex-1 min-w-0">
        <h4 className="font-semibold text-slate-900">{title}</h4>
        <p className="text-sm text-slate-500 truncate">{description}</p>
      </div>
      <ArrowRight className="w-5 h-5 text-slate-400" />
    </Link>
  );
}

function LegendItem({ status, label, description }) {
  const styles = statusStyles[status] || statusStyles.idle;
  return (
    <div className="flex items-center gap-2">
      <span className={`w-3 h-3 rounded-full ${styles.bg} border ${styles.border}`} />
      <span className="text-sm">
        <span className="font-medium text-slate-900">{label}</span>
        <span className="text-slate-500"> — {description}</span>
      </span>
    </div>
  );
}
