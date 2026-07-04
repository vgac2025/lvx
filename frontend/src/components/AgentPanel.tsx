import type { AgentMessage } from "../types";

interface Props {
  messages: AgentMessage[];
}

export function AgentPanel({ messages }: Props) {
  return (
    <div className="panel" style={{ maxHeight: 420, overflowY: "auto" }}>
      <h2>Dual Agents</h2>
      {messages.length === 0 && (
        <p style={{ color: "var(--muted)", fontSize: "0.9rem" }}>
          Explorer &amp; Critic will comment during encoding…
        </p>
      )}
      <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
        {messages.map((msg) => (
          <li
            key={msg.id}
            style={{
              marginBottom: "0.75rem",
              padding: "0.5rem 0.65rem",
              borderRadius: 8,
              borderLeft: `3px solid ${msg.agent === "explorer" ? "var(--explorer)" : "var(--critic)"}`,
              background: "#0f172a",
            }}
          >
            <strong style={{ color: msg.agent === "explorer" ? "var(--explorer)" : "var(--critic)" }}>
              {msg.agent === "explorer" ? "Explorer" : "Critic"}
            </strong>
            <div style={{ fontSize: "0.85rem", marginTop: 4 }}>{msg.text}</div>
          </li>
        ))}
      </ul>
    </div>
  );
}
