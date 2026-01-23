import { useEffect, useState } from "react";
import { api } from "../lib/api";

function Block({ title, children }) {
  return (
    <div className="card" style={{ padding: 16 }}>
      <div style={{ fontWeight: 900, marginBottom: 8 }}>{title}</div>
      {children}
    </div>
  );
}

function Table({ rows }) {
  if (!rows?.length) return <div className="muted">No rows</div>;
  const cols = Object.keys(rows[0] || {});
  return (
    <div style={{ overflow: "auto" }}>
      <table className="table">
        <thead><tr>{cols.map(c => <th key={c}>{c}</th>)}</tr></thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>{cols.map(c => <td key={c} className="muted">{String(r[c] ?? "")}</td>)}</tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function Security() {
  const [rls, setRls] = useState([]);
  const [policies, setPolicies] = useState([]);
  const [policyCount, setPolicyCount] = useState([]);
  const [bypass, setBypass] = useState([]);
  const [grants, setGrants] = useState([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    Promise.all([
      api.securityRls().then(setRls),
      api.securityPolicies().then(setPolicies),
      api.securityPolicyCount().then(setPolicyCount),
      api.securityBypass().then(setBypass),
      api.securityGrants().then(setGrants),
    ]).catch(e => setErr(String(e)));
  }, []);

  const pc = Number(policyCount?.[0]?.policy_count ?? NaN);

  return (
    <div className="container">
      <div style={{ fontSize: 20, fontWeight: 900 }}>Security & RLS Review</div>
      <div className="muted">Rendered strictly from Day-3 addendum evidence.</div>

      {err ? (
        <div className="card" style={{ padding: 16, marginTop: 12, borderColor: "#fca5a5" }}>
          <div style={{ fontWeight: 800 }}>Error</div>
          <div className="muted" style={{ marginTop: 6 }}>{err}</div>
        </div>
      ) : null}

      <div className="card" style={{ padding: 12, marginTop: 12, borderColor: isFinite(pc) && pc === 0 ? "#fcd34d" : "#e5e7eb" }}>
        <div style={{ fontWeight: 900 }}>Governance Note</div>
        <div className="muted" style={{ marginTop: 6 }}>
          RLS is enabled/forced on <b>app.audit_events</b>. Policy count is <b>{isFinite(pc) ? pc : "…"}</b>.
          {isFinite(pc) && pc === 0 ? " This is a flagged posture (evidenced)." : ""}
        </div>
        <div className="muted" style={{ marginTop: 6, fontSize: 12 }}>
          Baseline tag: <span className="badge">sprint-6-day-3-closed</span>
        </div>
      </div>

      <div className="grid grid-2" style={{ marginTop: 12 }}>
        <Block title="RLS Status (app.audit_events)"><Table rows={rls} /></Block>
        <Block title="Bypass RLS Roles"><Table rows={bypass} /></Block>
      </div>

      <div className="grid grid-2" style={{ marginTop: 12 }}>
        <Block title="Policy Count"><Table rows={policyCount} /></Block>
        <Block title="Policies"><Table rows={policies} /></Block>
      </div>

      <div style={{ marginTop: 12 }}>
        <Block title="Role Table Grants (app.audit_events)"><Table rows={grants} /></Block>
      </div>
    </div>
  );
}
