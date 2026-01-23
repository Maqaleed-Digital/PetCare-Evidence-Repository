import { useEffect, useState } from "react";
import { Lock, Shield, CheckCircle, XCircle, AlertTriangle, Info } from "lucide-react";
import api from "../lib/api";

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

  const tablesWithRLS = rlsStatus.filter(t => t.rls_enabled).length;
  const totalTables = rlsStatus.length;
  const bypassCount = bypassRoles.filter(r => r.bypass_rls).length;

  return (
    <div className="space-y-8 animate-fade-in" data-testid="security-page">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>
          Security Review
        </h1>
        <p className="mt-2 text-slate-500">
          Row-Level Security (RLS) status, policies, and role permissions
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <SummaryCard
          icon={Shield}
          title="RLS Coverage"
          value={`${tablesWithRLS}/${totalTables}`}
          status={tablesWithRLS === totalTables ? "green" : "amber"}
          description={tablesWithRLS === totalTables ? "All tables protected" : "Partial coverage"}
          testId="rls-coverage"
        />
        <SummaryCard
          icon={Lock}
          title="Bypass Roles"
          value={bypassCount}
          status={bypassCount <= 2 ? "green" : "amber"}
          description={`${bypassCount} role${bypassCount !== 1 ? 's' : ''} can bypass RLS`}
          testId="bypass-count"
        />
        <SummaryCard
          icon={AlertTriangle}
          title="Policies Active"
          value={policies.length}
          status="green"
          description="RLS policies defined"
          testId="policies-count"
        />
      </div>

      {/* RLS Status Table */}
      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200">
          <h2 className="text-lg font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
            RLS Status by Table
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            Shows whether Row-Level Security is enabled and forced for each table
          </p>
        </div>
        <div className="data-table border-0">
          <table className="w-full">
            <thead>
              <tr>
                <th>Table Name</th>
                <th>RLS Enabled</th>
                <th>RLS Forced</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {rlsStatus.map((table, idx) => (
                <tr key={table.table_name || idx} data-testid={`rls-row-${idx}`}>
                  <td className="font-mono">{table.table_name}</td>
                  <td>
                    {table.rls_enabled ? (
                      <span className="inline-flex items-center gap-1.5 text-emerald-600">
                        <CheckCircle className="w-4 h-4" />
                        <span>Yes</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 text-red-600">
                        <XCircle className="w-4 h-4" />
                        <span>No</span>
                      </span>
                    )}
                  </td>
                  <td>
                    {table.rls_forced ? (
                      <span className="inline-flex items-center gap-1.5 text-emerald-600">
                        <CheckCircle className="w-4 h-4" />
                        <span>Yes</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 text-slate-400">
                        <span>No</span>
                      </span>
                    )}
                  </td>
                  <td>
                    {table.rls_enabled ? (
                      <span className="status-badge bg-emerald-50 text-emerald-700 border-emerald-200">
                        Protected
                      </span>
                    ) : (
                      <span className="status-badge bg-amber-50 text-amber-700 border-amber-200">
                        Review Required
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Bypass Roles Table */}
      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200">
          <h2 className="text-lg font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Roles with Bypass RLS Privilege
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            These roles can bypass Row-Level Security policies
          </p>
        </div>
        <div className="data-table border-0">
          <table className="w-full">
            <thead>
              <tr>
                <th>Role Name</th>
                <th>Bypass RLS</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              {bypassRoles.map((role, idx) => (
                <tr key={role.role_name || idx} data-testid={`bypass-row-${idx}`}>
                  <td className="font-mono font-medium">{role.role_name}</td>
                  <td>
                    {role.bypass_rls ? (
                      <span className="inline-flex items-center gap-1.5 text-amber-600">
                        <AlertTriangle className="w-4 h-4" />
                        <span>Yes</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 text-emerald-600">
                        <CheckCircle className="w-4 h-4" />
                        <span>No</span>
                      </span>
                    )}
                  </td>
                  <td className="text-slate-500 text-sm">
                    {role.bypass_rls && (role.role_name === 'service_role' || role.role_name === 'postgres') 
                      ? 'Expected for system/service accounts'
                      : role.bypass_rls 
                        ? 'Review privilege grant'
                        : 'Standard user role'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {/* Bypass Note */}
        <div className="px-6 py-4 bg-amber-50 border-t border-amber-100">
          <div className="flex items-start gap-3">
            <Info className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm text-amber-800 font-medium">Note: service_role / postgres bypassrls=true</p>
              <p className="text-sm text-amber-700 mt-1">
                This is expected behavior for Supabase architecture. Service roles need bypass privileges for backend operations.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Policies Table */}
      {policies.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-200">
            <h2 className="text-lg font-bold text-slate-900" style={{ fontFamily: 'Manrope, sans-serif' }}>
              RLS Policies
            </h2>
            <p className="text-sm text-slate-500 mt-1">
              Active Row-Level Security policies
            </p>
          </div>
          <div className="data-table border-0">
            <table className="w-full">
              <thead>
                <tr>
                  <th>Policy Name</th>
                  <th>Table</th>
                  <th>Command</th>
                  <th>Roles</th>
                </tr>
              </thead>
              <tbody>
                {policies.map((policy, idx) => (
                  <tr key={policy.policyname || idx} data-testid={`policy-row-${idx}`}>
                    <td className="font-mono text-sm">{policy.policyname}</td>
                    <td className="font-mono">{policy.schemaname}.{policy.tablename}</td>
                    <td>
                      <span className="status-badge bg-slate-100 text-slate-700 border-slate-200">
                        {policy.cmd}
                      </span>
                    </td>
                    <td className="font-mono text-sm">{policy.roles}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Info Box */}
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-6">
        <h3 className="font-semibold text-slate-900 mb-2">Security Recommendations</h3>
        <ul className="space-y-2 text-sm text-slate-600">
          <li className="flex items-start gap-2">
            <CheckCircle className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
            <span>Enable RLS on all tenant-scoped tables for proper data isolation</span>
          </li>
          <li className="flex items-start gap-2">
            <CheckCircle className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
            <span>Use JWT claims (auth.jwt()) for tenant filtering in policies</span>
          </li>
          <li className="flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
            <span>Review any tables without RLS before production deployment</span>
          </li>
        </ul>
      </div>
    </div>
  );
}

function SummaryCard({ icon: Icon, title, value, status, description, testId }) {
  const statusStyles = {
    green: "border-emerald-200 bg-emerald-50",
    amber: "border-amber-200 bg-amber-50",
    red: "border-red-200 bg-red-50",
  };

  return (
    <div 
      className={`rounded-xl border-2 p-6 ${statusStyles[status] || 'border-slate-200 bg-white'}`}
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
      <p className="mt-3 text-sm text-slate-600">{description}</p>
    </div>
  );
}
