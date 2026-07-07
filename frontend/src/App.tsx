import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { DashboardProvider } from "./context/DashboardContext";
import { DashboardLayout } from "./layout/DashboardLayout";
import { ChainPage } from "./pages/ChainPage";
import { Console } from "./pages/Console";
import { GraphPage } from "./pages/GraphPage";
import { Groups } from "./pages/Groups";
import { Home } from "./pages/Home";
import { Logs } from "./pages/Logs";
import { Memorize } from "./pages/Memorize";
import { Mining } from "./pages/Mining";
import { SystemPage } from "./pages/SystemPage";
import { Wallets } from "./pages/Wallets";

export default function App() {
  return (
    <DashboardProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<DashboardLayout />}>
            <Route index element={<Home />} />
            <Route path="memorize" element={<Memorize />} />
            <Route path="graph" element={<GraphPage />} />
            <Route path="chain" element={<ChainPage />} />
            <Route path="wallets" element={<Wallets />} />
            <Route path="mining" element={<Mining />} />
            <Route path="system" element={<SystemPage />} />
            <Route path="logs" element={<Logs />} />
            <Route path="console" element={<Console />} />
            <Route path="groups" element={<Groups />} />
            <Route path="demo" element={<Navigate to="/memorize" replace />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </DashboardProvider>
  );
}
