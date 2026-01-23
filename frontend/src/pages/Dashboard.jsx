import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { 
  FolderArchive, 
  Shield, 
  ScrollText, 
  Brain, 
  Lock,
  CheckCircle,
  AlertTriangle,
  Activity,
  ArrowRight
} from "lucide-react";
import api from "../lib/api";

const statusColors = {
  green: "bg-emerald-50 text-emerald-700 border-emerald-200",
  complete: "bg-emerald-50 text-emerald-700 border-emerald-200",
  clear: "bg-emerald-50 text-emerald-700 border-emerald-200",
  amber: "bg-amber-50 text-amber-700 border-amber-200",
  idle: "bg-slate-100 text-slate-700 border-slate-200",
  red: "bg-red-50 text-red-700 border-red-200",
};

const sectionIcons = {
  A: Activity,
  B: Shield,
  C: Brain,
  D: ScrollText,
  E: Lock,
};

export default function Dashboard() {
  const [governance, setGovernance] = useState([]);
  const [packs, setPacks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [govRes, packsRes] = await Promise.all([
          api.getGovernanceSummary(),
          api.getEvidencePacks()
        ]);
        setGovernance(govRes.data);
        setPacks(packsRes.data);
      } catch (err) {
        console.error("Error fetching dashboard data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64" data-testid="dashboard-loading">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900"></div>
      </div>
    );
  }

  const totalFiles = packs.reduce((acc, p) => acc + p.file_count, 0);
  const verifiedFiles = packs.reduce((acc, p) => acc + p.verified_count, 0);
  const greenCount = governance.filter(g => ['green', 'complete', 'clear'].includes(g.status)).length;
  const amberCount = governance.filter(g => g.status === 'amber').length;

  return (
    <div className="space-y-8 animate-fade-in" data-testid="dashboard">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>
          Dashboard
        </h1>
        <p className="mt-2 text-slate-500">
          Sprint 6 Day-3 Evidence Analysis Overview
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          icon={FolderArchive}
          label="Evidence Files"
          value={totalFiles}
          subtext={`${verifiedFiles} verified`}
          href="/evidence"
          testId="metric-files"
        />
        <MetricCard
          icon={CheckCircle}
          label="Sections Green"
          value={`${greenCount}/5`}
          subtext="Governance checks"
          href="/governance"
          testId="metric-green"
        />
        <MetricCard
          icon={AlertTriangle}
          label="Sections Amber"
          value={amberCount}
          subtext="Require attention"
          href="/governance"
          testId="metric-amber"
        />
        <MetricCard
          icon={Shield}
          label="Integrity"
          value={verifiedFiles === totalFiles ? "Verified" : "Partial"}
          subtext={`${verifiedFiles}/${totalFiles} checksums`}
          href="/evidence"
          testId="metric-integrity"
        />
      </div>

      {/* Governance Summary */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Governance Summary (A–E)
          </h2>
          <Link 
            to="/governance" 
            className="text-sm font-medium text-slate-600 hover:text-slate-900 flex items-center gap-1"
            data-testid="view-governance-link"
          >
            View all <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {governance.map((item) => {
            const Icon = sectionIcons[item.section] || Shield;
            return (
              <div 
                key={item.section} 
                className="governance-card"
                data-testid={`governance-card-${item.section}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center">
                      <Icon className="w-5 h-5 text-slate-600" />
                    </div>
                    <div>
                      <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                        Section {item.section}
                      </p>
                      <h3 className="font-semibold text-slate-900">{item.title}</h3>
                    </div>
                  </div>
                  <span className={`status-badge ${statusColors[item.status] || 'gray'}`}>
                    {item.status.toUpperCase()}
                  </span>
                </div>
                <p className="mt-4 text-sm text-slate-600">{item.finding}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Quick Links */}
      <div>
        <h2 className="text-xl font-bold text-slate-900 mb-4" style={{ fontFamily: 'Manrope, sans-serif' }}>
          Quick Access
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <QuickLinkCard
            to="/report"
            icon={ScrollText}
            title="Day-3 Report"
            description="Full analysis report with all findings"
            testId="quick-report"
          />
          <QuickLinkCard
            to="/security"
            icon={Lock}
            title="Security Review"
            description="RLS status and bypass roles"
            testId="quick-security"
          />
          <QuickLinkCard
            to="/explainability"
            icon={Brain}
            title="AI Explainability"
            description="Rule runs and explainability logs"
            testId="quick-explainability"
          />
        </div>
      </div>

      {/* Standalone Notice */}
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-6" data-testid="standalone-notice">
        <p className="text-sm text-slate-600">
          <span className="font-medium text-slate-900">PetCare is a standalone project.</span>
          {" "}No portfolio/Crédito artifacts are included. This evidence repository is the authoritative source of truth.
        </p>
      </div>
    </div>
  );
}

function MetricCard({ icon: Icon, label, value, subtext, href, testId }) {
  return (
    <Link 
      to={href}
      className="governance-card cursor-pointer hover:border-slate-300"
      data-testid={testId}
    >
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center">
          <Icon className="w-5 h-5 text-slate-600" />
        </div>
        <div>
          <p className="text-sm text-slate-500">{label}</p>
          <p className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
            {value}
          </p>
          <p className="text-xs text-slate-400">{subtext}</p>
        </div>
      </div>
    </Link>
  );
}

function QuickLinkCard({ to, icon: Icon, title, description, testId }) {
  return (
    <Link 
      to={to}
      className="governance-card cursor-pointer hover:border-slate-300 flex items-center gap-4"
      data-testid={testId}
    >
      <div className="w-12 h-12 bg-slate-900 rounded-lg flex items-center justify-center flex-shrink-0">
        <Icon className="w-6 h-6 text-white" />
      </div>
      <div>
        <h3 className="font-semibold text-slate-900">{title}</h3>
        <p className="text-sm text-slate-500">{description}</p>
      </div>
      <ArrowRight className="w-5 h-5 text-slate-400 ml-auto" />
    </Link>
  );
}
