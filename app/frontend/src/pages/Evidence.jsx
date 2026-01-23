import { useEffect, useMemo, useState } from "react";
import { api } from "../lib/api";

export default function Evidence() {
  const [index, setIndex] = useState(null);
  const [q, setQ] = useState("");
  const [err, setErr] = useState("");
  useEffect(() => {
    api.evidenceIndex().then(setIndex).catch(e => setErr(String(e)));
  }, []);

  const items = useMemo(() => {
    const all = index?.items ?? [];
    const s = q.trim().toLowerCase();
    if (!s) return all;
    return all.filter(it => (it.path || "").toLowerCase().includes(s) || (it.kind || "").toLowerCase().includes(s));
  }, [index, q]);

  return (
    <div className="container">
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "baseline" }}>
        <div>
          <div style={{ fontSize: 20, fontWeight: 900 }}>Evidence Browser</div>
          <div className="muted">Listing from bundle index (repo-backed).</div>
        </div>
        <div className="badge">{items.length} / {index?.count ?? "…"} files</div>
      </div>

      {err ? (
        <div className="card" style={{ padding: 16, marginTop: 12, borderColor: "#fca5a5" }}>
          <div style={{ fontWeight: 800 }}>Error</div>
          <div className="muted" style={{ marginTop: 6 }}>{err}</div>
        </div>
      ) : null}

      <div className="card" style={{ padding: 12, marginTop: 12 }}>
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search by path or kind…"
          style={{ width: "100%", padding: 10, borderRadius: 10, border: "1px solid #e5e7eb" }}
        />
      </div>

      <div className="card" style={{ marginTop: 12, overflow: "hidden" }}>
        <table className="table">
          <thead>
            <tr>
              <th>Path</th>
              <th>Kind</th>
              <th>Bytes</th>
              <th>SHA256</th>
            </tr>
          </thead>
          <tbody>
            {items.map((it) => (
              <tr key={it.path}>
                <td style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace", fontSize: 12 }}>
                  {it.path}
                </td>
                <td><span className="badge">{it.kind}</span></td>
                <td className="muted">{it.bytes}</td>
                <td style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace", fontSize: 12 }}>
                  {String(it.sha256).slice(0, 16)}…
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="muted" style={{ marginTop: 10, fontSize: 12 }}>
        Next: add file preview + checksum verification (UI0-G4).
      </div>
    </div>
  );
}
