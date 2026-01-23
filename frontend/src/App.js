import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Evidence from "./pages/Evidence";
import Security from "./pages/Security";
import Report from "./pages/Report";
import SprintClosurePack from "./pages/SprintClosurePack";
import { Toaster } from "sonner";

// Sprint UI-0 Routes
// E1: /evidence - Evidence Browser + Checksum Verification
// E2: /security - Security & RLS View
// E3: /dashboard - Governance Dashboard (A-E Cards)
// E4: /sprint-closure - Notion-ready Sprint UI-0 Pack

function App() {
  return (
    <div className="min-h-screen bg-white">
      <Toaster position="top-right" richColors />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="evidence" element={<Evidence />} />
            <Route path="security" element={<Security />} />
            <Route path="report" element={<Report />} />
            <Route path="sprint-closure" element={<SprintClosurePack />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
