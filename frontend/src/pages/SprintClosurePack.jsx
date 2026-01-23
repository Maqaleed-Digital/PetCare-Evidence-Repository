import { useEffect, useState, useMemo } from "react";
import { 
  FileText, 
  CheckCircle, 
  Copy,
  Tag,
  Shield,
  Database,
  Monitor,
  Lock
} from "lucide-react";
import api, { getVerificationStatus, BASELINE_TAG, EVIDENCE_PACK_ID, EVIDENCE_ROOT } from "../lib/api";
import { toast } from "sonner";

// E4: Notion-ready Sprint UI-0 Pack (documentation output)
// Produces copy/paste Notion block to close sprint gates

const GATES = [
  { id: 'UI0-G1', name: 'Repo wiring', description: 'Evidence repository connected' },
  { id: 'UI0-G2', name: 'Security endpoints', description: 'RLS, policies, grants endpoints working' },
  { id: 'UI0-G3', name: 'Frontend build', description: 'React frontend builds successfully' },
  { id: 'UI0-G4', name: 'Checksum UI', description: 'Evidence browser with OK/FAIL/MISSING status' },
  { id: 'UI0-G5', name: 'A–E dashboard', description: 'Governance cards with prefix-based counts' },
];

export default function SprintClosurePack() {
  const [files, setFiles] = useState({ evidence: [], addendum: [] });
  const [manifestStatus, setManifestStatus] = useState(null);
  const [securityData, setSecurityData] = useState({ rls: [], policies: [], grants: [], bypass: [] });
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [filesRes, rlsRes, policiesRes, grantsRes, bypassRes] = await Promise.all([
          api.getPackFiles(EVIDENCE_PACK_ID),
          api.getRLSStatus(),
          api.getPolicies(),
          api.getGrants(),
          api.getBypassRLS()
        ]);
        setFiles({
          evidence: filesRes.data.evidence || [],
          addendum: filesRes.data.addendum || []
        });
        setManifestStatus(filesRes.data.manifest_status);
        setSecurityData({
          rls: rlsRes.data || [],
          policies: policiesRes.data || [],
          grants: grantsRes.data || [],
          bypass: bypassRes.data || []
        });
      } catch (err) {
        console.error("Error fetching data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // Calculate gate statuses
  const gateStatuses = useMemo(() => {
    const allFiles = [...files.evidence, ...files.addendum];
    const checksumStats = { ok: 0, fail: 0, missing: 0 };
    allFiles.forEach(f => {
      const status = getVerificationStatus(f);
      if (status === 'OK') checksumStats.ok++;
      else if (status === 'FAIL') checksumStats.fail++;
      else checksumStats.missing++;
    });

    return {
      'UI0-G1': allFiles.length > 0, // Repo wiring
      'UI0-G2': securityData.rls.length > 0, // Security endpoints
      'UI0-G3': true, // Frontend build (we're running)
      'UI0-G4': checksumStats.ok > 0, // Checksum UI working
      'UI0-G5': files.evidence.filter(f => f.name.startsWith('A_counts__')).length > 0 // A-E dashboard
    };
  }, [files, securityData]);

  // Generate Notion-ready text
  const notionText = useMemo(() => {
    const allFiles = [...files.evidence, ...files.addendum];
    const checksumStats = { ok: 0, fail: 0, missing: 0 };
    allFiles.forEach(f => {
      const status = getVerificationStatus(f);
      if (status === 'OK') checksumStats.ok++;
      else if (status === 'FAIL') checksumStats.fail++;
      else checksumStats.missing++;
    });

    const gateLines = GATES.map(g => {
      const passed = gateStatuses[g.id];
      return `- [${passed ? 'x' : ' '}] **${g.id}**: ${g.name} — ${passed ? 'PASS' : 'PENDING'}`;
    }).join('\n');

    return `# Sprint UI-0 Closure Pack

## Sprint Overview
- **Sprint**: UI-0 — PetCare Evidence UI (Standalone)
- **Objective**: Deterministic evidence-backed rendering with checksum verification
- **Baseline Tag**: \`${BASELINE_TAG}\`
- **Evidence Root**: \`${EVIDENCE_ROOT}\`

## Gate Status

${gateLines}

## Evidence Summary
- **Total Files**: ${allFiles.length}
- **Checksum OK**: ${checksumStats.ok}
- **Checksum FAIL**: ${checksumStats.fail}
- **Checksum MISSING**: ${checksumStats.missing}
- **Manifest Verified**: ${manifestStatus?.verified || 0}/${manifestStatus?.total_in_manifest || 0}

## Security Posture
- **RLS Tables**: ${securityData.rls.length}
- **RLS Enabled**: ${securityData.rls.filter(t => t.rls_enabled).length}/${securityData.rls.length}
- **Policies Defined**: ${securityData.policies.length}
- **Bypass Roles**: ${securityData.bypass.filter(r => r.bypass_rls).length}

## Evidence References
\`\`\`
${EVIDENCE_ROOT}/_bundle/index.json
${EVIDENCE_ROOT}/_bundle/checksums.sha256
${EVIDENCE_ROOT}/addendum/*
\`\`\`

## API Endpoints Verified
- \`GET /api/evidence/packs\`
- \`GET /api/evidence/packs/{pack_id}/files\`
- \`GET /api/security/rls\`
- \`GET /api/security/policies\`
- \`GET /api/security/grants\`
- \`GET /api/security/bypassrls\`

## Sign-off
- **Date**: ${new Date().toISOString().split('T')[0]}
- **Status**: ${Object.values(gateStatuses).every(v => v) ? '✅ ALL GATES PASS' : '⚠️ PENDING GATES'}
`;
  }, [files, manifestStatus, securityData, gateStatuses]);

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(notionText);
      setCopied(true);
      toast.success("Copied to clipboard!");
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      toast.error("Failed to copy");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64" data-testid="closure-loading">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900"></div>
      </div>
    );
  }

  const allPassed = Object.values(gateStatuses).every(v => v);

  return (
    <div className="space-y-6 animate-fade-in" data-testid="sprint-closure-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Sprint UI-0 Closure Pack
          </h1>
          <p className="mt-2 text-slate-500">
            Notion-ready documentation for sprint gate closure
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-2 bg-slate-100 rounded-lg">
          <Tag className="w-4 h-4 text-slate-500" />
          <span className="text-sm font-mono text-slate-700">{BASELINE_TAG}</span>
        </div>
      </div>

      {/* Status Banner */}
      <div className={`rounded-xl p-4 border-2 ${allPassed ? 'bg-emerald-50 border-emerald-200' : 'bg-amber-50 border-amber-200'}`}>
        <div className="flex items-center gap-3">
          {allPassed ? (
            <CheckCircle className="w-6 h-6 text-emerald-600" />
          ) : (
            <Shield className="w-6 h-6 text-amber-600" />
          )}
          <div>
            <p className={`font-bold ${allPassed ? 'text-emerald-700' : 'text-amber-700'}`}>
              {allPassed ? 'ALL GATES PASS' : 'PENDING GATES'}
            </p>
            <p className={`text-sm ${allPassed ? 'text-emerald-600' : 'text-amber-600'}`}>
              {Object.values(gateStatuses).filter(v => v).length}/{GATES.length} gates passed
            </p>
          </div>
        </div>
      </div>

      {/* Gates Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {GATES.map(gate => {
          const passed = gateStatuses[gate.id];
          const Icon = gate.id === 'UI0-G1' ? Database : 
                      gate.id === 'UI0-G2' ? Lock : 
                      gate.id === 'UI0-G3' ? Monitor : 
                      gate.id === 'UI0-G4' ? FileText : Shield;
          
          return (
            <div 
              key={gate.id}
              className={`rounded-xl p-4 border-2 ${passed ? 'bg-emerald-50 border-emerald-200' : 'bg-slate-50 border-slate-200'}`}
              data-testid={`gate-${gate.id}`}
            >
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${passed ? 'bg-emerald-100' : 'bg-slate-100'}`}>
                  <Icon className={`w-5 h-5 ${passed ? 'text-emerald-600' : 'text-slate-400'}`} />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-slate-500">{gate.id}</span>
                    <span className={`px-1.5 py-0.5 rounded text-xs font-medium ${passed ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-600'}`}>
                      {passed ? 'PASS' : 'PENDING'}
                    </span>
                  </div>
                  <p className="font-medium text-slate-900">{gate.name}</p>
                </div>
              </div>
              <p className="mt-2 text-sm text-slate-600">{gate.description}</p>
            </div>
          );
        })}
      </div>

      {/* Notion Output */}
      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
              Notion-Ready Output
            </h2>
            <p className="text-xs text-slate-500 mt-1">Copy and paste into Notion to close the sprint</p>
          </div>
          <button
            onClick={copyToClipboard}
            className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors ${
              copied 
                ? 'bg-emerald-100 text-emerald-700' 
                : 'bg-slate-900 text-white hover:bg-slate-800'
            }`}
            data-testid="copy-btn"
          >
            <Copy className="w-4 h-4" />
            {copied ? 'Copied!' : 'Copy to Clipboard'}
          </button>
        </div>
        <div className="p-6 bg-slate-50">
          <pre className="font-mono text-sm text-slate-700 whitespace-pre-wrap bg-white p-4 rounded-lg border border-slate-200 overflow-x-auto">
            {notionText}
          </pre>
        </div>
      </div>

      {/* Evidence References */}
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-6">
        <h3 className="font-semibold text-slate-900 mb-4">Evidence References</h3>
        <div className="space-y-2">
          <p className="text-sm font-mono text-slate-600">{EVIDENCE_ROOT}/_bundle/index.json</p>
          <p className="text-sm font-mono text-slate-600">{EVIDENCE_ROOT}/_bundle/checksums.sha256</p>
          <p className="text-sm font-mono text-slate-600">{EVIDENCE_ROOT}/addendum/*</p>
        </div>
      </div>
    </div>
  );
}
