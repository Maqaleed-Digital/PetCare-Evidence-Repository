export default function AdminPage() {
  return (
    <main className="stack">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <div className="kicker">Platform admin</div>
          <div className="title-lg">Governance &amp; operations</div>
        </div>
        <span className="badge badge-green"><span className="icon-dot green" />Constitution sealed</span>
      </div>

      <div className="grid cols2">
        <div className="role-card">
          <div className="role-card-icon">🏥</div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>Tenants</div>
            <p className="subtitle">Clinic listing, status, and pilot cohort tracking. Each tenant is isolated and audited.</p>
          </div>
          <span className="muted">1 clinic in pilot</span>
        </div>
        <div className="role-card">
          <div className="role-card-icon">👥</div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>Users &amp; roles</div>
            <p className="subtitle">Role assignment, least-privilege monitoring, and access review.</p>
          </div>
          <a className="button button-outline button-sm" href="#">Review roles</a>
        </div>
        <div className="role-card">
          <div className="role-card-icon">🔍</div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>Audit log</div>
            <p className="subtitle">Full trace visibility across all clinical, financial, and admin events.</p>
          </div>
          <a className="button button-outline button-sm" href="/api/audit-test">Test probe</a>
        </div>
        <div className="role-card">
          <div className="role-card-icon">📊</div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>Evidence export</div>
            <p className="subtitle">Governed reporting packs for board, investor, and regulator readouts.</p>
          </div>
          <a className="button button-outline button-sm" href="#">Export pack</a>
        </div>
      </div>

      <div className="card card-sm" style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
        <div><div className="muted">Platform state</div><div style={{ fontWeight: 700, marginTop: 4 }}>CONTROLLED_PRODUCTION_ACTIVE</div></div>
        <div><div className="muted">Audit chain</div><div style={{ fontWeight: 700, marginTop: 4, color: 'var(--success)' }}>Live</div></div>
        <div><div className="muted">Fail-closed</div><div style={{ fontWeight: 700, marginTop: 4, color: 'var(--success)' }}>Active</div></div>
        <div><div className="muted">Pilot clinics</div><div style={{ fontWeight: 700, marginTop: 4 }}>1 / 2 max</div></div>
      </div>
    </main>
  )
}
