import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const api = {
  // Evidence
  getEvidencePacks: () => axios.get(`${API}/evidence/packs`),
  getPackFiles: (packId) => axios.get(`${API}/evidence/packs/${packId}/files`),
  getPackManifest: (packId) => axios.get(`${API}/evidence/packs/${packId}/manifest`),
  getPackFile: (packId, path) => axios.get(`${API}/evidence/packs/${packId}/file?path=${encodeURIComponent(path)}`),
  getPackFileUrl: (packId, path) => `${API}/evidence/packs/${packId}/file?path=${encodeURIComponent(path)}`,
  
  // Governance
  getGovernanceSummary: () => axios.get(`${API}/governance/summary`),
  
  // Security
  getRLSStatus: () => axios.get(`${API}/security/rls`),
  getBypassRLS: () => axios.get(`${API}/security/bypassrls`),
  getPolicies: () => axios.get(`${API}/security/policies`),
  getGrants: () => axios.get(`${API}/security/grants`),
  
  // Audit
  getAuditEvents: (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.event_type) params.append('event_type', filters.event_type);
    if (filters.severity) params.append('severity', filters.severity);
    if (filters.correlation_id) params.append('correlation_id', filters.correlation_id);
    if (filters.limit) params.append('limit', filters.limit);
    return axios.get(`${API}/audit/events?${params.toString()}`);
  },
  getAuditEventTypes: () => axios.get(`${API}/audit/event-types`),
  getAuditEventCatalog: () => axios.get(`${API}/audit/event-catalog`),
  getSeverityDistribution: () => axios.get(`${API}/audit/severity-distribution`),
  getCorrelationDrilldown: (correlationId) => axios.get(`${API}/audit/correlation/${encodeURIComponent(correlationId)}`),
  getCorrelationIds: () => axios.get(`${API}/audit/correlations`),
  
  // Explainability
  getExplainabilityRuns: (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.request_id) params.append('request_id', filters.request_id);
    return axios.get(`${API}/explainability/runs?${params.toString()}`);
  },
  getExplainabilityLogs: (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.request_id) params.append('request_id', filters.request_id);
    if (filters.run_id) params.append('run_id', filters.run_id);
    return axios.get(`${API}/explainability/logs?${params.toString()}`);
  },
  getExplainabilitySchema: () => axios.get(`${API}/explainability/schema`),
  
  // Report
  getDay3Report: () => axios.get(`${API}/report/day3`),
};

export default api;
