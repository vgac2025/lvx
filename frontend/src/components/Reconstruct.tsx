interface Props {
  original: string;
  reconstructed: string;
  similarity: number;
  reversible: boolean;
  visible: boolean;
}

export function Reconstruct({ original, reconstructed, similarity, reversible, visible }: Props) {
  if (!visible) return null;

  return (
    <div className="panel">
      <h2>Reconstruction</h2>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
        <div>
          <div className="mc-muted" style={{ marginBottom: 4 }}>Original</div>
          <pre className="mc-pre">{original}</pre>
        </div>
        <div>
          <div className="mc-muted" style={{ marginBottom: 4 }}>
            Reconstruit {reversible ? "OK 100%" : `(${Math.round(similarity * 100)}%)`}
          </div>
          <pre className={`mc-pre${reversible ? " mc-pre-ok" : ""}`}>{reconstructed}</pre>
        </div>
      </div>
    </div>
  );
}
