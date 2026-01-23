import { NavLink, Outlet } from "react-router-dom";

const nav = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/evidence", label: "Evidence" },
  { to: "/security", label: "Security" },
];

export default function Layout() {
  return (
    <div className="shell">
      <aside className="sidebar">
        <div style={{ padding: "6px 10px", marginBottom: 10 }}>
          <div style={{ fontWeight: 800 }}>PetCare</div>
          <div className="muted" style={{ fontSize: 12 }}>UI-0 (Standalone)</div>
          <div style={{ marginTop: 8 }}>
            <span className="badge">Read-only</span>{" "}
            <span className="badge">Evidence-backed</span>
          </div>
        </div>

        <div className="grid" style={{ gap: 8 }}>
          {nav.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              className={({ isActive }) => `navitem ${isActive ? "active" : ""}`}
            >
              {n.label}
            </NavLink>
          ))}
        </div>

        <div className="muted" style={{ marginTop: 14, fontSize: 12 }}>
          Evidence baseline: <span className="badge">sprint-6-day-3-closed</span>
        </div>
      </aside>

      <main className="main">
        <Outlet />
      </main>
    </div>
  );
}
