import type { PolMetrics } from "../types";

interface Props {
  pol: PolMetrics | null;
}

export function PolGauge({ pol }: Props) {
  const score = pol?.pol_score ?? 0;
  const pct = Math.round(score * 100);
  const accepted = pol?.block_accepted ?? false;

  return (
    <div className="panel">
      <h2>Proof-of-Learning</h2>
      <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
        <svg width="100" height="100" viewBox="0 0 100 100" aria-label={`PoL score ${pct}%`}>
          <circle cx="50" cy="50" r="42" fill="none" stroke="#1e293b" strokeWidth="10" />
          <circle
            cx="50"
            cy="50"
            r="42"
            fill="none"
            stroke={accepted ? "#22c55e" : "#f59e0b"}
            strokeWidth="10"
            strokeDasharray={`${pct * 2.64} 264`}
            transform="rotate(-90 50 50)"
          />
          <text x="50" y="54" textAnchor="middle" fill="#e8eef7" fontSize="16" fontWeight="bold">
            {score.toFixed(2)}
          </text>
        </svg>
        <div style={{ fontSize: "0.85rem", color: "var(--muted)" }}>
          <div>Compression: {((pol?.delta_compression ?? 0) * 100).toFixed(0)}%</div>
          <div>Validation: {((pol?.validation_rate ?? 0) * 100).toFixed(0)}%</div>
          <div>Retrieval: {((pol?.retrieval_accuracy ?? 0) * 100).toFixed(0)}%</div>
          <div style={{ marginTop: 6, color: accepted ? "var(--critic)" : "var(--danger)" }}>
            {accepted ? "Block accepted ✓" : "Below threshold"}
          </div>
        </div>
      </div>
    </div>
  );
}
