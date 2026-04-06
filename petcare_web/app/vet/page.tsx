export default function VetPage() {
  return (
    <main className="stack">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <div className="kicker">Vet portal</div>
          <div className="title-lg">Consultation queue</div>
        </div>
        <span className="badge badge-green"><span className="icon-dot green" />Audit active</span>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table className="table">
          <thead>
            <tr>
              <th>Case</th>
              <th>Patient</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Consultation queue</td>
              <td>—</td>
              <td><span className="badge badge-amber">Waiting</span></td>
              <td><a className="button button-outline button-sm" href="#">Open</a></td>
            </tr>
            <tr>
              <td>Clinical note (SOAP)</td>
              <td>—</td>
              <td><span className="badge badge-gray">Draft</span></td>
              <td><a className="button button-outline button-sm" href="#">Review &amp; sign</a></td>
            </tr>
            <tr>
              <td>Prescription</td>
              <td>—</td>
              <td><span className="badge badge-amber">Pending</span></td>
              <td><a className="button button-outline button-sm" href="#">Authorize</a></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="note">
        <span className="muted">Clinical sign-off is human-only and immutable once completed. All prescription authorizations are audit-traced.</span>
      </div>
    </main>
  )
}
