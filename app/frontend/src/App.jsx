import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Evidence from "./pages/Evidence";
import Security from "./pages/Security";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/evidence" element={<Evidence />} />
          <Route path="/security" element={<Security />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
