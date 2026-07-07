import { SystemMetrics } from "../components/SystemMetrics";

export function SystemPage() {
  return (
    <div className="mc-page">
      <h1 className="dashboard-title">Système · F3 Debug</h1>
      <div className="mc-f3">
        <p className="mc-f3-title">[ F3 ] ARTCB DEBUG SCREEN</p>
        <SystemMetrics />
      </div>
    </div>
  );
}
