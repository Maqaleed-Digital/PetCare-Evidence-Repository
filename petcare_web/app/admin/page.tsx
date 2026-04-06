export default function AdminPage() {
  return (
    <main className="stack">
      <div className="card">
        <div className="kicker">Platform admin</div>
        <div className="title">Governance, tenants, and evidence export</div>
        <div className="subtitle">Operational and compliance surface with audit visibility and role discipline.</div>
      </div>
      <div className="grid cards">
        <div className="card"><strong>Tenants</strong><p className="subtitle">Clinic listing and status.</p></div>
        <div className="card"><strong>Users and roles</strong><p className="subtitle">Role review and least-privilege monitoring.</p></div>
        <div className="card"><strong>Audit log</strong><p className="subtitle">Trace visibility and export readiness.</p></div>
        <div className="card"><strong>Evidence export</strong><p className="subtitle">Governed reporting and operational proof.</p></div>
      </div>
    </main>
  )
}
