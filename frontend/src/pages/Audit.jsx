import { useEffect, useState } from "react";
import { 
  ScrollText, 
  Search, 
  Filter, 
  ChevronDown, 
  AlertTriangle, 
  Info, 
  AlertCircle,
  Link as LinkIcon,
  Clock,
  Database,
  ArrowRight,
  X,
  Layers
} from "lucide-react";
import api from "../lib/api";

const severityConfig = {
  info: { bg: "bg-sky-50", text: "text-sky-700", border: "border-sky-200", icon: Info, dot: "bg-sky-500" },
  warning: { bg: "bg-amber-50", text: "text-amber-700", border: "border-amber-200", icon: AlertTriangle, dot: "bg-amber-500" },
  critical: { bg: "bg-red-50", text: "text-red-700", border: "border-red-200", icon: AlertCircle, dot: "bg-red-500" },
};

export default function Audit() {
  const [events, setEvents] = useState([]);
  const [eventTypes, setEventTypes] = useState([]);
  const [severityDist, setSeverityDist] = useState({});
  const [correlationIds, setCorrelationIds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    event_type: "",
    severity: "",
    correlation_id: ""
  });
  const [expandedEvent, setExpandedEvent] = useState(null);
  const [correlationDrilldown, setCorrelationDrilldown] = useState(null);
  const [drilldownLoading, setDrilldownLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [eventsRes, typesRes, distRes, corrRes] = await Promise.all([
          api.getAuditEvents(filters),
          api.getAuditEventTypes(),
          api.getSeverityDistribution(),
          api.getCorrelationIds()
        ]);
        setEvents(eventsRes.data);
        setEventTypes(typesRes.data);
        setSeverityDist(distRes.data);
        setCorrelationIds(corrRes.data);
      } catch (err) {
        console.error("Error fetching audit data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [filters]);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({ event_type: "", severity: "", correlation_id: "" });
  };

  const openCorrelationDrilldown = async (correlationId) => {
    setDrilldownLoading(true);
    try {
      const res = await api.getCorrelationDrilldown(correlationId);
      setCorrelationDrilldown(res.data);
    } catch (err) {
      console.error("Error fetching correlation drilldown:", err);
    } finally {
      setDrilldownLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64" data-testid="audit-loading">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in" data-testid="audit-page">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>
          Audit Explorer
        </h1>
        <p className="mt-2 text-slate-500">
          Browse and filter audit events from all CSV sources
        </p>
      </div>

      {/* Severity Distribution */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <SeverityCard 
          severity="critical" 
          count={severityDist.critical || 0} 
          onClick={() => handleFilterChange('severity', 'critical')}
          active={filters.severity === 'critical'}
        />
        <SeverityCard 
          severity="warning" 
          count={severityDist.warning || 0} 
          onClick={() => handleFilterChange('severity', 'warning')}
          active={filters.severity === 'warning'}
        />
        <SeverityCard 
          severity="info" 
          count={severityDist.info || 0} 
          onClick={() => handleFilterChange('severity', 'info')}
          active={filters.severity === 'info'}
        />
        <div className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-3">
          <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center">
            <Database className="w-5 h-5 text-slate-600" />
          </div>
          <div>
            <p className="text-xs text-slate-500">Total Event Types</p>
            <p className="text-xl font-bold text-slate-900">{eventTypes.length}</p>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white border border-slate-200 rounded-xl p-4">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-4 h-4 text-slate-500" />
          <span className="text-sm font-medium text-slate-700">Filters</span>
          {(filters.event_type || filters.severity || filters.correlation_id) && (
            <button
              onClick={clearFilters}
              className="ml-auto text-xs text-slate-500 hover:text-slate-700 flex items-center gap-1"
              data-testid="clear-filters"
            >
              <X className="w-3 h-3" /> Clear all
            </button>
          )}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="text-xs text-slate-500 block mb-1">Event Type</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search event type..."
                value={filters.event_type}
                onChange={(e) => handleFilterChange("event_type", e.target.value)}
                className="w-full pl-9 pr-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-slate-900"
                data-testid="filter-event-type"
              />
            </div>
          </div>
          <div>
            <label className="text-xs text-slate-500 block mb-1">Severity</label>
            <select
              value={filters.severity}
              onChange={(e) => handleFilterChange("severity", e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-slate-900"
              data-testid="filter-severity"
            >
              <option value="">All severities</option>
              <option value="info">Info</option>
              <option value="warning">Warning</option>
              <option value="critical">Critical</option>
            </select>
          </div>
          <div>
            <label className="text-xs text-slate-500 block mb-1">Correlation ID</label>
            <select
              value={filters.correlation_id}
              onChange={(e) => handleFilterChange("correlation_id", e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-slate-900"
              data-testid="filter-correlation-id"
            >
              <option value="">All correlations</option>
              {correlationIds.map(cid => (
                <option key={cid} value={cid}>{cid}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Correlation Drilldown Banner */}
      {correlationIds.length > 0 && !correlationDrilldown && (
        <div className="bg-gradient-to-r from-violet-50 to-purple-50 border border-violet-200 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-violet-100 rounded-lg flex items-center justify-center">
                <Layers className="w-5 h-5 text-violet-600" />
              </div>
              <div>
                <p className="font-medium text-violet-900">Correlation Drilldown</p>
                <p className="text-sm text-violet-700">
                  Explore the <code className="bg-violet-100 px-1.5 py-0.5 rounded text-xs font-mono">{correlationIds[0]}</code> correlation chain
                </p>
              </div>
            </div>
            <button
              onClick={() => openCorrelationDrilldown(correlationIds[0])}
              className="px-4 py-2 bg-violet-600 text-white rounded-lg text-sm font-medium hover:bg-violet-700 transition-colors flex items-center gap-2"
              data-testid="drilldown-btn"
            >
              View Drilldown
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Correlation Drilldown Panel */}
      {correlationDrilldown && (
        <CorrelationDrilldownPanel 
          data={correlationDrilldown} 
          onClose={() => setCorrelationDrilldown(null)}
          loading={drilldownLoading}
        />
      )}

      {/* Results Count */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-500">
          {events.length} event{events.length !== 1 ? 's' : ''} found
        </p>
      </div>

      {/* Events List */}
      {events.length > 0 ? (
        <div className="space-y-3">
          {events.map((event, idx) => {
            const config = severityConfig[event.severity] || severityConfig.info;
            const Icon = config.icon;
            const isExpanded = expandedEvent === idx;

            return (
              <div 
                key={event.id || idx}
                className={`border rounded-xl overflow-hidden transition-all ${config.border} ${isExpanded ? config.bg : 'bg-white'}`}
                data-testid={`audit-event-${idx}`}
              >
                <button
                  onClick={() => setExpandedEvent(isExpanded ? null : idx)}
                  className="w-full px-6 py-4 flex items-center gap-4 text-left hover:bg-slate-50/50 transition-colors"
                  data-testid={`audit-event-toggle-${idx}`}
                >
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${config.bg}`}>
                    <Icon className={`w-4 h-4 ${config.text}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-mono text-sm font-medium text-slate-900">{event.event_type}</span>
                      <span className={`status-badge ${config.bg} ${config.text} ${config.border}`}>
                        {event.severity}
                      </span>
                      {event._source && (
                        <span className="text-xs bg-slate-100 text-slate-500 px-2 py-0.5 rounded font-mono">
                          {event._source.split('__')[0]}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-4 mt-1 text-xs text-slate-500">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {event.occurred_at || 'N/A'}
                      </span>
                      {event.source_mode && (
                        <span>{event.source_mode}</span>
                      )}
                      {event.source_provider && (
                        <span>{event.source_provider}</span>
                      )}
                    </div>
                  </div>
                  {event.correlation_id && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        openCorrelationDrilldown(event.correlation_id);
                      }}
                      className="text-xs text-violet-600 hover:text-violet-800 flex items-center gap-1 px-2 py-1 bg-violet-50 rounded-lg"
                      data-testid={`correlation-link-${idx}`}
                    >
                      <LinkIcon className="w-3 h-3" />
                      Drilldown
                    </button>
                  )}
                  <ChevronDown className={`w-5 h-5 text-slate-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
                </button>

                {isExpanded && (
                  <div className="px-6 pb-4 border-t border-slate-200/50">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4">
                      <DetailItem label="ID" value={event.id} mono />
                      <DetailItem label="Tenant ID" value={event.tenant_id} mono />
                      <DetailItem label="Correlation ID" value={event.correlation_id} mono />
                      <DetailItem label="Target Type" value={event.target_type} />
                      <DetailItem label="Target ID" value={event.target_id || "—"} mono />
                      <DetailItem label="Actor User ID" value={event.actor_user_id || "—"} mono />
                      <DetailItem label="Evidence Hash" value={event.evidence_hash || "—"} mono />
                      <DetailItem label="Source File" value={event._source || "—"} mono />
                    </div>
                    {event.metadata && event.metadata !== '{}' && (
                      <div className="mt-4 p-3 bg-slate-100 rounded-lg">
                        <p className="text-xs text-slate-500 mb-1">Metadata</p>
                        <pre className="text-xs font-mono text-slate-700 overflow-x-auto">
                          {typeof event.metadata === 'string' ? event.metadata : JSON.stringify(event.metadata, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-12 bg-white border border-slate-200 rounded-xl">
          <ScrollText className="w-12 h-12 text-slate-300 mx-auto" />
          <p className="mt-4 text-slate-500">No audit events found</p>
          <p className="text-sm text-slate-400 mt-1">Try adjusting your filters</p>
        </div>
      )}

      {/* Event Types Reference */}
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-6">
        <h3 className="font-semibold text-slate-900 mb-4">Available Event Types by Severity</h3>
        <div className="space-y-4">
          {['critical', 'warning', 'info'].map(sev => {
            const config = severityConfig[sev];
            const types = eventTypes.filter(t => t.severity === sev);
            if (types.length === 0) return null;
            return (
              <div key={sev}>
                <div className="flex items-center gap-2 mb-2">
                  <span className={`w-2 h-2 rounded-full ${config.dot}`}></span>
                  <span className="text-sm font-medium text-slate-700 capitalize">{sev} ({types.length})</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {types.slice(0, 8).map((type) => (
                    <button
                      key={type.id || type.code}
                      onClick={() => handleFilterChange('event_type', type.code)}
                      className={`px-2 py-1 border rounded text-xs font-mono transition-colors ${
                        filters.event_type === type.code 
                          ? `${config.bg} ${config.text} ${config.border}` 
                          : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300'
                      }`}
                    >
                      {type.code}
                    </button>
                  ))}
                  {types.length > 8 && (
                    <span className="px-2 py-1 text-xs text-slate-500">
                      +{types.length - 8} more
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function SeverityCard({ severity, count, onClick, active }) {
  const config = severityConfig[severity] || severityConfig.info;
  const Icon = config.icon;
  
  return (
    <button
      onClick={onClick}
      className={`rounded-xl p-4 flex items-center gap-3 transition-all border-2 ${
        active 
          ? `${config.bg} ${config.border}` 
          : 'bg-white border-slate-200 hover:border-slate-300'
      }`}
      data-testid={`severity-card-${severity}`}
    >
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${config.bg}`}>
        <Icon className={`w-5 h-5 ${config.text}`} />
      </div>
      <div className="text-left">
        <p className="text-xs text-slate-500 capitalize">{severity}</p>
        <p className="text-xl font-bold text-slate-900">{count}</p>
      </div>
    </button>
  );
}

function CorrelationDrilldownPanel({ data, onClose, loading }) {
  if (loading) {
    return (
      <div className="bg-violet-50 border-2 border-violet-200 rounded-xl p-6">
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-violet-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-violet-50 to-purple-50 border-2 border-violet-200 rounded-xl overflow-hidden" data-testid="correlation-drilldown">
      <div className="px-6 py-4 border-b border-violet-200 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-violet-100 rounded-lg flex items-center justify-center">
            <Layers className="w-5 h-5 text-violet-600" />
          </div>
          <div>
            <p className="font-bold text-violet-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
              Correlation Drilldown
            </p>
            <code className="text-xs text-violet-600 font-mono">{data.correlation_id}</code>
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
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-white/60 rounded-lg p-3 text-center">
            <p className="text-xs text-violet-600">Audit Events</p>
            <p className="text-2xl font-bold text-violet-900">{data.audit_events?.length || 0}</p>
          </div>
          <div className="bg-white/60 rounded-lg p-3 text-center">
            <p className="text-xs text-violet-600">Rule Runs</p>
            <p className="text-2xl font-bold text-violet-900">{data.explainability_runs?.length || 0}</p>
          </div>
          <div className="bg-white/60 rounded-lg p-3 text-center">
            <p className="text-xs text-violet-600">Explain Logs</p>
            <p className="text-2xl font-bold text-violet-900">{data.explainability_logs?.length || 0}</p>
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
                  <div className="w-2 h-2 mt-2 rounded-full bg-violet-400 flex-shrink-0"></div>
                  <div className="flex-1 bg-white/80 rounded-lg p-3 border border-violet-100">
                    <div className="flex items-center justify-between mb-1">
                      <span className={`text-xs px-2 py-0.5 rounded ${
                        item.type === 'audit_event' ? 'bg-sky-100 text-sky-700' :
                        item.type === 'rule_run' ? 'bg-emerald-100 text-emerald-700' :
                        'bg-purple-100 text-purple-700'
                      }`}>
                        {item.type.replace('_', ' ')}
                      </span>
                      <span className="text-xs text-slate-500">{item.timestamp}</span>
                    </div>
                    <p className="text-sm text-slate-700">{item.event}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Audit Event Details */}
        {data.audit_events?.length > 0 && (
          <div className="mt-6">
            <p className="text-sm font-medium text-violet-900 mb-3">Audit Event Details</p>
            {data.audit_events.map((event, idx) => (
              <div key={idx} className="bg-white/80 rounded-lg p-4 border border-violet-100">
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-slate-500">Event: </span>
                    <span className="font-mono text-slate-900">{event.event_type}</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Severity: </span>
                    <span className="font-medium text-slate-900">{event.severity}</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Mode: </span>
                    <span className="text-slate-900">{event.source_mode}</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Provider: </span>
                    <span className="text-slate-900">{event.source_provider}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Explainability Details */}
        {data.explainability_logs?.length > 0 && (
          <div className="mt-6">
            <p className="text-sm font-medium text-violet-900 mb-3">Explainability Logs</p>
            {data.explainability_logs.map((log, idx) => (
              <div key={idx} className="bg-white/80 rounded-lg p-4 border border-violet-100">
                <div className="flex items-center gap-2 mb-2">
                  <span className="font-mono text-sm font-medium text-slate-900">{log.rule_key}</span>
                  <span className="text-xs text-slate-500">v{log.rule_version}</span>
                  {log.hit === 'true' && (
                    <span className="text-xs bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded">HIT</span>
                  )}
                </div>
                <p className="text-sm text-slate-600">{log.reason_text}</p>
                <div className="mt-2 text-xs text-slate-500">
                  Code: <code className="bg-slate-100 px-1 rounded">{log.reason_code}</code>
                  {' • '}Weight: {log.weight} • Points: {log.points}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
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
