export default function OwnerPage() {
  return (
    <main className="stack">
      <div className="card">
        <div className="kicker">Owner portal</div>
        <div className="title">Pet profile and appointment activation</div>
        <div className="subtitle">Governed entry surface for owners. Real auth and real API wiring required in production.</div>
      </div>
      <div className="grid cards">
        <div className="card"><strong>Pet profile</strong><p className="subtitle">Identity, species, age, allergies, vaccinations.</p></div>
        <div className="card"><strong>Health timeline</strong><p className="subtitle">Visits, prescriptions, results, events.</p></div>
        <div className="card"><strong>Appointment booking</strong><p className="subtitle">Book, reschedule, cancel with audit trace.</p></div>
        <div className="card"><strong>Consent</strong><p className="subtitle">Capture and revoke with audit enforcement.</p></div>
      </div>
    </main>
  )
}
