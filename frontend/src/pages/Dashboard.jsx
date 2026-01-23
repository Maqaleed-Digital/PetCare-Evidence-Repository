import { useEffect, useState, useMemo } from "react";
import { Link } from "react-router-dom";
import { 
  BarChart3,
  FileText,
  Shield,
  Activity,
  Lock,
  ArrowRight,
  Tag,
  CheckCircle,
  Database
} from "lucide-react";
import api, { getVerificationStatus, BASELINE_TAG, EVIDENCE_PACK_ID, EVIDENCE_ROOT } from "../lib/api";

// E3: Governance Dashboard (A–E Cards) (UI0-G5)
// Cards derived from evidence file counts with prefix matching
// Each card deep-links to /evidence with query filter

const CARD_CONFIG = {
  A: {
    prefix: 'A_counts__',
    title: 'Counts',
    description: 'Row count snapshots per table',
    icon: Database,
    color: 'sky',
    link: '/evidence?prefix=A_counts__'
  },
  B: {
    prefix: 'B_dist__',
    title: 'Distributions',
    description: 'Value distribution analysis',
    icon: BarChart3,
    color: 'violet',
    link: '/evidence?prefix=B_dist__'
  },
  C: {
    prefix: 'B_quality__',
    title: 'Quality',
    description: 'Data quality checks',
    icon: CheckCircle,
    color: 'emerald',
    link: '/evidence?prefix=B_quality__'
  },
  D: {
    prefix: 'ZZ_window_activity_snapshot',
    title: 'Window Snapshot',
    description: 'Activity window evidence',
    icon: Activity,
    color: 'amber',
    link: '/evidence?search=ZZ_window',
    checkPresence: true
  },
  E: {
    prefix: 'addendum/',
    title: 'Security Addendum',
    description: 'Security evidence files',
    icon: Lock,
    color: 'rose',
    link: '/security',
    isAddendum: true
  }
};

const COLOR_CLASSES = {
  sky: { bg: 'bg-sky-50', border: 'border-sky-200', icon: 'bg-sky-100 text-sky-600', text: 'text-sky-700' },
  violet: { bg: 'bg-violet-50', border: 'border-violet-200', icon: 'bg-violet-100 text-violet-600', text: 'text-violet-700' },
  emerald: { bg: 'bg-emerald-50', border: 'border-emerald-200', icon: 'bg-emerald-100 text-emerald-600', text: 'text-emerald-700' },
  amber: { bg: 'bg-amber-50', border: 'border-amber-200', icon: 'bg-amber-100 text-amber-600', text: 'text-amber-700' },
  rose: { bg: 'bg-rose-50', border: 'border-rose-200', icon: 'bg-rose-100 text-rose-600', text: 'text-rose-700' },
};

