import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { 
  ArrowLeft, 
  FileText, 
  CheckCircle, 
  XCircle, 
  Download,
  Search,
  Filter
} from "lucide-react";
import api from "../lib/api";
import { toast } from "sonner";

export default function EvidencePack() {
  const { packId } = useParams();
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all"); // all, verified, unverified

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const res = await api.getPackFiles(packId);
        setFiles(res.data);
      } catch (err) {
        console.error("Error fetching files:", err);
        toast.error("Failed to load files");
      } finally {
        setLoading(false);
      }
    };
    fetchFiles();
  }, [packId]);

  const filteredFiles = files.filter(file => {
    const matchesSearch = file.name.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = 
      filter === "all" ||
      (filter === "verified" && file.verified === true) ||
      (filter === "unverified" && file.verified !== true);
    return matchesSearch && matchesFilter;
  });

  const verifiedCount = files.filter(f => f.verified === true).length;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64" data-testid="pack-loading">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900"></div>
      </div>
    );
  }

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
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>
            {packId.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </h1>
          <p className="mt-1 text-slate-500">
            {files.length} files • {verifiedCount} verified
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <span className={`status-badge ${verifiedCount === files.length ? 'green' : 'amber'}`}>
            {verifiedCount === files.length ? 'Fully Verified' : 'Partial Verification'}
          </span>
        </div>
      </div>

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
      <div className="data-table">
        <table className="w-full">
          <thead>
            <tr>
              <th>File Name</th>
              <th>Size</th>
              <th>SHA256 Status</th>
              <th className="text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredFiles.map((file) => (
              <tr key={file.name} data-testid={`file-row-${file.name}`}>
                <td>
                  <div className="flex items-center gap-3">
                    <FileText className="w-4 h-4 text-slate-400 flex-shrink-0" />
                    <span className="font-mono text-sm truncate max-w-xs">{file.name}</span>
                  </div>
                </td>
                <td className="text-slate-500">{formatBytes(file.size_bytes)}</td>
                <td>
                  {file.verified === true ? (
                    <span className="inline-flex items-center gap-1.5 text-emerald-600">
                      <CheckCircle className="w-4 h-4" />
                      <span className="text-sm font-medium">Verified</span>
                    </span>
                  ) : file.verified === false ? (
                    <span className="inline-flex items-center gap-1.5 text-red-600">
                      <XCircle className="w-4 h-4" />
                      <span className="text-sm font-medium">Failed</span>
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 text-slate-400">
                      <span className="w-4 h-4 rounded-full border-2 border-dashed border-slate-300" />
                      <span className="text-sm">No checksum</span>
                    </span>
                  )}
                </td>
                <td className="text-right">
                  <a
                    href={api.getPackFileUrl(packId, file.name)}
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
            {filteredFiles.length === 0 && (
              <tr>
                <td colSpan={4} className="text-center py-8 text-slate-500">
                  No files match your search
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Checksum Info */}
      {files.length > 0 && files[0].checksum && (
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-6">
          <h3 className="font-semibold text-slate-900 mb-2">SHA256 Verification</h3>
          <p className="text-sm text-slate-600 mb-3">
            Files are verified against checksums in <code className="bg-slate-200 px-1.5 py-0.5 rounded text-xs">manifests/sprint-6-day-3_sha256.txt</code>
          </p>
          <div className="font-mono text-xs text-slate-500 bg-white border border-slate-200 rounded p-3 overflow-x-auto">
            Example: {files[0].checksum?.substring(0, 32)}...
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
