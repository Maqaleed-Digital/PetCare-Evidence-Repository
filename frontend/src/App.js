import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Evidence from "./pages/Evidence";
import EvidencePack from "./pages/EvidencePack";
import Governance from "./pages/Governance";
import Audit from "./pages/Audit";
import Explainability from "./pages/Explainability";
import Security from "./pages/Security";
import Report from "./pages/Report";
import { Toaster } from "sonner";

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
            <Route path="evidence/:packId" element={<EvidencePack />} />
            <Route path="governance" element={<Governance />} />
            <Route path="audit" element={<Audit />} />
            <Route path="explainability" element={<Explainability />} />
            <Route path="security" element={<Security />} />
            <Route path="report" element={<Report />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
