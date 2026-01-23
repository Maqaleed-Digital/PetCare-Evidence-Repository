import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { 
  ArrowLeft, 
  FileText, 
  CheckCircle, 
  XCircle, 
  Download,
  Search,
  Filter,
  ShieldCheck,
  AlertTriangle,
  Plus,
  Trash2,
  FileCode
} from "lucide-react";
import api from "../lib/api";
import { toast } from "sonner";

export default function EvidencePack() {
  const { packId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all"); // all, verified, unverified, addendum
  const [activeTab, setActiveTab] = useState("evidence");

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const res = await api.getPackFiles(packId);
        setData(res.data);
      } catch (err) {
        console.error("Error fetching files:", err);
        toast.error("Failed to load files");
      } finally {
        setLoading(false);
      }
    };
    fetchFiles();
  }, [packId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64" data-testid="pack-loading">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900"></div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-12">
        <FileText className="w-12 h-12 text-slate-300 mx-auto" />
        <p className="mt-4 text-slate-500">Failed to load evidence pack</p>
      </div>
    );
  }

  const { evidence = [], addendum = [], trash = [], manifest_status = {} } = data;
  const allFiles = [...evidence, ...addendum];
  
  const filteredFiles = allFiles.filter(file => {
    const matchesSearch = file.name.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = 
      filter === "all" ||
      (filter === "verified" && file.verified === true) ||
      (filter === "unverified" && file.verified !== true && !file.is_addendum) ||
      (filter === "addendum" && file.is_addendum);
    return matchesSearch && matchesFilter;
  });

  const verifiedCount = evidence.filter(f => f.verified === true).length;
  const allOk = manifest_status.all_ok;

  return (
    <div className="space-y-6 animate-fade-in" data-testid="evidence-pack-page">
      {/* Back Link */}
      <Link 
        to="/evidence" 
        className="inline-flex items-center gap-2 text-sm text-slate-600 hover:text-slate-900"
        data-testid="back-to-evidence"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Evidence Packs
      </Link>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>
            {packId.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
          </h1>
          <p className="mt-1 text-slate-500 font-mono text-sm">
            pilot/{packId.replace(/-/g, '/')}
          </p>
          <p className="mt-2 text-slate-500">
            {evidence.length} evidence files • {verifiedCount} verified
            {addendum.length > 0 && ` • ${addendum.length} addendum files`}
          </p>
        </div>
        
        {/* Manifest Status Badge */}
        <div className="flex-shrink-0">
          {allOk ? (
            <div className="flex items-center gap-2 px-4 py-2 bg-emerald-50 border-2 border-emerald-200 rounded-xl">
              <ShieldCheck className="w-5 h-5 text-emerald-600" />
              <div>
                <span className="text-lg font-bold text-emerald-700">ALL OK</span>
                <p className="text-xs text-emerald-600">{manifest_status.verified}/{manifest_status.total_in_manifest} checksums verified</p>
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-2 px-4 py-2 bg-amber-50 border-2 border-amber-200 rounded-xl">
              <AlertTriangle className="w-5 h-5 text-amber-600" />
              <div>
                <span className="text-lg font-bold text-amber-700">PARTIAL</span>
                <p className="text-xs text-amber-600">{manifest_status.status_message}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-200">
        <div className="flex gap-6">
          <TabButton 
            active={activeTab === "evidence"} 
            onClick={() => setActiveTab("evidence")}
            icon={FileText}
            label={`Evidence (${evidence.length})`}
            testId="tab-evidence"
          />
          {addendum.length > 0 && (
            <TabButton 
              active={activeTab === "addendum"} 
              onClick={() => setActiveTab("addendum")}
              icon={Plus}
              label={`Addendum (${addendum.length})`}
              testId="tab-addendum"
            />
          )}
          {trash.length > 0 && (
            <TabButton 
              active={activeTab === "trash"} 
              onClick={() => setActiveTab("trash")}
              icon={Trash2}
              label={`Trash (${trash.length})`}
              testId="tab-trash"
            />
          )}
        </div>
      </div>

      {/* Evidence Tab */}
      {activeTab === "evidence" && (
        <>
          {/* Filters */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search files..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent"
                data-testid="file-search"
              />
            </div>
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-slate-400" />
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-slate-900"
                data-testid="file-filter"
              >
                <option value="all">All Files</option>
                <option value="verified">Verified Only</option>
                <option value="unverified">Unverified Only</option>
              </select>
            </div>
          </div>

          {/* Files Table */}
          <FileTable 
            files={evidence.filter(f => 
              f.name.toLowerCase().includes(search.toLowerCase()) &&
              (filter === "all" || 
               (filter === "verified" && f.verified === true) ||
               (filter === "unverified" && f.verified !== true))
            )} 
            packId={packId}
            showChecksum={true}
          />
        </>
      )}

      {/* Addendum Tab */}
      {activeTab === "addendum" && (
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <FileCode className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <p className="font-medium text-blue-900">Addendum Files</p>
                <p className="text-sm text-blue-700 mt-1">
                  These files supplement the main evidence pack with additional data. 
                  They are not included in the original manifest checksum verification.
                </p>
              </div>
            </div>
          </div>
          <FileTable files={addendum} packId={packId} showChecksum={false} isAddendum={true} />
        </div>
      )}

      {/* Trash Tab */}
      {activeTab === "trash" && (
        <div className="space-y-4">
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <Trash2 className="w-5 h-5 text-slate-500 mt-0.5" />
              <div>
                <p className="font-medium text-slate-700">Non-authoritative Files</p>
                <p className="text-sm text-slate-600 mt-1">
                  Files in _trash/ are excluded from analysis but preserved for reference.
                </p>
              </div>
            </div>
          </div>
          <FileTable files={trash} packId={packId} showChecksum={true} isTrash={true} />
        </div>
      )}

      {/* Manifest Summary */}
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <h3 className="font-semibold text-slate-900 mb-4">Manifest Verification Summary</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <StatBox label="Total in Manifest" value={manifest_status.total_in_manifest || 0} />
          <StatBox label="Verified" value={manifest_status.verified || 0} color="emerald" />
          <StatBox label="Failed" value={manifest_status.failed || 0} color={manifest_status.failed > 0 ? "red" : "slate"} />
          <StatBox label="Missing" value={manifest_status.missing_files?.length || 0} color={manifest_status.missing_files?.length > 0 ? "amber" : "slate"} />
          <StatBox label="Extra Files" value={manifest_status.extra_files?.length || 0} color="slate" />
        </div>
        
        {manifest_status.missing_files?.length > 0 && (
          <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
            <p className="text-sm font-medium text-amber-800">Missing files:</p>
            <div className="flex flex-wrap gap-2 mt-2">
              {manifest_status.missing_files.map(f => (
                <code key={f} className="text-xs bg-amber-100 text-amber-800 px-2 py-1 rounded">{f}</code>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function TabButton({ active, onClick, icon: Icon, label, testId }) {
  return (
    <button
      onClick={onClick}
      className={`pb-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
        active 
          ? "border-slate-900 text-slate-900" 
          : "border-transparent text-slate-500 hover:text-slate-700"
      }`}
      data-testid={testId}
    >
      <Icon className="w-4 h-4" />
      {label}
    </button>
  );
}

function FileTable({ files, packId, showChecksum = true, isAddendum = false, isTrash = false }) {
  if (files.length === 0) {
    return (
      <div className="text-center py-8 bg-slate-50 border border-slate-200 rounded-xl">
        <FileText className="w-8 h-8 text-slate-300 mx-auto" />
        <p className="mt-2 text-slate-500">No files found</p>
      </div>
    );
  }

  return (
    <div className="data-table">
      <table className="w-full">
        <thead>
          <tr>
            <th>File Name</th>
            <th>Size</th>
            {showChecksum && <th>SHA256 Status</th>}
            <th className="text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          {files.map((file) => (
            <tr key={file.name} data-testid={`file-row-${file.name}`}>
              <td>
                <div className="flex items-center gap-3">
                  <FileText className={`w-4 h-4 flex-shrink-0 ${
                    isAddendum ? 'text-blue-400' : isTrash ? 'text-slate-300' : 'text-slate-400'
                  }`} />
                  <span className="font-mono text-sm truncate max-w-xs">{file.name}</span>
                  {file.category === "manifest" && (
                    <span className="px-1.5 py-0.5 bg-slate-100 text-slate-500 text-xs rounded">manifest</span>
                  )}
                </div>
              </td>
              <td className="text-slate-500">{formatBytes(file.size_bytes)}</td>
              {showChecksum && (
                <td>
                  {file.verified === true ? (
                    <span className="inline-flex items-center gap-1.5 text-emerald-600">
                      <CheckCircle className="w-4 h-4" />
                      <span className="text-sm font-medium">Verified</span>
                    </span>
                  ) : file.verified === false ? (
                    <span className="inline-flex items-center gap-1.5 text-red-600">
                      <XCircle className="w-4 h-4" />
                      <span className="text-sm font-medium">Mismatch</span>
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 text-slate-400">
                      <span className="w-4 h-4 rounded-full border-2 border-dashed border-slate-300" />
                      <span className="text-sm">No checksum</span>
                    </span>
                  )}
                </td>
              )}
              <td className="text-right">
                <a
                  href={api.getPackFileUrl(packId, isAddendum ? `addendum/${file.name}` : isTrash ? `_trash/${file.name}` : file.name)}
                  download
                  className="inline-flex items-center gap-1 text-sm text-slate-600 hover:text-slate-900"
                  data-testid={`download-${file.name}`}
                >
                  <Download className="w-4 h-4" />
                  Download
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function StatBox({ label, value, color = "slate" }) {
  const colors = {
    emerald: "text-emerald-600",
    red: "text-red-600",
    amber: "text-amber-600",
    slate: "text-slate-900"
  };
  
  return (
    <div className="text-center p-3 bg-slate-50 rounded-lg">
      <p className="text-xs text-slate-500 uppercase tracking-wider">{label}</p>
      <p className={`text-2xl font-bold ${colors[color]}`} style={{ fontFamily: 'Manrope, sans-serif' }}>
        {value}
      </p>
    </div>
  );
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}
