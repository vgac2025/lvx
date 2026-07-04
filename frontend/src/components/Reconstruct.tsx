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
    <div className="panel" style={{ marginTop: "1rem" }}>
      <h2>Reconstruction</h2>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
        <div>
          <div style={{ color: "var(--muted)", fontSize: "0.8rem", marginBottom: 4 }}>Original</div>
          <pre
            style={{
              whiteSpace: "pre-wrap",
              fontSize: "0.8rem",
              background: "#0f172a",
              padding: "0.75rem",
              borderRadius: 8,
              maxHeight: 200,
              overflow: "auto",
            }}
          >
            {original}
          </pre>
        </div>
        <div>
          <div style={{ color: "var(--muted)", fontSize: "0.8rem", marginBottom: 4 }}>
            Rebuilt {reversible ? "✓ 100%" : `(${Math.round(similarity * 100)}%)`}
          </div>
          <pre
            style={{
              whiteSpace: "pre-wrap",
              fontSize: "0.8rem",
              background: reversible ? "#052e16" : "#0f172a",
              padding: "0.75rem",
              borderRadius: 8,
              maxHeight: 200,
              overflow: "auto",
              border: reversible ? "1px solid #166534" : undefined,
            }}
          >
            {reconstructed}
          </pre>
        </div>
      </div>
    </div>
  );
}
