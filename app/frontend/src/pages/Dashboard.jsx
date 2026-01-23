import { useEffect, useState } from "react";
import { api } from "../lib/api";

function Card({ title, children }) {
  return (
    <div className="card" style={{ padding: 16 }}>
      <div style={{ fontWeight: 800, marginBottom: 8 }}>{title}</div>
      {children}
    </div>
  );
}

export default function Dashboard() {
  const [index, setIndex] = useState(null);
  const [err, setErr] = useState("");
  useEffect(() => {
    api.evidenceIndex().then(setIndex).catch(e => setErr(String(e)));
  }, []);

  return (
    <div className="container">
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "baseline" }}>
        <div>
          <div style={{ fontSize: 20, fontWeight: 900 }}>Governance Dashboard</div>
          <div className="muted">A–E cards will be wired to Day-3 evidence.</div>
        </div>
        <div className="badge">Evidence files: {index?.count ?? "…"}</div>
      </div>

      {err ? (
        <div className="card" style={{ padding: 16, marginTop: 12, borderColor: "#fca5a5" }}>
          <div style={{ fontWeight: 800 }}>Backend not reachable</div>
          <div className="muted" style={{ marginTop: 6 }}>{err}</div>
          <div className="muted" style={{ marginTop: 6 }}>Expected: backend on :8010, Vite proxy /api enabled.</div>
        </div>
      ) : null}

      <div className="grid grid-3" style={{ marginTop: 12 }}>
        <Card title="A — Counts"><div className="muted">Pending wiring</div></Card>
        <Card title="B — Distributions"><div className="muted">Pending wiring</div></Card>
        <Card title="C — Quality"><div className="muted">Pending wiring</div></Card>
        <Card title="D — Window Snapshot"><div className="muted">Pending wiring</div></Card>
        <Card title="E — Security"><div className="muted">See Security page</div></Card>
      </div>
    </div>
  );
}
