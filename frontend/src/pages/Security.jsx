import { useEffect, useState } from "react";
import { 
  Lock, 
  Shield, 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Info,
  Users,
  FileText,
  Tag
} from "lucide-react";
import api, { BASELINE_TAG } from "../lib/api";

// E2: Security & RLS View (UI0-G2)
// Deterministic rule: If policy_count == 0, show flagged notice
// Highlight any role where rolbypassrls=true

export default function Security() {
  const [rlsStatus, setRlsStatus] = useState([]);
  const [bypassRoles, setBypassRoles] = useState([]);
  const [policies, setPolicies] = useState([]);
  const [grants, setGrants] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [rlsRes, bypassRes, policiesRes, grantsRes] = await Promise.all([
          api.getRLSStatus(),
          api.getBypassRLS(),
          api.getPolicies(),
          api.getGrants()
        ]);
        setRlsStatus(rlsRes.data);
        setBypassRoles(bypassRes.data);
        setPolicies(policiesRes.data);
        setGrants(grantsRes.data);
      } catch (err) {
        console.error("Error fetching security data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64" data-testid="security-loading">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900"></div>
      </div>
    );
  }

  // E2: Calculate policy count for deterministic flagging
  const policyCount = policies.length;
  const tablesWithRLS = rlsStatus.filter(t => t.rls_enabled).length;
  const tablesWithForce = rlsStatus.filter(t => t.rls_forced).length;
  const bypassCount = bypassRoles.filter(r => r.bypass_rls).length;

  // E2: Check for app.audit_events specifically
  const auditEventsRLS = rlsStatus.find(t => t.table_name === 'app.audit_events');
  const auditEventsEnabled = auditEventsRLS?.rls_enabled;
  const auditEventsForced = auditEventsRLS?.rls_forced;

  return (
    <div className="space-y-6 animate-fade-in" data-testid="security-page">
      {/* Header with Baseline Tag */}
      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Security & RLS
          </h1>
          <p className="mt-2 text-slate-500">
            Evidence-backed security posture review
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-2 bg-slate-100 rounded-lg">
          <Tag className="w-4 h-4 text-slate-500" />
          <span className="text-sm font-mono text-slate-700">{BASELINE_TAG}</span>
        </div>
      </div>

      {/* E2: Flagged Notice - policy_count == 0 */}
      {policyCount === 0 && auditEventsEnabled && auditEventsForced && (
        <div className="bg-amber-50 border-2 border-amber-200 rounded-xl p-4" data-testid="policy-count-warning">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-6 h-6 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-bold text-amber-800">Security Notice (Evidence-Backed)</p>
              <p className="text-sm text-amber-700 mt-1">
                RLS enabled+forced on <code className="bg-amber-100 px-1.5 py-0.5 rounded font-mono">app.audit_events</code>; 
                policy_count={policyCount}
              </p>
              <p className="text-xs text-amber-600 mt-2">
                Source: /api/security/policies, /api/security/rls
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <SummaryCard
          icon={Shield}
          title="RLS Coverage"
          value={`${tablesWithRLS}/${rlsStatus.length}`}
          status={tablesWithRLS === rlsStatus.length ? "green" : "amber"}
          subtitle="Tables with RLS enabled"
          testId="rls-coverage"
        />
        <SummaryCard
          icon={Lock}
          title="Force RLS"
          value={`${tablesWithForce}/${rlsStatus.length}`}
          status={tablesWithForce > 0 ? "green" : "amber"}
          subtitle="Tables with force enabled"
          testId="force-rls"
        />
        <SummaryCard
          icon={FileText}
          title="Policies"
          value={policyCount}
          status={policyCount > 0 ? "green" : "amber"}
          subtitle="RLS policies defined"
          testId="policy-count"
        />
        <SummaryCard
          icon={Users}
          title="Bypass Roles"
          value={bypassCount}
          status={bypassCount <= 2 ? "green" : "amber"}
          subtitle="Roles can bypass RLS"
          testId="bypass-count"
        />
      </div>

      {/* RLS Status Table - /api/security/rls */}
      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 bg-slate-50">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
                RLS Status by Table
              </h2>
              <p className="text-xs text-slate-500 font-mono mt-1">Source: /api/security/rls</p>
            </div>
          </div>
        </div>
        <table className="w-full">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Table Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">RLS Enabled</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">RLS Forced</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {rlsStatus.map((table, idx) => (
              <tr key={table.table_name || idx} className="hover:bg-slate-50" data-testid={`rls-row-${idx}`}>
                <td className="px-6 py-4 font-mono text-sm text-slate-900">{table.table_name}</td>
                <td className="px-6 py-4">
                  {table.rls_enabled ? (
                    <span className="inline-flex items-center gap-1.5 text-emerald-600">
                      <CheckCircle className="w-4 h-4" />
                      <span className="text-sm font-medium">Yes</span>
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 text-red-600">
                      <XCircle className="w-4 h-4" />
                      <span className="text-sm font-medium">No</span>
                    </span>
                  )}
                </td>
                <td className="px-6 py-4">
                  {table.rls_forced ? (
                    <span className="inline-flex items-center gap-1.5 text-emerald-600">
                      <CheckCircle className="w-4 h-4" />
                      <span className="text-sm font-medium">Yes</span>
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 text-slate-400">
                      <span className="text-sm">No</span>
                    </span>
                  )}
                </td>
                <td className="px-6 py-4">
                  {table.rls_enabled ? (
                    <span className="px-2 py-1 bg-emerald-50 text-emerald-700 text-xs font-medium rounded-full border border-emerald-200">
                      Protected
                    </span>
                  ) : (
                    <span className="px-2 py-1 bg-amber-50 text-amber-700 text-xs font-medium rounded-full border border-amber-200">
                      Review Required
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Bypass Roles Table - /api/security/bypassrls */}
      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 bg-slate-50">
          <div>
            <h2 className="text-lg font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
              Bypass RLS Roles
            </h2>
            <p className="text-xs text-slate-500 font-mono mt-1">Source: /api/security/bypassrls</p>
          </div>
        </div>
        <table className="w-full">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Role Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Bypass RLS</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Notes</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {bypassRoles.map((role, idx) => {
              const isBypass = role.bypass_rls;
              const isSystemRole = role.role_name === 'postgres' || role.role_name === 'service_role';
              
              return (
                <tr 
                  key={role.role_name || idx} 
                  className={`hover:bg-slate-50 ${isBypass ? 'bg-amber-50/50' : ''}`}
                  data-testid={`bypass-row-${idx}`}
                >
                  <td className="px-6 py-4">
                    <span className={`font-mono text-sm font-medium ${isBypass ? 'text-amber-800' : 'text-slate-900'}`}>
                      {role.role_name}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    {isBypass ? (
                      <span className="inline-flex items-center gap-1.5 text-amber-600">
                        <AlertTriangle className="w-4 h-4" />
                        <span className="text-sm font-medium">Yes</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 text-emerald-600">
                        <CheckCircle className="w-4 h-4" />
                        <span className="text-sm font-medium">No</span>
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-500">
                    {isBypass && isSystemRole 
                      ? 'Expected for system/service accounts'
                      : isBypass 
                        ? 'Review privilege grant'
                        : 'Standard user role'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        
        {/* E2: Highlight bypass roles notice */}
        <div className="px-6 py-4 bg-amber-50 border-t border-amber-100">
          <div className="flex items-start gap-3">
            <Info className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm text-amber-800 font-medium">
                Note: postgres/service_role bypassrls=true
              </p>
              <p className="text-xs text-amber-700 mt-1">
                Expected behavior for Supabase architecture. Service roles need bypass privileges for backend operations.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Policies Table - /api/security/policies */}
      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 bg-slate-50">
          <div>
            <h2 className="text-lg font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
              RLS Policies
            </h2>
            <p className="text-xs text-slate-500 font-mono mt-1">Source: /api/security/policies</p>
          </div>
        </div>
        {policies.length > 0 ? (
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Policy Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Table</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Command</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Roles</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {policies.map((policy, idx) => (
                <tr key={policy.policyname || idx} className="hover:bg-slate-50" data-testid={`policy-row-${idx}`}>
                  <td className="px-6 py-4 font-mono text-sm text-slate-900">{policy.policyname}</td>
                  <td className="px-6 py-4 font-mono text-sm text-slate-600">{policy.schemaname}.{policy.tablename}</td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-1 bg-slate-100 text-slate-700 text-xs font-medium rounded">
                      {policy.cmd}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-mono text-sm text-slate-600">{policy.roles}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="text-center py-12">
            <FileText className="w-12 h-12 text-slate-300 mx-auto" />
            <p className="mt-4 text-slate-500">No policies defined (policy_count=0)</p>
          </div>
        )}
      </div>

      {/* Grants Table - /api/security/grants */}
      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 bg-slate-50">
          <div>
            <h2 className="text-lg font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
              Role Table Grants
            </h2>
            <p className="text-xs text-slate-500 font-mono mt-1">Source: /api/security/grants</p>
          </div>
        </div>
        {grants.length > 0 ? (
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Grantee</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Schema</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Table</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Privilege</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {grants.slice(0, 20).map((grant, idx) => (
                <tr key={idx} className="hover:bg-slate-50" data-testid={`grant-row-${idx}`}>
                  <td className="px-6 py-4 font-mono text-sm text-slate-900">{grant.grantee}</td>
                  <td className="px-6 py-4 text-sm text-slate-600">{grant.table_schema}</td>
                  <td className="px-6 py-4 font-mono text-sm text-slate-600">{grant.table_name}</td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-1 bg-slate-100 text-slate-700 text-xs font-medium rounded">
                      {grant.privilege_type}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="text-center py-12">
            <Users className="w-12 h-12 text-slate-300 mx-auto" />
            <p className="mt-4 text-slate-500">No grants data available</p>
          </div>
        )}
        {grants.length > 20 && (
          <div className="px-6 py-3 bg-slate-50 border-t border-slate-200 text-center">
            <p className="text-sm text-slate-500">Showing 20 of {grants.length} grants</p>
          </div>
        )}
      </div>
    </div>
  );
}

function SummaryCard({ icon: Icon, title, value, status, subtitle, testId }) {
  const statusStyles = {
    green: "border-emerald-200 bg-emerald-50",
    amber: "border-amber-200 bg-amber-50",
    red: "border-red-200 bg-red-50",
  };

  return (
    <div 
      className={`rounded-xl border-2 p-5 ${statusStyles[status] || 'border-slate-200 bg-white'}`}
      data-testid={testId}
    >
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center border border-slate-200">
          <Icon className="w-5 h-5 text-slate-600" />
        </div>
        <div>
          <p className="text-sm text-slate-500">{title}</p>
          <p className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
            {value}
          </p>
        </div>
      </div>
      <p className="mt-3 text-sm text-slate-600">{subtitle}</p>
    </div>
  );
}
