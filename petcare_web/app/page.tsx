import { env } from '@/lib/env'

export default function HomePage() {
  return (
    <main className="stack">
      <div className="card">
        <div className="kicker">Governed web activation</div>
        <div className="title">{env.NEXT_PUBLIC_APP_NAME}</div>
        <div className="subtitle">
          Full governed UI for owner, vet, pharmacy, and platform administration. Domain go-live is blocked until environment, auth, API wiring, and audit verification all pass.
        </div>
      </div>

      <div className="grid cards">
        <div className="card">
          <span className="badge">Owner</span>
          <p className="subtitle">Pet profiles, health timeline, appointment booking, consent.</p>
          <a className="button" href="/owner">Open owner portal</a>
        </div>
        <div className="card">
          <span className="badge">Vet</span>
          <p className="subtitle">Consultation queue, sign-off, case documentation, escalation.</p>
          <a className="button" href="/vet">Open vet portal</a>
        </div>
        <div className="card">
          <span className="badge">Pharmacy</span>
          <p className="subtitle">Prescription queue, dispense workflow, safety and cold-chain states.</p>
          <a className="button" href="/pharmacy">Open pharmacy portal</a>
        </div>
        <div className="card">
          <span className="badge">Admin</span>
          <p className="subtitle">Tenants, roles, evidence export, audit visibility.</p>
          <a className="button" href="/admin">Open admin portal</a>
        </div>
      </div>
    </main>
  )
}
