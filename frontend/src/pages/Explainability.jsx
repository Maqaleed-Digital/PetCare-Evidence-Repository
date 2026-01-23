import { useEffect, useState } from "react";
import { Brain, Search, ChevronDown, CheckCircle, Link as LinkIcon } from "lucide-react";
import api from "../lib/api";

export default function Explainability() {
  const [runs, setRuns] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchRequestId, setSearchRequestId] = useState("");
  const [expandedRun, setExpandedRun] = useState(null);
  const [activeTab, setActiveTab] = useState("runs");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [runsRes, logsRes] = await Promise.all([
          api.getExplainabilityRuns({ request_id: searchRequestId }),
          api.getExplainabilityLogs({ request_id: searchRequestId })
        ]);
        setRuns(runsRes.data);
        setLogs(logsRes.data);
      } catch (err) {
        console.error("Error fetching explainability data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [searchRequestId]);

  const getLogsForRun = (runId) => logs.filter(log => log.run_id === runId);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64" data-testid="explainability-loading">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in" data-testid="explainability-page">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>
          AI Explainability
        </h1>
        <p className="mt-2 text-slate-500">
          TCF rule runs and explainability logs from the governance engine
        </p>
      </div>

      {/* Search */}
      <div className="bg-white border border-slate-200 rounded-xl p-4">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Filter by request ID..."
            value={searchRequestId}
            onChange={(e) => setSearchRequestId(e.target.value)}
            className="w-full pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-slate-900"
            data-testid="search-request-id"
          />
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-200">
        <div className="flex gap-6">
          <button
            onClick={() => setActiveTab("runs")}
            className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === "runs" 
                ? "border-slate-900 text-slate-900" 
                : "border-transparent text-slate-500 hover:text-slate-700"
            }`}
            data-testid="tab-runs"
          >
            Rule Runs ({runs.length})
          </button>
          <button
            onClick={() => setActiveTab("logs")}
            className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === "logs" 
                ? "border-slate-900 text-slate-900" 
                : "border-transparent text-slate-500 hover:text-slate-700"
            }`}
            data-testid="tab-logs"
          >
            Explainability Logs ({logs.length})
          </button>
        </div>
      </div>

      {/* Runs Tab */}
      {activeTab === "runs" && (
        <div className="space-y-4">
          {runs.length > 0 ? (
            runs.map((run, idx) => {
              const isExpanded = expandedRun === idx;
              const runLogs = getLogsForRun(run.id);

              return (
                <div 
                  key={run.id || idx}
                  className="bg-white border border-slate-200 rounded-xl overflow-hidden"
                  data-testid={`run-card-${idx}`}
                >
                  <button
                    onClick={() => setExpandedRun(isExpanded ? null : idx)}
                    className="w-full px-6 py-4 flex items-center gap-4 text-left hover:bg-slate-50 transition-colors"
                    data-testid={`run-toggle-${idx}`}
                  >
                    <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center">
                      <Brain className="w-5 h-5 text-slate-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3">
                        <span className="font-mono text-sm font-medium text-slate-900 truncate">
                          {run.request_id}
                        </span>
                        <span className="status-badge bg-slate-100 text-slate-700 border-slate-200">
                          {run.decision}
                        </span>
                      </div>
                      <div className="flex items-center gap-4 mt-1 text-xs text-slate-500">
                        <span>Score: <strong className="text-slate-700">{run.score}</strong></span>
                        <span>Band: <strong className="text-slate-700">{run.band}</strong></span>
                        <span>Engine: <strong className="text-slate-700">{run.engine_version}</strong></span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {runLogs.length > 0 && (
                        <span className="text-xs text-slate-500">
                          {runLogs.length} log{runLogs.length !== 1 ? 's' : ''}
                        </span>
                      )}
                      <ChevronDown className={`w-5 h-5 text-slate-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
                    </div>
                  </button>

                  {isExpanded && (
                    <div className="px-6 pb-4 border-t border-slate-200">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4">
                        <DetailItem label="Run ID" value={run.id} mono />
                        <DetailItem label="Tenant ID" value={run.tenant_id} mono />
                        <DetailItem label="Subject Type" value={run.subject_type} />
                        <DetailItem label="Subject ID" value={run.subject_id} mono />
                        <DetailItem label="Created At" value={run.created_at} />
                        <DetailItem label="Created By" value={run.created_by || "—"} mono />
                        <DetailItem label="Context" value={JSON.stringify(run.context_json || {})} mono />
                      </div>

                      {/* Linked Logs */}
                      {runLogs.length > 0 && (
                        <div className="mt-6">
                          <div className="flex items-center gap-2 mb-3">
                            <LinkIcon className="w-4 h-4 text-slate-400" />
                            <span className="text-sm font-medium text-slate-700">Linked Explainability Logs</span>
                          </div>
                          <div className="space-y-2">
                            {runLogs.map((log, logIdx) => (
                              <div 
                                key={log.id || logIdx}
                                className="bg-slate-50 border border-slate-200 rounded-lg p-4"
                              >
                                <div className="flex items-center gap-3 mb-2">
                                  <span className="font-mono text-sm font-medium text-slate-900">{log.rule_key}</span>
                                  <span className="text-xs text-slate-500">v{log.rule_version}</span>
                                  {log.hit && (
                                    <span className="status-badge bg-emerald-50 text-emerald-700 border-emerald-200">
                                      <CheckCircle className="w-3 h-3 mr-1" />
                                      HIT
                                    </span>
                                  )}
                                </div>
                                <p className="text-sm text-slate-600">{log.reason_text}</p>
                                <div className="flex items-center gap-4 mt-2 text-xs text-slate-500">
                                  <span>Code: <code className="bg-slate-200 px-1 rounded">{log.reason_code}</code></span>
                                  <span>Weight: {log.weight}</span>
                                  <span>Points: {log.points}</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })
          ) : (
            <EmptyState message="No rule runs found" />
          )}
        </div>
      )}

      {/* Logs Tab */}
      {activeTab === "logs" && (
        <div className="space-y-4">
          {logs.length > 0 ? (
            <div className="data-table">
              <table className="w-full">
                <thead>
                  <tr>
                    <th>Rule Key</th>
                    <th>Version</th>
                    <th>Hit</th>
                    <th>Reason Code</th>
                    <th>Reason Text</th>
                    <th>Points</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log, idx) => (
                    <tr key={log.id || idx} data-testid={`log-row-${idx}`}>
                      <td className="font-mono">{log.rule_key}</td>
                      <td>{log.rule_version}</td>
                      <td>
                        {log.hit ? (
                          <span className="status-badge bg-emerald-50 text-emerald-700 border-emerald-200">
                            <CheckCircle className="w-3 h-3 mr-1" />
                            Yes
                          </span>
                        ) : (
                          <span className="status-badge bg-slate-100 text-slate-600 border-slate-200">No</span>
                        )}
                      </td>
                      <td><code className="bg-slate-100 px-1.5 py-0.5 rounded text-xs">{log.reason_code}</code></td>
                      <td className="max-w-xs truncate">{log.reason_text}</td>
                      <td>{log.points}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState message="No explainability logs found" />
          )}
        </div>
      )}

      {/* Info */}
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-6">
        <h3 className="font-semibold text-slate-900 mb-2">About Explainability</h3>
        <p className="text-sm text-slate-600">
          The TCF (Trust & Compliance Framework) engine produces rule runs with linked explainability logs. 
          Each log entry explains why a rule triggered (or didn't), providing full auditability for governance decisions.
        </p>
      </div>
    </div>
  );
}

function DetailItem({ label, value, mono = false }) {
  return (
    <div>
      <p className="text-xs text-slate-500">{label}</p>
      <p className={`text-sm text-slate-900 truncate ${mono ? 'font-mono' : ''}`} title={value}>
        {value}
      </p>
    </div>
  );
}

function EmptyState({ message }) {
  return (
    <div className="text-center py-12 bg-white border border-slate-200 rounded-xl">
      <Brain className="w-12 h-12 text-slate-300 mx-auto" />
      <p className="mt-4 text-slate-500">{message}</p>
    </div>
  );
}
