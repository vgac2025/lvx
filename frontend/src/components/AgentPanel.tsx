import type { AgentMessage } from "../types";

interface Props {
  messages: AgentMessage[];
}

export function AgentPanel({ messages }: Props) {
  return (
    <div className="panel" style={{ maxHeight: 360, overflowY: "auto" }}>
      <h2>Agents duels</h2>
      {messages.length === 0 && (
        <p className="mc-muted">Explorer &amp; Critic commentent pendant l&apos;encodage…</p>
      )}
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`mc-agent-msg ${msg.agent === "explorer" ? "mc-agent-explorer" : "mc-agent-critic"}`}
        >
          <strong style={{ color: msg.agent === "explorer" ? "var(--explorer)" : "var(--critic)" }}>
            {msg.agent === "explorer" ? "Explorer" : "Critic"}
          </strong>
          <div style={{ fontSize: "0.95rem", marginTop: 4 }}>{msg.text}</div>
        </div>
      ))}
    </div>
  );
}
