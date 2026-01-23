import { useEffect, useState, useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import { 
  FileText, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Download,
  Search,
  Eye,
  X,
  Filter,
  ShieldCheck,
  Tag
} from "lucide-react";
import api, { getVerificationStatus, BASELINE_TAG, EVIDENCE_PACK_ID, EVIDENCE_ROOT } from "../lib/api";
import { toast } from "sonner";

// E1: Evidence Browser + Checksum Verification (UI0-G4)
// Status rules (deterministic, evidence-backed):
// OK: checksum exists + matches
// FAIL: checksum exists + mismatch  
// MISSING: checksum does not include path

const STATUS_CONFIG = {
  OK: { 
    icon: CheckCircle, 
    bg: "bg-emerald-50", 
    text: "text-emerald-700", 
    border: "border-emerald-200",
    label: "OK"
  },
  FAIL: { 
    icon: XCircle, 
    bg: "bg-red-50", 
    text: "text-red-700", 
    border: "border-red-200",
    label: "FAIL"
  },
  MISSING: { 
    icon: AlertTriangle, 
    bg: "bg-amber-50", 
    text: "text-amber-700", 
    border: "border-amber-200",
    label: "MISSING"
  },
};

export default function Evidence() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [files, setFiles] = useState({ evidence: [], addendum: [], trash: [] });
  const [manifestStatus, setManifestStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState(searchParams.get('search') || "");
  const [statusFilter, setStatusFilter] = useState(searchParams.get('status') || "all");
  const [addendumOnly, setAddendumOnly] = useState(searchParams.get('addendum') === 'true');
  const [prefixFilter, setPrefixFilter] = useState(searchParams.get('prefix') || "");
  const [previewFile, setPreviewFile] = useState(null);
  const [previewContent, setPreviewContent] = useState("");
  const [previewLoading, setPreviewLoading] = useState(false);

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const res = await api.getPackFiles(EVIDENCE_PACK_ID);
        setFiles({
          evidence: res.data.evidence || [],
          addendum: res.data.addendum || [],
          trash: res.data.trash || []
        });
        setManifestStatus(res.data.manifest_status);
      } catch (err) {
        console.error("Error fetching files:", err);
        toast.error("Failed to load evidence files");
      } finally {
        setLoading(false);
      }
    };
    fetchFiles();
  }, []);

  // Combine all files with status
  const allFiles = useMemo(() => {
    const combined = [
      ...files.evidence.map(f => ({ ...f, status: getVerificationStatus(f) })),
      ...files.addendum.map(f => ({ ...f, status: getVerificationStatus(f) }))
    ];
    return combined;
  }, [files]);

  // Apply filters
  const filteredFiles = useMemo(() => {
    return allFiles.filter(file => {
      // Search filter
      if (search && !file.path.toLowerCase().includes(search.toLowerCase())) {
        return false;
      }
      // Status filter
      if (statusFilter !== "all" && file.status !== statusFilter) {
        return false;
      }
      // Addendum only toggle
      if (addendumOnly && !file.is_addendum) {
        return false;
      }
      // Prefix filter (for dashboard deep links)
      if (prefixFilter && !file.name.startsWith(prefixFilter)) {
        return false;
      }
      return true;
    });
  }, [allFiles, search, statusFilter, addendumOnly, prefixFilter]);

  // Count by status
  const statusCounts = useMemo(() => {
    const counts = { OK: 0, FAIL: 0, MISSING: 0, all: allFiles.length };
    allFiles.forEach(f => {
      counts[f.status] = (counts[f.status] || 0) + 1;
    });
    return counts;
  }, [allFiles]);

  // Preview file content
  const handlePreview = async (file) => {
    if (!isPreviewable(file)) return;
    
    setPreviewFile(file);
    setPreviewLoading(true);
    try {
      const filePath = file.is_addendum ? `addendum/${file.name}` : file.name;
      const res = await api.getPackFile(EVIDENCE_PACK_ID, filePath);
      setPreviewContent(typeof res.data === 'string' ? res.data : JSON.stringify(res.data, null, 2));
    } catch (err) {
      setPreviewContent("Error loading file preview");
    } finally {
      setPreviewLoading(false);
    }
  };

  const isPreviewable = (file) => {
    const ext = file.name.split('.').pop().toLowerCase();
    return ['txt', 'csv', 'json', 'jsonl', 'md'].includes(ext) && file.size_bytes < 50000;
  };

  // Update URL params
  const updateFilter = (key, value) => {
    const params = new URLSearchParams(searchParams);
    if (value && value !== 'all' && value !== '') {
      params.set(key, value);
    } else {
      params.delete(key);
    }
    setSearchParams(params);
    
    if (key === 'search') setSearch(value);
    if (key === 'status') setStatusFilter(value);
    if (key === 'addendum') setAddendumOnly(value === 'true');
    if (key === 'prefix') setPrefixFilter(value);
  };

  const clearFilters = () => {
    setSearch("");
    setStatusFilter("all");
    setAddendumOnly(false);
    setPrefixFilter("");
    setSearchParams({});
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64" data-testid="evidence-loading">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in" data-testid="evidence-page">
      {/* Header with Baseline Tag */}
      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Evidence Browser
          </h1>
          <p className="mt-1 text-slate-500 font-mono text-sm">{EVIDENCE_ROOT}</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-2 bg-slate-100 rounded-lg">
          <Tag className="w-4 h-4 text-slate-500" />
          <span className="text-sm font-mono text-slate-700">{BASELINE_TAG}</span>
        </div>
      </div>

      {/* Manifest Status Banner */}
      {manifestStatus && (
        <div className={`rounded-xl p-4 border-2 ${manifestStatus.all_ok ? 'bg-emerald-50 border-emerald-200' : 'bg-amber-50 border-amber-200'}`}>
          <div className="flex items-center gap-3">
            {manifestStatus.all_ok ? (
              <ShieldCheck className="w-6 h-6 text-emerald-600" />
            ) : (
              <AlertTriangle className="w-6 h-6 text-amber-600" />
            )}
            <div>
              <p className={`font-bold ${manifestStatus.all_ok ? 'text-emerald-700' : 'text-amber-700'}`}>
                {manifestStatus.all_ok ? 'ALL OK' : 'Integrity Check: Partial'}
              </p>
              <p className={`text-sm ${manifestStatus.all_ok ? 'text-emerald-600' : 'text-amber-600'}`}>
                {manifestStatus.verified}/{manifestStatus.total_in_manifest} verified • 
                {manifestStatus.failed} failed • 
                {manifestStatus.missing_files?.length || 0} missing from manifest
              </p>
            </div>
          </div>
          {manifestStatus.missing_files?.length > 0 && (
            <div className="mt-3 text-xs text-amber-700">
              <span className="font-medium">Missing paths: </span>
              {manifestStatus.missing_files.join(', ')}
            </div>
          )}
        </div>
      )}

      {/* Status Filter Chips - E1 requirement */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-sm text-slate-500 mr-2">Filter:</span>
        {['all', 'OK', 'FAIL', 'MISSING'].map(status => {
          const isActive = statusFilter === status;
          const count = status === 'all' ? statusCounts.all : statusCounts[status];
          const config = STATUS_CONFIG[status];
          
          return (
            <button
              key={status}
              onClick={() => updateFilter('status', status)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all flex items-center gap-1.5 ${
                isActive 
                  ? status === 'all' 
                    ? 'bg-slate-900 text-white' 
                    : `${config?.bg} ${config?.text} ${config?.border} border`
                  : 'bg-white border border-slate-200 text-slate-600 hover:border-slate-300'
              }`}
              data-testid={`filter-${status.toLowerCase()}`}
            >
              {config?.icon && <config.icon className="w-3.5 h-3.5" />}
              {status === 'all' ? 'All' : status}
              <span className="ml-1 text-xs opacity-70">({count})</span>
            </button>
          );
        })}

        {/* Addendum Only Toggle - E1 requirement */}
        <label className="flex items-center gap-2 ml-4 cursor-pointer">
          <input
            type="checkbox"
            checked={addendumOnly}
            onChange={(e) => updateFilter('addendum', e.target.checked ? 'true' : '')}
            className="w-4 h-4 rounded border-slate-300 text-slate-900 focus:ring-slate-900"
            data-testid="addendum-toggle"
          />
          <span className="text-sm text-slate-600">Addendum only</span>
        </label>
      </div>

      {/* Search + Prefix Filter */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search by path..."
            value={search}
            onChange={(e) => updateFilter('search', e.target.value)}
            className="w-full pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-slate-900"
            data-testid="file-search"
          />
        </div>
        {prefixFilter && (
          <div className="flex items-center gap-2 px-3 py-2 bg-violet-50 border border-violet-200 rounded-lg">
            <Filter className="w-4 h-4 text-violet-600" />
            <span className="text-sm text-violet-700">Prefix: {prefixFilter}</span>
            <button 
              onClick={() => updateFilter('prefix', '')}
              className="p-0.5 hover:bg-violet-100 rounded"
            >
              <X className="w-3 h-3 text-violet-600" />
            </button>
          </div>
        )}
        {(search || statusFilter !== 'all' || addendumOnly || prefixFilter) && (
          <button
            onClick={clearFilters}
            className="px-3 py-2 text-sm text-slate-600 hover:text-slate-900 flex items-center gap-1"
            data-testid="clear-filters"
          >
            <X className="w-4 h-4" /> Clear
          </button>
        )}
      </div>

      {/* Results Count */}
      <p className="text-sm text-slate-500">
        Showing {filteredFiles.length} of {allFiles.length} files
      </p>

      {/* Files Table */}
      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Status</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Path</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Size</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">SHA256</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filteredFiles.map((file, idx) => {
              const config = STATUS_CONFIG[file.status];
              const Icon = config.icon;
              
              return (
                <tr key={file.path} className="hover:bg-slate-50" data-testid={`file-row-${idx}`}>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium ${config.bg} ${config.text} ${config.border} border`}>
                      <Icon className="w-3 h-3" />
                      {config.label}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <FileText className={`w-4 h-4 ${file.is_addendum ? 'text-violet-400' : 'text-slate-400'}`} />
                      <span className="font-mono text-sm text-slate-700 truncate max-w-md" title={file.path}>
                        {file.path}
                      </span>
                      {file.is_addendum && (
                        <span className="px-1.5 py-0.5 bg-violet-100 text-violet-700 text-xs rounded">addendum</span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-500 whitespace-nowrap">
                    {formatBytes(file.size_bytes)}
                  </td>
                  <td className="px-4 py-3">
                    {file.checksum ? (
                      <span className="font-mono text-xs text-slate-500" title={file.checksum}>
                        {file.checksum.substring(0, 16)}...
                      </span>
                    ) : (
                      <span className="text-xs text-slate-400 italic">not in manifest</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      {isPreviewable(file) && (
                        <button
                          onClick={() => handlePreview(file)}
                          className="p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded"
                          title="Preview"
                          data-testid={`preview-${file.name}`}
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                      )}
                      <a
                        href={api.getPackFileUrl(EVIDENCE_PACK_ID, file.is_addendum ? `addendum/${file.name}` : file.name)}
                        download={file.name}
                        className="p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded"
                        title="Download"
                        data-testid={`download-${file.name}`}
                      >
                        <Download className="w-4 h-4" />
                      </a>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {filteredFiles.length === 0 && (
          <div className="text-center py-12">
            <FileText className="w-12 h-12 text-slate-300 mx-auto" />
            <p className="mt-4 text-slate-500">No files match your filters</p>
          </div>
        )}
      </div>

      {/* Preview Modal */}
      {previewFile && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[80vh] overflow-hidden flex flex-col">
            <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-slate-500" />
                <span className="font-mono text-sm text-slate-700">{previewFile.name}</span>
                <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_CONFIG[previewFile.status].bg} ${STATUS_CONFIG[previewFile.status].text}`}>
                  {STATUS_CONFIG[previewFile.status].label}
                </span>
              </div>
              <button
                onClick={() => setPreviewFile(null)}
                className="p-1 hover:bg-slate-100 rounded"
              >
                <X className="w-5 h-5 text-slate-500" />
              </button>
            </div>
            <div className="flex-1 overflow-auto p-4 bg-slate-50">
              {previewLoading ? (
                <div className="flex items-center justify-center h-32">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-slate-900"></div>
                </div>
              ) : (
                <pre className="font-mono text-xs text-slate-700 whitespace-pre-wrap">{previewContent}</pre>
              )}
            </div>
          </div>
        </div>
      )}
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
