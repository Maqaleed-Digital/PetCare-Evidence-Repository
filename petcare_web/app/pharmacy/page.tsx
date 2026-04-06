export default function PharmacyPage() {
  return (
    <main className="stack">
      <div className="card">
        <div className="kicker">Pharmacy portal</div>
        <div className="title">Prescription queue and fulfillment</div>
        <div className="subtitle">Dispense workflow with safety and cold-chain visibility.</div>
      </div>
      <div className="grid cards">
        <div className="card"><strong>Queue</strong><p className="subtitle">Validated prescriptions only.</p></div>
        <div className="card"><strong>Safety</strong><p className="subtitle">Warnings, contraindications, substitutions.</p></div>
        <div className="card"><strong>Cold-chain</strong><p className="subtitle">Handling state for regulated fulfillment.</p></div>
      </div>
    </main>
  )
}
