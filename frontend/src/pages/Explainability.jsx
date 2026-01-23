import { useEffect, useState } from "react";
import { 
  Brain, 
  Search, 
  ChevronDown, 
  CheckCircle, 
  XCircle,
  Link as LinkIcon,
  Clock,
  Target,
  Zap,
  BarChart3,
  FileText,
  ArrowRight,
  X,
  TrendingUp,
  Hash
} from "lucide-react";
import api from "../lib/api";

export default function Explainability() {
  const [runs, setRuns] = useState([]);
  const [logs, setLogs] = useState([]);
  const [distributions, setDistributions] = useState(null);
  const [requestIds, setRequestIds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchRequestId, setSearchRequestId] = useState("");
  const [activeTab, setActiveTab] = useState("overview");
  const [drilldown, setDrilldown] = useState(null);
  const [drilldownLoading, setDrilldownLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [runsRes, logsRes, distRes, reqIdsRes] = await Promise.all([
          api.getExplainabilityRuns({ request_id: searchRequestId }),
          api.getExplainabilityLogs({ request_id: searchRequestId }),
          api.getExplainabilityDistributions(),
          api.getRequestIds()
        ]);
        setRuns(runsRes.data);
        setLogs(logsRes.data);
        setDistributions(distRes.data);
        setRequestIds(reqIdsRes.data);
      } catch (err) {
        console.error("Error fetching explainability data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [searchRequestId]);

  const openRequestDrilldown = async (requestId) => {
    setDrilldownLoading(true);
    try {
      const res = await api.getRequestDrilldown(requestId);
      setDrilldown(res.data);
    } catch (err) {
      console.error("Error fetching request drilldown:", err);
    } finally {
      setDrilldownLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64" data-testid="explainability-loading">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900"></div>
      </div>
    );
  }

  const summary = distributions?.summary || {};

  return (
    <div className="space-y-6 animate-fade-in" data-testid="explainability-page">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>
          Explainability Explorer
        </h1>
        <p className="mt-2 text-slate-500">
          TCF rule runs, explainability logs, and reason code analysis
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <StatCard icon={Target} label="Total Runs" value={summary.total_runs || 0} color="violet" />
        <StatCard icon={FileText} label="Total Logs" value={summary.total_logs || 0} color="blue" />
        <StatCard icon={Zap} label="Unique Rules" value={summary.unique_rules || 0} color="emerald" />
        <StatCard icon={Hash} label="Reason Codes" value={summary.unique_reason_codes || 0} color="amber" />
        <StatCard 
          icon={TrendingUp} 
          label="Hit Rate" 
          value={`${(summary.hit_rate || 0).toFixed(0)}%`} 
          color="sky" 
        />
      </div>

      {/* Distribution Charts */}
      {distributions && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Decision Distribution */}
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-violet-500" />
              Decision Distribution
            </h3>
            {Object.keys(distributions.decisions || {}).length > 0 ? (
              <div className="space-y-3">
                {Object.entries(distributions.decisions).map(([decision, count]) => (
                  <DistributionBar 
                    key={decision} 
                    label={decision} 
                    value={count} 
                    total={summary.total_runs || 1}
                    color="violet"
                  />
                ))}
              </div>
            ) : (
              <EmptyChart message="No decisions recorded yet" />
            )}
          </div>

          {/* Band Distribution */}
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-blue-500" />
              Band Distribution
            </h3>
            {Object.keys(distributions.bands || {}).length > 0 ? (
              <div className="space-y-3">
                {Object.entries(distributions.bands).map(([band, count]) => (
                  <DistributionBar 
                    key={band} 
                    label={band} 
                    value={count} 
                    total={summary.total_runs || 1}
                    color="blue"
                  />
                ))}
              </div>
            ) : (
              <EmptyChart message="No bands recorded yet" />
            )}
          </div>

          {/* Reason Code Distribution */}
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-emerald-500" />
              Reason Code Distribution
            </h3>
            {Object.keys(distributions.reason_codes || {}).length > 0 ? (
              <div className="space-y-3">
                {Object.entries(distributions.reason_codes).map(([code, count]) => (
                  <DistributionBar 
                    key={code} 
                    label={code} 
                    value={count} 
                    total={summary.total_logs || 1}
                    color="emerald"
                  />
                ))}
              </div>
            ) : (
              <EmptyChart message="No reason codes recorded yet" />
            )}
          </div>

          {/* Rule Hit Distribution */}
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-amber-500" />
              Rule Hit/Miss Distribution
            </h3>
            {Object.keys(distributions.rule_hits || {}).length > 0 ? (
              <div className="space-y-3">
                {Object.entries(distributions.rule_hits).map(([key, count]) => {
                  const isHit = key.endsWith('_hit');
                  return (
                    <DistributionBar 
                      key={key} 
                      label={key.replace('_hit', ' (HIT)').replace('_miss', ' (MISS)')} 
                      value={count} 
                      total={summary.total_logs || 1}
                      color={isHit ? "emerald" : "red"}
                    />
                  );
                })}
              </div>
            ) : (
              <EmptyChart message="No rule hits recorded yet" />
            )}
          </div>
        </div>
      )}

      {/* Request ID Drilldown Banner */}
      {requestIds.length > 0 && !drilldown && (
        <div className="bg-gradient-to-r from-violet-50 to-purple-50 border border-violet-200 rounded-xl p-4">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-violet-100 rounded-lg flex items-center justify-center">
                <Target className="w-5 h-5 text-violet-600" />
              </div>
              <div>
                <p className="font-medium text-violet-900">Request Drilldown</p>
                <p className="text-sm text-violet-700">
                  Explore <code className="bg-violet-100 px-1.5 py-0.5 rounded text-xs font-mono">{requestIds[0]}</code>
                </p>
              </div>
            </div>
            <button
              onClick={() => openRequestDrilldown(requestIds[0])}
              className="px-4 py-2 bg-violet-600 text-white rounded-lg text-sm font-medium hover:bg-violet-700 transition-colors flex items-center gap-2"
              data-testid="drilldown-btn"
            >
              View Drilldown
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Request Drilldown Panel */}
      {drilldown && (
        <RequestDrilldownPanel 
          data={drilldown} 
          onClose={() => setDrilldown(null)}
          loading={drilldownLoading}
        />
      )}

      {/* Tabs */}
      <div className="border-b border-slate-200">
        <div className="flex gap-6">
          <TabButton 
            active={activeTab === "overview"} 
            onClick={() => setActiveTab("overview")}
            label={`Rule Runs (${runs.length})`}
            testId="tab-runs"
          />
          <TabButton 
            active={activeTab === "logs"} 
            onClick={() => setActiveTab("logs")}
            label={`Explainability Logs (${logs.length})`}
            testId="tab-logs"
          />
        </div>
      </div>

      {/* Search */}
      <div className="bg-white border border-slate-200 rounded-xl p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Filter by request ID..."
              value={searchRequestId}
              onChange={(e) => setSearchRequestId(e.target.value)}
              className="w-full pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
              data-testid="search-request-id"
            />
          </div>
          {requestIds.length > 0 && (
            <select
              value={searchRequestId}
              onChange={(e) => setSearchRequestId(e.target.value)}
              className="px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
              data-testid="select-request-id"
            >
              <option value="">All requests</option>
              {requestIds.map(rid => (
                <option key={rid} value={rid}>{rid}</option>
              ))}
            </select>
          )}
        </div>
      </div>

      {/* Rule Runs Tab */}
      {activeTab === "overview" && (
        <div className="space-y-4">
          {runs.length > 0 ? (
            runs.map((run, idx) => (
              <RunCard 
                key={run.id || idx} 
                run={run} 
                onDrilldown={() => openRequestDrilldown(run.request_id)}
              />
            ))
          ) : (
            <EmptyState message="No rule runs found" icon={Target} />
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
                    <th>Weight</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log, idx) => (
                    <tr key={log.id || idx} data-testid={`log-row-${idx}`}>
                      <td className="font-mono font-medium">{log.rule_key}</td>
                      <td>v{log.rule_version}</td>
                      <td>
                        {log.hit === 't' || log.hit === true ? (
                          <span className="inline-flex items-center gap-1 text-emerald-600">
                            <CheckCircle className="w-4 h-4" />
                            <span className="text-sm font-medium">HIT</span>
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-slate-400">
                            <XCircle className="w-4 h-4" />
                            <span className="text-sm">MISS</span>
                          </span>
                        )}
                      </td>
                      <td>
                        <code className="bg-slate-100 px-1.5 py-0.5 rounded text-xs">{log.reason_code}</code>
                      </td>
                      <td className="max-w-xs truncate" title={log.reason_text}>{log.reason_text}</td>
                      <td className="font-mono">{log.points}</td>
                      <td className="font-mono">{log.weight}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState message="No explainability logs found" icon={FileText} />
          )}
        </div>
      )}

      {/* Source Info */}
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-6">
        <h3 className="font-semibold text-slate-900 mb-2">Data Sources</h3>
        <div className="flex flex-wrap gap-2">
          <span className="text-xs font-mono bg-white border border-slate-200 text-slate-600 px-2 py-1 rounded">
            D3_1_insert_proof__public.tcf_rule_runs.csv
          </span>
          <span className="text-xs font-mono bg-white border border-slate-200 text-slate-600 px-2 py-1 rounded">
            D3_1_insert_proof__public.tcf_explainability_logs.csv
          </span>
          <span className="text-xs font-mono bg-white border border-slate-200 text-slate-600 px-2 py-1 rounded">
            B_dist__public.tcf_explainability_logs__reason_codes.csv
          </span>
          <span className="text-xs font-mono bg-white border border-slate-200 text-slate-600 px-2 py-1 rounded">
            B_dist__public.tcf_explainability_logs__rule_hit_rate.csv
          </span>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, color }) {
  const colorClasses = {
    violet: "bg-violet-50 text-violet-600",
    blue: "bg-blue-50 text-blue-600",
    emerald: "bg-emerald-50 text-emerald-600",
    amber: "bg-amber-50 text-amber-600",
    sky: "bg-sky-50 text-sky-600",
  };
  
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-3">
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${colorClasses[color]}`}>
        <Icon className="w-5 h-5" />
      </div>
      <div>
        <p className="text-xs text-slate-500">{label}</p>
        <p className="text-xl font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>{value}</p>
      </div>
    </div>
  );
}

function DistributionBar({ label, value, total, color }) {
  const percentage = (value / total) * 100;
  const colorClasses = {
    violet: "bg-violet-500",
    blue: "bg-blue-500",
    emerald: "bg-emerald-500",
    amber: "bg-amber-500",
    red: "bg-red-400",
  };
  
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm font-mono text-slate-700">{label}</span>
        <span className="text-sm text-slate-500">{value} ({percentage.toFixed(0)}%)</span>
      </div>
      <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
        <div 
          className={`h-full ${colorClasses[color]} rounded-full transition-all duration-500`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

function EmptyChart({ message }) {
  return (
    <div className="flex items-center justify-center h-24 bg-slate-50 rounded-lg">
      <p className="text-sm text-slate-500">{message}</p>
    </div>
  );
}

function TabButton({ active, onClick, label, testId }) {
  return (
    <button
      onClick={onClick}
      className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
        active 
          ? "border-violet-600 text-violet-600" 
          : "border-transparent text-slate-500 hover:text-slate-700"
      }`}
      data-testid={testId}
    >
      {label}
    </button>
  );
}

