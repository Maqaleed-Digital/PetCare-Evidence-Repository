export default function PharmacyPage() {
  return (
    <main className="stack">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <div className="kicker">Pharmacy portal</div>
          <div className="title-lg">Prescription queue</div>
        </div>
        <span className="badge badge-green"><span className="icon-dot green" />Audit active</span>
      </div>

      <div className="grid cols2">
        <div className="role-card">
          <div className="role-card-icon">📬</div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>Validated prescriptions</div>
            <p className="subtitle">Only vet-signed prescriptions appear here. Unsigned items are not dispatchable.</p>
          </div>
          <span className="muted">Queue empty</span>
        </div>
        <div className="role-card">
          <div className="role-card-icon">⚠️</div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>Safety checks</div>
            <p className="subtitle">Contraindication warnings, dosage alerts, and substitution flags shown before dispense.</p>
          </div>
          <span className="muted">No active alerts</span>
        </div>
        <div className="role-card">
          <div className="role-card-icon">❄️</div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>Cold-chain tracking</div>
            <p className="subtitle">Regulated product handling state. Dispense blocked if chain-of-custody is broken.</p>
          </div>
          <span className="muted">No cold-chain items</span>
        </div>
        <div className="role-card">
          <div className="role-card-icon">📦</div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>Dispense log</div>
            <p className="subtitle">Every dispense action is timestamped, attributed, and immutably recorded.</p>
          </div>
          <span className="muted">No dispenses yet</span>
        </div>
      </div>

      <div className="note">
        <span className="muted">Dispense actions are irreversible once confirmed. All entries carry a correlation ID for audit tracing.</span>
      </div>
    </main>
  )
}
