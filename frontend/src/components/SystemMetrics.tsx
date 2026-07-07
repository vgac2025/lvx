import { useEffect, useState } from "react";

interface SystemMetricsData {
  cpu: { percent: number; count: number; freq_mhz: number };
  memory: { total_gb: number; used_gb: number; available_gb: number; percent: number };
  disk: { total_gb: number; used_gb: number; free_gb: number; percent: number };
  network: { bytes_sent_mb: number; bytes_recv_mb: number; packets_sent: number; packets_recv: number };
  system: { platform: string; platform_release: string; hostname: string; processor: string };
}

export function SystemMetrics() {
  const [metrics, setMetrics] = useState<SystemMetricsData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await fetch("/api/v1/metrics");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        setMetrics(await res.json());
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Erreur inconnue");
      }
    };
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 2000);
    return () => clearInterval(interval);
  }, []);

  if (error) {
    return <p className="mc-error">Erreur métriques : {error}</p>;
  }

  if (!metrics) {
    return <p>Chargement métriques…</p>;
  }

  const bar = (pct: number) => (
    <div className="mc-hp-bar">
      <div
        className="mc-hp-fill"
        style={{
          width: `${pct}%`,
          background: pct < 50 ? "var(--mc-grass)" : pct < 75 ? "var(--mc-gold)" : "var(--mc-redstone)",
        }}
      />
    </div>
  );

  return (
    <div className="mc-f3-grid">
      <div>
        <div>CPU ({metrics.cpu.count} cores) — {metrics.cpu.percent.toFixed(1)}%</div>
        {bar(metrics.cpu.percent)}
        <div className="mc-muted">{metrics.cpu.freq_mhz.toFixed(0)} MHz</div>
      </div>
      <div>
        <div>RAM — {metrics.memory.percent.toFixed(1)}%</div>
        {bar(metrics.memory.percent)}
        <div className="mc-muted">
          {metrics.memory.used_gb.toFixed(1)} / {metrics.memory.total_gb.toFixed(1)} GB
        </div>
      </div>
      <div>
        <div>Disque — {metrics.disk.percent.toFixed(1)}%</div>
        {bar(metrics.disk.percent)}
        <div className="mc-muted">{metrics.disk.free_gb.toFixed(1)} GB libre</div>
      </div>
      <div>
        <div>Réseau ↑ {metrics.network.bytes_sent_mb.toFixed(1)} MB</div>
        <div>↓ {metrics.network.bytes_recv_mb.toFixed(1)} MB</div>
      </div>
      <div>
        <div>
          <strong>{metrics.system.hostname}</strong>
        </div>
        <div>
          {metrics.system.platform} {metrics.system.platform_release}
        </div>
        <div className="mc-muted">{metrics.system.processor}</div>
      </div>
    </div>
  );
}
