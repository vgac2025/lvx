import { useEffect, useState } from "react";

interface SystemMetrics {
  cpu: {
    percent: number;
    count: number;
    freq_mhz: number;
  };
  memory: {
    total_gb: number;
    used_gb: number;
    available_gb: number;
    percent: number;
  };
  disk: {
    total_gb: number;
    used_gb: number;
    free_gb: number;
    percent: number;
  };
  network: {
    bytes_sent_mb: number;
    bytes_recv_mb: number;
    packets_sent: number;
    packets_recv: number;
  };
  system: {
    platform: string;
    platform_release: string;
    hostname: string;
    processor: string;
  };
}

export function SystemMetrics() {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await fetch("/api/v1/metrics");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        setMetrics(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Erreur inconnue");
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 2000); // Mise à jour toutes les 2s
    return () => clearInterval(interval);
  }, []);

  if (error) {
    return (
      <div style={{ padding: "1rem", background: "#fee", borderRadius: "8px" }}>
        <strong>Erreur métriques système :</strong> {error}
      </div>
    );
  }

  if (!metrics) {
    return <div style={{ padding: "1rem" }}>Chargement métriques...</div>;
  }

  const getColor = (percent: number) => {
    if (percent < 50) return "#4ade80";
    if (percent < 75) return "#fbbf24";
    return "#f87171";
  };

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
        gap: "1rem",
        padding: "1rem",
        background: "#1e293b",
        borderRadius: "8px",
        color: "#e2e8f0",
      }}
    >
      {/* CPU */}
      <div style={{ background: "#334155", padding: "0.75rem", borderRadius: "6px" }}>
        <div style={{ fontSize: "0.875rem", color: "#94a3b8", marginBottom: "0.5rem" }}>
          CPU ({metrics.cpu.count} cores)
        </div>
        <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: getColor(metrics.cpu.percent) }}>
          {metrics.cpu.percent.toFixed(1)}%
        </div>
        <div style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "0.25rem" }}>
          {metrics.cpu.freq_mhz.toFixed(0)} MHz
        </div>
      </div>

      {/* RAM */}
      <div style={{ background: "#334155", padding: "0.75rem", borderRadius: "6px" }}>
        <div style={{ fontSize: "0.875rem", color: "#94a3b8", marginBottom: "0.5rem" }}>
          RAM
        </div>
        <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: getColor(metrics.memory.percent) }}>
          {metrics.memory.percent.toFixed(1)}%
        </div>
        <div style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "0.25rem" }}>
          {metrics.memory.used_gb.toFixed(1)} / {metrics.memory.total_gb.toFixed(1)} GB
        </div>
      </div>

      {/* Disk */}
      <div style={{ background: "#334155", padding: "0.75rem", borderRadius: "6px" }}>
        <div style={{ fontSize: "0.875rem", color: "#94a3b8", marginBottom: "0.5rem" }}>
          Disque
        </div>
        <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: getColor(metrics.disk.percent) }}>
          {metrics.disk.percent.toFixed(1)}%
        </div>
        <div style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "0.25rem" }}>
          {metrics.disk.free_gb.toFixed(1)} GB libre
        </div>
      </div>

      {/* Network */}
      <div style={{ background: "#334155", padding: "0.75rem", borderRadius: "6px" }}>
        <div style={{ fontSize: "0.875rem", color: "#94a3b8", marginBottom: "0.5rem" }}>
          Réseau
        </div>
        <div style={{ fontSize: "1.125rem", fontWeight: "bold", color: "#60a5fa" }}>
          ↑ {metrics.network.bytes_sent_mb.toFixed(1)} MB
        </div>
        <div style={{ fontSize: "1.125rem", fontWeight: "bold", color: "#34d399", marginTop: "0.25rem" }}>
          ↓ {metrics.network.bytes_recv_mb.toFixed(1)} MB
        </div>
      </div>

      {/* System Info */}
      <div
        style={{
          background: "#334155",
          padding: "0.75rem",
          borderRadius: "6px",
          gridColumn: "span 2",
        }}
      >
        <div style={{ fontSize: "0.875rem", color: "#94a3b8", marginBottom: "0.5rem" }}>
          Système
        </div>
        <div style={{ fontSize: "0.875rem", color: "#cbd5e1" }}>
          <div><strong>{metrics.system.hostname}</strong></div>
          <div>{metrics.system.platform} {metrics.system.platform_release}</div>
          <div style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "0.25rem" }}>
            {metrics.system.processor}
          </div>
        </div>
      </div>
    </div>
  );
}

