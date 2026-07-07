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
      <div className="mc-kpi-value" style={{ marginBottom: "0.5rem" }}>
        {score.toFixed(2)}
      </div>
      <div className="mc-pol-bar-wrap">
        <div className="mc-pol-bar" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
          <div
            className={`mc-pol-bar-fill${accepted ? "" : " mc-pol-bar-fill-warn"}`}
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>
      <div className="mc-muted" style={{ marginTop: "0.75rem", fontSize: "0.95rem" }}>
        <div>Compression: {((pol?.delta_compression ?? 0) * 100).toFixed(0)}%</div>
        <div>Validation: {((pol?.validation_rate ?? 0) * 100).toFixed(0)}%</div>
        <div>Retrieval: {((pol?.retrieval_accuracy ?? 0) * 100).toFixed(0)}%</div>
        <div style={{ marginTop: 6, color: accepted ? "var(--critic)" : "var(--danger)" }}>
          {accepted ? "Bloc accepté ✓" : "Sous le seuil"}
        </div>
      </div>
    </div>
  );
}
