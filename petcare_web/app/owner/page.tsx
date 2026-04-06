export default function OwnerPage() {
  return (
    <main className="stack">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <div className="kicker">Owner portal</div>
          <div className="title-lg">My pets</div>
        </div>
        <span className="badge badge-green"><span className="icon-dot green" />Audit active</span>
      </div>

      <div className="grid cols2">
        <div className="role-card">
          <div className="role-card-icon">🐾</div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>Pet profile</div>
            <p className="subtitle">Identity, species, age, allergies, vaccinations, and microchip data.</p>
          </div>
          <span className="muted">No pets registered yet</span>
        </div>
        <div className="role-card">
          <div className="role-card-icon">📋</div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>Health timeline</div>
            <p className="subtitle">Visits, prescriptions, lab results, and clinical events in order.</p>
          </div>
          <span className="muted">No records yet</span>
        </div>
        <div className="role-card">
          <div className="role-card-icon">📅</div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>Appointments</div>
            <p className="subtitle">Book, reschedule, and cancel with full audit trace on each action.</p>
          </div>
          <a className="button button-outline button-sm" href="#">Book appointment</a>
        </div>
        <div className="role-card">
          <div className="role-card-icon">✅</div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>Consent</div>
            <p className="subtitle">Capture and revoke treatment consent. Every change is immutably logged.</p>
          </div>
          <span className="muted">No active consents</span>
        </div>
      </div>

      <div className="note">
        <span className="muted">All actions in this portal are governed and audit-traced. Signing out revokes your active session.</span>
      </div>
    </main>
  )
}
