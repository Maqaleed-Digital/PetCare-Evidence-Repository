export const dynamic = 'force-dynamic'

export default function HomePage() {
  return (
    <main className="stack">
      {/* Hero */}
      <div className="hero">
        <div className="hero-eyebrow">Governed veterinary platform</div>
        <h1 className="hero-title">
          Clinical care, built for<br />accountability from day one.
        </h1>
        <p className="hero-sub">
          VetiCare connects owners, vets, and pharmacies under a single
          governed platform — every action audited, every prescription
          traceable, every consultation signed.
        </p>
        <div className="hero-actions">
          <a className="button button-white" href="/signin">Sign in</a>
          <a className="button button-ghost" href="/onboarding">Clinic onboarding</a>
        </div>
      </div>

      {/* Role portals */}
      <div>
        <p className="kicker">Portals</p>
        <div className="grid cols2" style={{ marginTop: 12 }}>
          <div className="role-card">
            <div className="role-card-icon">🐾</div>
            <div>
              <div className="title" style={{ fontSize: 16 }}>Owner portal</div>
              <p className="subtitle">Pet profiles, health timeline, appointment booking, and consent management.</p>
            </div>
            <a className="button button-outline button-sm" href="/owner">Open owner portal</a>
          </div>
          <div className="role-card">
            <div className="role-card-icon">🩺</div>
            <div>
              <div className="title" style={{ fontSize: 16 }}>Vet portal</div>
              <p className="subtitle">Consultation queue, clinical note sign-off, case documentation, and escalation.</p>
            </div>
            <a className="button button-outline button-sm" href="/vet">Open vet portal</a>
          </div>
          <div className="role-card">
            <div className="role-card-icon">💊</div>
            <div>
              <div className="title" style={{ fontSize: 16 }}>Pharmacy portal</div>
              <p className="subtitle">Prescription queue, dispense workflow, safety and cold-chain states.</p>
            </div>
            <a className="button button-outline button-sm" href="/pharmacy">Open pharmacy portal</a>
          </div>
          <div className="role-card">
            <div className="role-card-icon">🛡️</div>
            <div>
              <div className="title" style={{ fontSize: 16 }}>Admin portal</div>
              <p className="subtitle">Tenant management, roles, evidence export, and audit visibility.</p>
            </div>
            <a className="button button-outline button-sm" href="/admin">Open admin portal</a>
          </div>
        </div>
      </div>

      {/* Governance strip */}
      <div className="card card-sm" style={{ display: 'flex', gap: 24, flexWrap: 'wrap', alignItems: 'center' }}>
        <span className="badge badge-green"><span className="icon-dot green" />All systems operational</span>
        <span className="muted">Fail-closed governance active</span>
        <span className="muted">·</span>
        <span className="muted">Audit chain live</span>
        <span className="muted">·</span>
        <span className="muted">Pilot phase</span>
      </div>
    </main>
  )
}
