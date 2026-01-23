import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { FolderArchive, FileText, CheckCircle, XCircle, ArrowRight } from "lucide-react";
import api from "../lib/api";

export default function Evidence() {
  const [packs, setPacks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPacks = async () => {
      try {
        const res = await api.getEvidencePacks();
        setPacks(res.data);
      } catch (err) {
        console.error("Error fetching packs:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchPacks();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64" data-testid="evidence-loading">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in" data-testid="evidence-page">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>
          Evidence Packs
        </h1>
        <p className="mt-2 text-slate-500">
          Browse and verify evidence files from the PetCare repository
        </p>
      </div>

      {/* Packs Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {packs.map((pack) => (
          <Link
            key={pack.id}
            to={`/evidence/${pack.id}`}
            className="governance-card cursor-pointer hover:border-slate-300 group"
            data-testid={`pack-card-${pack.id}`}
          >
            <div className="flex items-start justify-between">
              <div className="w-12 h-12 bg-slate-100 rounded-lg flex items-center justify-center">
                <FolderArchive className="w-6 h-6 text-slate-600" />
              </div>
              <ArrowRight className="w-5 h-5 text-slate-300 group-hover:text-slate-600 transition-colors" />
            </div>
            
            <div className="mt-4">
              <h3 className="font-semibold text-lg text-slate-900">{pack.name}</h3>
              <p className="text-sm text-slate-500 mt-1">{pack.path}</p>
            </div>

            <div className="mt-4 pt-4 border-t border-slate-100 grid grid-cols-3 gap-4">
              <div>
                <p className="text-xs text-slate-500">Files</p>
                <p className="text-lg font-semibold text-slate-900">{pack.file_count}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500">Verified</p>
                <p className="text-lg font-semibold text-emerald-600">{pack.verified_count}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500">Size</p>
                <p className="text-lg font-semibold text-slate-900">
                  {formatBytes(pack.total_size_bytes)}
                </p>
              </div>
            </div>

            {/* Verification Status */}
            <div className="mt-4">
              {pack.verified_count === pack.file_count ? (
                <div className="flex items-center gap-2 text-emerald-600">
                  <CheckCircle className="w-4 h-4" />
                  <span className="text-sm font-medium">All files verified</span>
                </div>
              ) : (
                <div className="flex items-center gap-2 text-amber-600">
                  <XCircle className="w-4 h-4" />
                  <span className="text-sm font-medium">
                    {pack.file_count - pack.verified_count} files unverified
                  </span>
                </div>
              )}
            </div>
          </Link>
        ))}

        {packs.length === 0 && (
          <div className="col-span-full text-center py-12">
            <FileText className="w-12 h-12 text-slate-300 mx-auto" />
            <p className="mt-4 text-slate-500">No evidence packs found</p>
          </div>
        )}
      </div>

      {/* Info Box */}
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-6">
        <h3 className="font-semibold text-slate-900 mb-2">About Evidence Integrity</h3>
        <p className="text-sm text-slate-600">
          Each file is verified against SHA256 checksums stored in the manifest file 
          (<code className="bg-slate-200 px-1.5 py-0.5 rounded text-xs">manifests/sprint-6-day-3_sha256.txt</code>). 
          Green checkmarks indicate the file matches its expected checksum.
        </p>
      </div>
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
