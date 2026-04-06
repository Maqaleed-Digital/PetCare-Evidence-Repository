export default function VetPage() {
  return (
    <main className="stack">
      <div className="card">
        <div className="kicker">Vet portal</div>
        <div className="title">Consultation queue and sign-off</div>
        <div className="subtitle">Clinical sign-off remains human-only and immutable after approval.</div>
      </div>
      <table className="table card">
        <thead>
          <tr>
            <th>Case</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Case queue</td>
            <td>Ready</td>
            <td>Open consultation</td>
          </tr>
          <tr>
            <td>SOAP note</td>
            <td>Draft</td>
            <td>Review and sign</td>
          </tr>
          <tr>
            <td>Prescription</td>
            <td>Pending</td>
            <td>Authorize</td>
          </tr>
        </tbody>
      </table>
    </main>
  )
}