export default function Dashboard() {
  const [files, setFiles] = useState({ evidence: [], addendum: [] });
  const [manifestStatus, setManifestStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await api.getPackFiles(EVIDENCE_PACK_ID);
        setFiles({
          evidence: res.data.evidence || [],
          addendum: res.data.addendum || []
        });
        setManifestStatus(res.data.manifest_status);
      } catch (err) {
        console.error("Error fetching dashboard data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // E3: Calculate counts for each card based on prefix matching
  const cardCounts = useMemo(() => {
    const allFiles = [...files.evidence, ...files.addendum];
    const counts = {};
    
    Object.entries(CARD_CONFIG).forEach(([key, config]) => {
      if (config.isAddendum) {
        // E: Count addendum files
        counts[key] = files.addendum.length;
      } else if (config.checkPresence) {
        // D: Check presence of specific file
        counts[key] = allFiles.some(f => f.name.startsWith(config.prefix)) ? 1 : 0;
      } else {
        // A, B, C: Count files with prefix
        counts[key] = files.evidence.filter(f => f.name.startsWith(config.prefix)).length;
      }
    });
    
    return counts;
  }, [files]);

  // Calculate overall verification stats
  const verificationStats = useMemo(() => {
    const allFiles = [...files.evidence, ...files.addendum];
    let ok = 0, fail = 0, missing = 0;
    
    allFiles.forEach(f => {
      const status = getVerificationStatus(f);
      if (status === 'OK') ok++;
      else if (status === 'FAIL') fail++;
      else missing++;
    });
    
    return { ok, fail, missing, total: allFiles.length };
  }, [files]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64" data-testid="dashboard-loading">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in" data-testid="dashboard">
      {/* Header with Baseline Tag */}
      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Governance Dashboard
          </h1>
          <p className="mt-2 text-slate-500">
            Sprint UI-0 evidence summary for {EVIDENCE_ROOT}
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-2 bg-slate-100 rounded-lg">
          <Tag className="w-4 h-4 text-slate-500" />
          <span className="text-sm font-mono text-slate-700">{BASELINE_TAG}</span>
        </div>
      </div>

      {/* Verification Summary */}
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Evidence Integrity
          </h2>
          <Link 
            to="/evidence" 
            className="text-sm text-slate-600 hover:text-slate-900 flex items-center gap-1"
          >
            View all <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatBox label="Total Files" value={verificationStats.total} />
          <StatBox label="OK" value={verificationStats.ok} color="emerald" />
          <StatBox label="FAIL" value={verificationStats.fail} color={verificationStats.fail > 0 ? "red" : "slate"} />
          <StatBox label="MISSING" value={verificationStats.missing} color={verificationStats.missing > 0 ? "amber" : "slate"} />
        </div>
        {manifestStatus && (
          <p className="mt-4 text-xs text-slate-500 font-mono">
            Manifest: {manifestStatus.verified}/{manifestStatus.total_in_manifest} verified
            {manifestStatus.missing_files?.length > 0 && ` • ${manifestStatus.missing_files.length} missing`}
          </p>
        )}
      </div>

      {/* E3: A–E Cards */}
      <div>
        <h2 className="text-lg font-bold text-slate-900 mb-4" style={{ fontFamily: 'Manrope, sans-serif' }}>
          Evidence Categories (A–E)
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(CARD_CONFIG).map(([key, config]) => {
            const count = cardCounts[key];
            const colors = COLOR_CLASSES[config.color];
            const Icon = config.icon;
            
            return (
              <Link
                key={key}
                to={config.link}
                className={`group rounded-xl border-2 p-5 transition-all hover:shadow-md ${colors.bg} ${colors.border}`}
                data-testid={`card-${key}`}
              >
                <div className="flex items-start justify-between">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${colors.icon}`}>
                    <Icon className="w-6 h-6" />
                  </div>
                  <div className="flex items-center gap-1 text-slate-400 group-hover:text-slate-600 transition-colors">
                    <span className="text-sm">View</span>
                    <ArrowRight className="w-4 h-4" />
                  </div>
                </div>
                
                <div className="mt-4">
                  <div className="flex items-baseline gap-2">
                    <span className="text-sm font-medium text-slate-500">Section {key}</span>
                    <span className={`text-xs px-1.5 py-0.5 rounded font-mono ${colors.bg} ${colors.text} border ${colors.border}`}>
                      {config.prefix.replace('__', '')}
                    </span>
                  </div>
                  <h3 className="text-xl font-bold text-slate-900 mt-1" style={{ fontFamily: 'Manrope, sans-serif' }}>
                    {config.title}
                  </h3>
                  <p className="text-sm text-slate-600 mt-1">{config.description}</p>
                </div>
                
                <div className="mt-4 pt-4 border-t border-slate-200/50">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-500">
                      {config.checkPresence ? 'Present' : 'Files'}
                    </span>
                    <span className={`text-2xl font-bold ${colors.text}`} style={{ fontFamily: 'Manrope, sans-serif' }}>
                      {config.checkPresence ? (count > 0 ? '✓' : '—') : count}
                    </span>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Quick Links */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Link
          to="/evidence"
          className="bg-white border border-slate-200 rounded-xl p-5 hover:border-slate-300 hover:shadow-sm transition-all flex items-center gap-4 group"
          data-testid="quick-evidence"
        >
          <div className="w-12 h-12 bg-slate-100 rounded-xl flex items-center justify-center">
            <FileText className="w-6 h-6 text-slate-600" />
          </div>
          <div className="flex-1">
            <h3 className="font-bold text-slate-900">Evidence Browser</h3>
            <p className="text-sm text-slate-500">Browse all files with checksum verification</p>
          </div>
          <ArrowRight className="w-5 h-5 text-slate-300 group-hover:text-slate-600 transition-colors" />
        </Link>
        
        <Link
          to="/security"
          className="bg-white border border-slate-200 rounded-xl p-5 hover:border-slate-300 hover:shadow-sm transition-all flex items-center gap-4 group"
          data-testid="quick-security"
        >
          <div className="w-12 h-12 bg-slate-100 rounded-xl flex items-center justify-center">
            <Shield className="w-6 h-6 text-slate-600" />
          </div>
          <div className="flex-1">
            <h3 className="font-bold text-slate-900">Security & RLS</h3>
            <p className="text-sm text-slate-500">View security posture and RLS status</p>
          </div>
          <ArrowRight className="w-5 h-5 text-slate-300 group-hover:text-slate-600 transition-colors" />
        </Link>
      </div>

      {/* Standalone Notice */}
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-6" data-testid="standalone-notice">
        <p className="text-sm text-slate-600">
          <span className="font-medium text-slate-900">PetCare is a standalone project.</span>
          {" "}No portfolio/Crédito artifacts are included. This evidence repository is the authoritative source of truth.
        </p>
        <p className="text-xs text-slate-500 font-mono mt-2">
          Evidence root: {EVIDENCE_ROOT} • Baseline: {BASELINE_TAG}
        </p>
      </div>
    </div>
  );
}

function StatBox({ label, value, color = "slate" }) {
  const colorClasses = {
    emerald: "text-emerald-600",
    red: "text-red-600",
    amber: "text-amber-600",
    slate: "text-slate-900"
  };
  
  return (
    <div className="text-center p-4 bg-slate-50 rounded-lg">
      <p className="text-xs text-slate-500 uppercase tracking-wider">{label}</p>
      <p className={`text-3xl font-bold ${colorClasses[color]}`} style={{ fontFamily: 'Manrope, sans-serif' }}>
        {value}
      </p>
    </div>
  );
}
