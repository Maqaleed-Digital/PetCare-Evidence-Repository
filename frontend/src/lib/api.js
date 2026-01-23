import axios from 'axios';

// Use relative URLs for Vite proxy to backend
const API = '/api';

// Baseline tag for evidence-backed rendering
export const BASELINE_TAG = 'sprint-6-day-3-closed-v2';
export const EVIDENCE_PACK_ID = 'sprint-6-day-3';
export const EVIDENCE_ROOT = 'pilot/sprint-6/day-3';

export const api = {
  // Evidence - E1
  getEvidencePacks: () => axios.get(`${API}/evidence/packs`),
  getPackFiles: (packId) => axios.get(`${API}/evidence/packs/${packId}/files`),
  getPackManifest: (packId) => axios.get(`${API}/evidence/packs/${packId}/manifest`),
  getPackFile: (packId, path) => axios.get(`${API}/evidence/packs/${packId}/file?path=${encodeURIComponent(path)}`),
  getPackFileUrl: (packId, path) => `${API}/evidence/packs/${packId}/file?path=${encodeURIComponent(path)}`,
  
  // Governance - E3
  getGovernanceSummary: () => axios.get(`${API}/governance/summary`),
  
  // Security - E2
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
  getExplainabilityDistributions: () => axios.get(`${API}/explainability/distributions`),
  getRequestDrilldown: (requestId) => axios.get(`${API}/explainability/request/${encodeURIComponent(requestId)}`),
  getRequestIds: () => axios.get(`${API}/explainability/request-ids`),
  
  // Report
  getDay3Report: () => axios.get(`${API}/report/day3`),
};

// E1: Checksum verification status mapping
// verified: true → OK (checksum exists + matches)
// verified: false → FAIL (checksum exists + mismatch)
// verified: null → MISSING (checksum does not include path)
export const getVerificationStatus = (file) => {
  if (file.verified === true) return 'OK';
  if (file.verified === false) return 'FAIL';
  return 'MISSING';
};

export default api;
