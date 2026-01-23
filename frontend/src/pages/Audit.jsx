import { useEffect, useState } from "react";
import { ScrollText, Search, Filter, ChevronDown, AlertTriangle, Info, AlertCircle } from "lucide-react";
import api from "../lib/api";

const severityConfig = {
  info: { bg: "bg-sky-50", text: "text-sky-700", border: "border-sky-200", icon: Info },
  warning: { bg: "bg-amber-50", text: "text-amber-700", border: "border-amber-200", icon: AlertTriangle },
  critical: { bg: "bg-red-50", text: "text-red-700", border: "border-red-200", icon: AlertCircle },
};

export default function Audit() {
  const [events, setEvents] = useState([]);
  const [eventTypes, setEventTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    event_type: "",
    severity: "",
    correlation_id: ""
  });
  const [expandedEvent, setExpandedEvent] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [eventsRes, typesRes] = await Promise.all([
          api.getAuditEvents(filters),
          api.getAuditEventTypes()
        ]);
        setEvents(eventsRes.data);
        setEventTypes(typesRes.data);
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
          Audit Events
        </h1>
        <p className="mt-2 text-slate-500">
          Browse and filter audit events from the pilot evidence
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white border border-slate-200 rounded-xl p-4">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-4 h-4 text-slate-500" />
          <span className="text-sm font-medium text-slate-700">Filters</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
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
            <input
              type="text"
              placeholder="Search correlation ID..."
              value={filters.correlation_id}
              onChange={(e) => handleFilterChange("correlation_id", e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-slate-900"
              data-testid="filter-correlation-id"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={clearFilters}
              className="px-4 py-2 text-sm text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
              data-testid="clear-filters"
            >
              Clear filters
            </button>
          </div>
        </div>
      </div>

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
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-sm font-medium text-slate-900">{event.event_type}</span>
                      <span className={`status-badge ${config.bg} ${config.text} ${config.border}`}>
                        {event.severity}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mt-1">
                      {event.occurred_at} • {event.source_mode} • {event.source_provider}
                    </p>
                  </div>
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
                      <DetailItem label="Metadata" value={JSON.stringify(event.metadata || {})} mono />
                    </div>
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
        <h3 className="font-semibold text-slate-900 mb-4">Available Event Types</h3>
        <p className="text-sm text-slate-600 mb-4">
          {eventTypes.length} event types defined in the system
        </p>
        <div className="flex flex-wrap gap-2">
          {eventTypes.slice(0, 10).map((type) => (
            <span 
              key={type.id || type.code}
              className="px-2 py-1 bg-white border border-slate-200 rounded text-xs font-mono text-slate-600"
            >
              {type.code}
            </span>
          ))}
          {eventTypes.length > 10 && (
            <span className="px-2 py-1 text-xs text-slate-500">
              +{eventTypes.length - 10} more
            </span>
          )}
        </div>
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