function RunCard({ run, onDrilldown }) {
  const [expanded, setExpanded] = useState(false);
  
  return (
    <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-6 py-4 flex items-center gap-4 text-left hover:bg-slate-50 transition-colors"
        data-testid={`run-card-${run.id}`}
      >
        <div className="w-10 h-10 bg-violet-100 rounded-lg flex items-center justify-center">
          <Brain className="w-5 h-5 text-violet-600" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 flex-wrap">
            <span className="font-mono text-sm font-medium text-slate-900">{run.request_id}</span>
            <span className="status-badge bg-violet-50 text-violet-700 border-violet-200">
              {run.decision}
            </span>
          </div>
          <div className="flex items-center gap-4 mt-1 text-xs text-slate-500">
            <span>Score: <strong className="text-slate-700">{run.score}</strong></span>
            <span>Band: <strong className="text-slate-700">{run.band}</strong></span>
            <span>Engine: <strong className="text-slate-700">{run.engine_version}</strong></span>
            {run._logs_count > 0 && (
              <span className="flex items-center gap-1">
                <LinkIcon className="w-3 h-3" />
                {run._logs_count} logs
              </span>
            )}
          </div>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDrilldown();
          }}
          className="text-xs text-violet-600 hover:text-violet-800 flex items-center gap-1 px-2 py-1 bg-violet-50 rounded-lg"
          data-testid={`drilldown-link-${run.id}`}
        >
          <Target className="w-3 h-3" />
          Drilldown
        </button>
        <ChevronDown className={`w-5 h-5 text-slate-400 transition-transform ${expanded ? 'rotate-180' : ''}`} />
      </button>
      
      {expanded && (
        <div className="px-6 pb-4 border-t border-slate-100">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4">
            <DetailItem label="Run ID" value={run.id} mono />
            <DetailItem label="Tenant ID" value={run.tenant_id} mono />
            <DetailItem label="Subject Type" value={run.subject_type} />
            <DetailItem label="Subject ID" value={run.subject_id} mono />
            <DetailItem label="Created At" value={run.created_at} />
            <DetailItem label="Created By" value={run.created_by || "—"} />
            <DetailItem label="Context" value={run.context_json || "{}"} mono />
            <DetailItem label="Source" value={run._source} mono />
          </div>
        </div>
      )}
    </div>
  );
}

function RequestDrilldownPanel({ data, onClose, loading }) {
  if (loading) {
    return (
      <div className="bg-violet-50 border-2 border-violet-200 rounded-xl p-6">
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-violet-600"></div>
        </div>
      </div>
    );
  }

  const summary = data.summary || {};

  return (
    <div className="bg-gradient-to-br from-violet-50 to-purple-50 border-2 border-violet-200 rounded-xl overflow-hidden" data-testid="request-drilldown">
      <div className="px-6 py-4 border-b border-violet-200 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-violet-100 rounded-lg flex items-center justify-center">
            <Target className="w-5 h-5 text-violet-600" />
          </div>
          <div>
            <p className="font-bold text-violet-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
              Request Drilldown
            </p>
            <code className="text-xs text-violet-600 font-mono">{data.request_id}</code>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-2 hover:bg-violet-100 rounded-lg transition-colors"
          data-testid="close-drilldown"
        >
          <X className="w-5 h-5 text-violet-600" />
        </button>
      </div>

      <div className="p-6">
        {/* Summary Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white/60 rounded-lg p-3 text-center">
            <p className="text-xs text-violet-600">Final Decision</p>
            <p className="text-lg font-bold text-violet-900">{summary.final_decision}</p>
          </div>
          <div className="bg-white/60 rounded-lg p-3 text-center">
            <p className="text-xs text-violet-600">Band / Score</p>
            <p className="text-lg font-bold text-violet-900">{summary.final_band} / {summary.final_score}</p>
          </div>
          <div className="bg-white/60 rounded-lg p-3 text-center">
            <p className="text-xs text-violet-600">Hit Rate</p>
            <p className="text-lg font-bold text-emerald-600">{(summary.hit_rate || 0).toFixed(0)}%</p>
          </div>
          <div className="bg-white/60 rounded-lg p-3 text-center">
            <p className="text-xs text-violet-600">Total Points</p>
            <p className="text-lg font-bold text-violet-900">{summary.total_points}</p>
          </div>
        </div>

        {/* Timeline */}
        {data.timeline && data.timeline.length > 0 && (
          <div>
            <p className="text-sm font-medium text-violet-900 mb-3 flex items-center gap-2">
              <Clock className="w-4 h-4" />
              Event Timeline
            </p>
            <div className="space-y-3">
              {data.timeline.map((item, idx) => (
                <div key={idx} className="flex items-start gap-3">
                  <div className={`w-2 h-2 mt-2 rounded-full flex-shrink-0 ${
                    item.type === 'rule_run' ? 'bg-violet-500' : 'bg-emerald-500'
                  }`}></div>
                  <div className="flex-1 bg-white/80 rounded-lg p-3 border border-violet-100">
                    <div className="flex items-center justify-between mb-1 flex-wrap gap-2">
                      <span className={`text-xs px-2 py-0.5 rounded font-medium ${
                        item.type === 'rule_run' 
                          ? 'bg-violet-100 text-violet-700' 
                          : 'bg-emerald-100 text-emerald-700'
                      }`}>
                        {item.type === 'rule_run' ? 'RULE RUN' : 'EXPLAIN LOG'}
                      </span>
                      <span className="text-xs text-slate-500 font-mono">{item.timestamp}</span>
                    </div>
                    <p className="text-sm font-medium text-slate-900">{item.title}</p>
                    <p className="text-xs text-slate-600 mt-1">{item.subtitle}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Explainability Details */}
        {data.logs && data.logs.length > 0 && (
          <div className="mt-6">
            <p className="text-sm font-medium text-violet-900 mb-3">Rule Evaluation Details</p>
            <div className="space-y-2">
              {data.logs.map((log, idx) => (
                <div key={idx} className="bg-white/80 rounded-lg p-4 border border-violet-100">
                  <div className="flex items-center gap-2 mb-2 flex-wrap">
                    <span className="font-mono text-sm font-medium text-slate-900">{log.rule_key}</span>
                    <span className="text-xs text-slate-500">v{log.rule_version}</span>
                    {(log.hit === 't' || log.hit === true) ? (
                      <span className="text-xs bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded flex items-center gap-1">
                        <CheckCircle className="w-3 h-3" /> HIT
                      </span>
                    ) : (
                      <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded flex items-center gap-1">
                        <XCircle className="w-3 h-3" /> MISS
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-slate-600">{log.reason_text}</p>
                  <div className="mt-2 flex flex-wrap gap-3 text-xs text-slate-500">
                    <span>Code: <code className="bg-slate-100 px-1 rounded">{log.reason_code}</code></span>
                    <span>Points: <strong>{log.points}</strong></span>
                    <span>Weight: <strong>{log.weight}</strong></span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function EmptyState({ message, icon: Icon }) {
  return (
    <div className="text-center py-12 bg-white border border-slate-200 rounded-xl">
      <Icon className="w-12 h-12 text-slate-300 mx-auto" />
      <p className="mt-4 text-slate-500">{message}</p>
    </div>
  );
}

function DetailItem({ label, value, mono = false }) {
  return (
    <div>
      <p className="text-xs text-slate-500">{label}</p>
      <p className={`text-sm text-slate-900 truncate ${mono ? 'font-mono' : ''}`} title={value}>
        {value || '—'}
      </p>
    </div>
  );
}
